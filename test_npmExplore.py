import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from npmExplore import (
    get_settings, fetch_website_content, parse_html, get_weekly_downloads,
    get_maintainers, get_current_source_package, get_dependents, consolidate_packages,
    save_data, load_data, Settings, Author, Package
)

class TestNpmExplore(unittest.TestCase):

    @patch('npmExplore.requests.get')
    def test_fetch_website_content(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'test content'
        mock_get.return_value = mock_response
        content = fetch_website_content('http://test-url.com')
        self.assertEqual(content, 'test content')

    def test_parse_html(self):
        html_content = '<html><head><title>Test</title></head><body></body></html>'
        soup = parse_html(html_content)
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.title.string, 'Test')

    # @patch('npmExplore.requests.get')
    # def test_get_weekly_downloads(self, mock_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {'downloads': 1234}
    #     mock_get.return_value = mock_response
    #     downloads = get_weekly_downloads('test-package')
    #     self.assertEqual(downloads, 1234)

    # @patch('npmExplore.requests.get')
    # def test_get_maintainers(self, mock_get):
    #     mock_response = MagicMock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         'maintainers': [{'name': 'test-user', 'email': 'test@example.com'}],
    #         'versions': {}
    #     }
    #     mock_get.return_value = mock_response
    #     maintainers = get_maintainers('test-package')
    #     self.assertEqual(len(maintainers), 1)
    #     self.assertEqual(maintainers[0].username, 'test-user')
    #     self.assertEqual(maintainers[0].email, 'test@example.com')

    def test_get_current_source_package(self):
        html_content = '<html><head><meta property="og:url" content="https://registry.npmjs.org/package/test-package"></head><body></body></html>'
        soup = parse_html(html_content)
        package = get_current_source_package(soup)
        self.assertEqual(package, 'test-package')

    # @patch('npmExplore.fetch_website_content')
    # def test_get_dependents(self, mock_fetch_website_content):
    #     html_content = '<html><body><div id="tabpanel-dependents"><ul><li><a href="/package/dependent1">dependent1</a></li></ul></div></body></html>'
    #     soup = parse_html(html_content)
    #     mock_fetch_website_content.return_value = None
    #     dependents = get_dependents(soup)
    #     self.assertEqual(len(dependents), 1)
    #     self.assertEqual(dependents[0].name, 'dependent1')

    def test_consolidate_packages(self):
        new_packages = [Package(name='package1', url='url1', sourced_from=[], dependents=[], lastCheckedOn='')]
        known_packages = [Package(name='package1', url='url1', sourced_from=[], dependents=['dep1'], lastCheckedOn='')]
        consolidated = consolidate_packages(new_packages, known_packages)
        self.assertEqual(consolidated[0].dependents, ['dep1'])

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('npmExplore.json.dump')
    def test_save_data(self, mock_json_dump, mock_open):
        data = [Package(name='package1', url='url1', sourced_from=[], dependents=[], lastCheckedOn='')]
        save_data(data, 'testfile')
        mock_open.assert_called_once_with('data_testfile.json', 'w')
        mock_json_dump.assert_called_once()

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='[{"name": "package1", "url": "url1", "sourced_from": [], "dependents": [], "lastCheckedOn": ""}]')
    @patch('os.path.exists')
    def test_load_data(self, mock_exists, mock_open):
        mock_exists.return_value = True
        data = load_data('testfile')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'package1')

if __name__ == '__main__':
    unittest.main()