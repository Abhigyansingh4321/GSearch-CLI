import json
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from src.engine import SearchResult
from src.main import main


class TestMainCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch("src.main.SearchEngine")
    def test_json_output_returns_machine_readable_payload(self, mock_engine_cls):
        mock_engine = mock_engine_cls.return_value
        mock_engine.perform_search.return_value = [
            SearchResult(
                title="Python Docs",
                url="https://docs.python.org/3/",
                description="Official documentation.",
                source="DuckDuckGo",
            )
        ]

        result = self.runner.invoke(
            main,
            [
                "python click",
                "--json-output",
                "--engine",
                "duckduckgo",
                "--site",
                "docs.python.org",
            ],
        )

        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["title"], "Python Docs")
        mock_engine.perform_search.assert_called_once_with(
            "python click",
            num_results=10,
            provider="duckduckgo",
            site="docs.python.org",
        )

    @patch("src.main.webbrowser.open")
    @patch("src.main.SearchEngine")
    def test_lucky_opens_first_result(self, mock_engine_cls, mock_webbrowser_open):
        mock_engine = mock_engine_cls.return_value
        mock_engine.perform_search.return_value = [
            SearchResult(
                title="Python",
                url="https://www.python.org",
                description="Homepage",
                source="DuckDuckGo",
            )
        ]

        result = self.runner.invoke(main, ["python", "--lucky", "--no-prompt"])

        self.assertEqual(result.exit_code, 0, result.output)
        mock_webbrowser_open.assert_called_once_with("https://www.python.org", new=2)


if __name__ == "__main__":
    unittest.main()
