import unittest
from unittest.mock import patch

from src.engine import SearchEngine, SearchError, SearchResult


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class TestSearchResult(unittest.TestCase):
    def test_search_result_defaults(self):
        result = SearchResult("Title", "https://example.com", "Description")

        self.assertEqual(result.title, "Title")
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.description, "Description")
        self.assertEqual(result.source, "Unknown")
        self.assertEqual(
            result.to_dict(),
            {
                "title": "Title",
                "url": "https://example.com",
                "description": "Description",
                "source": "Unknown",
            },
        )


class TestSearchEngine(unittest.TestCase):
    def test_google_provider_requires_credentials(self):
        engine = SearchEngine(google_api_key=None, google_cse_id=None)

        with self.assertRaises(SearchError):
            engine.perform_search("python", provider="google")

    def test_normalize_query_appends_site_filter(self):
        engine = SearchEngine()

        normalized = engine._normalize_query(" python testing ", "https://docs.python.org/3/")

        self.assertEqual(normalized, "python testing site:docs.python.org")

    @patch.object(SearchEngine, "_ddg_search")
    @patch.object(SearchEngine, "_google_search")
    def test_auto_falls_back_to_duckduckgo_when_google_fails(
        self,
        mock_google_search,
        mock_ddg_search,
    ):
        engine = SearchEngine(google_api_key="key", google_cse_id="cx")
        mock_google_search.side_effect = SearchError("quota exceeded")
        mock_ddg_search.return_value = [
            SearchResult(
                title="Fallback result",
                url="https://example.com",
                description="DuckDuckGo result",
                source="DuckDuckGo",
            )
        ]

        results = engine.perform_search("python", provider="auto")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, "DuckDuckGo")
        mock_google_search.assert_called_once_with("python", 10)
        mock_ddg_search.assert_called_once_with("python", 10)

    @patch("src.engine.requests.get")
    def test_google_search_paginates_for_more_than_ten_results(self, mock_get):
        engine = SearchEngine(google_api_key="key", google_cse_id="cx")
        mock_get.side_effect = [
            FakeResponse({"items": build_google_items(1, 10)}),
            FakeResponse({"items": build_google_items(11, 5)}),
        ]

        results = engine.perform_search("python", num_results=15, provider="google")

        self.assertEqual(len(results), 15)
        self.assertEqual(results[0].source, "Google")
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(mock_get.call_args_list[0].kwargs["params"]["start"], 1)
        self.assertEqual(mock_get.call_args_list[0].kwargs["params"]["num"], 10)
        self.assertEqual(mock_get.call_args_list[1].kwargs["params"]["start"], 11)
        self.assertEqual(mock_get.call_args_list[1].kwargs["params"]["num"], 5)


def build_google_items(start: int, count: int):
    return [
        {
            "title": f"Result {index}",
            "link": f"https://example.com/{index}",
            "snippet": f"Snippet {index}",
        }
        for index in range(start, start + count)
    ]


if __name__ == "__main__":
    unittest.main()
