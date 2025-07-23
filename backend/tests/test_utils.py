import unittest
from unittest.mock import patch, MagicMock
import asyncio

from utils.chartify import create_chart_svg
from utils.csl import format_citations

class TestUtils(unittest.TestCase):

    @patch('utils.chartify.async_playwright')
    def test_create_chart_svg(self, mock_playwright):
        # This is a simplified test that mocks the playwright interaction
        async def run_test():
            mock_browser = MagicMock()
            mock_page = MagicMock()
            mock_element = MagicMock()
            
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.query_selector.return_value = mock_element
            mock_element.inner_html.return_value = "<g>chart content</g>"

            svg = await create_chart_svg("some data")
            self.assertIn("<svg>", svg)
            self.assertIn("chart content", svg)

        asyncio.run(run_test())

    @patch('utils.csl.requests.get')
    def test_format_citations(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = """
        <style xmlns="http://purl.org/net/xbiblio/csl" class="in-text" version="1.0">
          <citation>
            <layout>
              <text value="test citation"/>
            </layout>
          </citation>
          <bibliography>
            <layout>
              <text value="test bibliography"/>
            </layout>
          </bibliography>
        </style>
        """
        mock_get.return_value = mock_response

        sample_csl = [{"id": "1", "type": "article-journal", "title": "Title"}]
        formatted = format_citations(sample_csl, 'apa')
        
        self.assertEqual(len(formatted['in_text_citations']), 1)
        self.assertEqual(formatted['in_text_citations'][0]['in_text'], 'test citation')
        self.assertIn('test bibliography', formatted['bibliography'][0])

if __name__ == '__main__':
    unittest.main()