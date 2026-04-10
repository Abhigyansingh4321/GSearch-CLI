"""
Search engine integrations for G-Search CLI.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Literal
from urllib.parse import urlparse

import requests
from ddgs import DDGS

ProviderName = Literal["auto", "duckduckgo", "google"]

GOOGLE_RESULTS_PER_REQUEST = 10
GOOGLE_MAX_RESULTS = 50


class SearchError(RuntimeError):
    """Raised when a search provider cannot satisfy a request."""


@dataclass(slots=True)
class SearchResult:
    """Represents a single search result."""

    title: str
    url: str
    description: str
    source: str = "Unknown"

    def to_dict(self) -> dict[str, str]:
        """Returns a JSON-serialisable representation of the result."""

        return asdict(self)


class SearchEngine:
    """Manages Google and DuckDuckGo search requests."""

    def __init__(
        self,
        google_api_key: str | None = None,
        google_cse_id: str | None = None,
        timeout: int = 10,
    ) -> None:
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = google_cse_id or os.getenv("GOOGLE_CSE_ID")
        self.timeout = timeout

    def perform_search(
        self,
        query: str,
        num_results: int = 10,
        provider: ProviderName = "auto",
        site: str | None = None,
    ) -> list[SearchResult]:
        """Runs a search using the requested provider strategy."""

        normalized_query = self._normalize_query(query, site)
        providers = self._resolve_providers(provider)
        errors: list[str] = []
        empty_result_seen = False

        for provider_name in providers:
            try:
                results = self._search_with_provider(
                    provider_name,
                    normalized_query,
                    num_results,
                )
            except SearchError as exc:
                errors.append(f"{provider_name}: {exc}")
                continue

            if results:
                return results

            empty_result_seen = True

        if empty_result_seen:
            return []

        details = "; ".join(errors) if errors else "No provider was available."
        raise SearchError(f"Search failed. {details}")

    def _search_with_provider(
        self,
        provider: Literal["duckduckgo", "google"],
        query: str,
        num_results: int,
    ) -> list[SearchResult]:
        if provider == "google":
            return self._google_search(query, num_results)
        if provider == "duckduckgo":
            return self._ddg_search(query, num_results)
        raise SearchError(f"Unsupported provider '{provider}'.")

    def _resolve_providers(self, provider: ProviderName) -> list[Literal["duckduckgo", "google"]]:
        if provider == "auto":
            if self.google_api_key and self.google_cse_id:
                return ["google", "duckduckgo"]
            return ["duckduckgo"]

        if provider == "google":
            if not self.google_api_key or not self.google_cse_id:
                raise SearchError(
                    "Google search requires both GOOGLE_API_KEY and GOOGLE_CSE_ID."
                )
            return ["google"]

        if provider == "duckduckgo":
            return ["duckduckgo"]

        raise SearchError(f"Unsupported provider '{provider}'.")

    def _normalize_query(self, query: str, site: str | None) -> str:
        cleaned_query = query.strip()
        if not cleaned_query:
            raise SearchError("Query cannot be empty.")

        if site:
            cleaned_query = f"{cleaned_query} site:{self._normalize_site(site)}"

        return cleaned_query

    def _normalize_site(self, site: str) -> str:
        cleaned_site = site.strip()
        if not cleaned_site:
            raise SearchError("Site filter cannot be empty.")

        parsed = urlparse(cleaned_site if "://" in cleaned_site else f"https://{cleaned_site}")
        normalized_site = parsed.netloc or parsed.path
        normalized_site = normalized_site.strip("/").lower()

        if not normalized_site:
            raise SearchError("Site filter is invalid.")

        return normalized_site

    def _google_search(self, query: str, num_results: int) -> list[SearchResult]:
        """Fetches results using the Google Custom Search API."""

        if not self.google_api_key or not self.google_cse_id:
            raise SearchError(
                "Google search requires both GOOGLE_API_KEY and GOOGLE_CSE_ID."
            )

        requested_results = max(1, min(num_results, GOOGLE_MAX_RESULTS))
        collected_results: list[SearchResult] = []
        start_index = 1

        while len(collected_results) < requested_results:
            batch_size = min(
                GOOGLE_RESULTS_PER_REQUEST,
                requested_results - len(collected_results),
            )
            params = {
                "q": query,
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "num": batch_size,
                "safe": "off",
                "start": start_index,
            }

            try:
                response = requests.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                raise SearchError(f"Google request failed: {exc}") from exc

            items = response.json().get("items", [])
            if not items:
                break

            for item in items:
                collected_results.append(
                    SearchResult(
                        title=item.get("title") or "No title",
                        url=item.get("link") or "",
                        description=item.get("snippet") or "No description available.",
                        source="Google",
                    )
                )

            if len(items) < batch_size:
                break

            start_index += len(items)

        return collected_results

    def _ddg_search(self, query: str, num_results: int) -> list[SearchResult]:
        """Fetches results using DuckDuckGo."""

        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        max_results=max(1, num_results),
                        safesearch="off",
                    )
                )
        except Exception as exc:
            raise SearchError(f"DuckDuckGo request failed: {exc}") from exc

        search_results: list[SearchResult] = []
        for result in results:
            search_results.append(
                SearchResult(
                    title=result.get("title") or "No title",
                    url=result.get("href") or "",
                    description=result.get("body") or "No description available.",
                    source="DuckDuckGo",
                )
            )

        return search_results
