"""
Test suite for the local-go redirector service.

This test suite verifies the functionality of the redirector service, including:
- URL redirection
- Configuration management
- File operations
- Error handling
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator, Tuple
from unittest.mock import patch, mock_open, MagicMock
import json
import unittest

from main import app, redirect_map, CONFIG_FILE, load_config

@dataclass
class TestConfig:
    """Configuration for test cases"""
    shortcut: str
    url: str
    expected_status: int
    expected_data: Any = None

class TestRedirector(unittest.TestCase):
    """Test suite for the redirector service"""

    def setUp(self) -> None:
        """
        Set up test environment before each test.
        - Creates a test client
        - Clears the redirect map
        - Sets up a temporary config file
        """
        self.app = app.test_client()
        self._clear_redirect_map()
        self._setup_test_config()

    def tearDown(self) -> None:
        """
        Clean up after each test.
        - Removes the temporary config file
        """
        self._cleanup_test_config()

    def _clear_redirect_map(self) -> None:
        """Clear the redirect map for a fresh test state"""
        redirect_map.clear()

    def _setup_test_config(self) -> None:
        """Set up a temporary config file for testing"""
        self.test_config = Path("test_config")
        if self.test_config.exists():
            self.test_config.unlink()

    def _cleanup_test_config(self) -> None:
        """Remove the temporary config file"""
        if self.test_config.exists():
            self.test_config.unlink()

    def _mock_file_operations(self, read_data: str = '', exists: bool = True) -> Generator[Tuple[Any, Any], None, None]:
        """
        Helper method to mock file operations
        Args:
            read_data: Data to return when file is read
            exists: Whether the file should exist
        Yields:
            Tuple of mock file and mock exists patches
        """
        mock_file = mock_open(read_data=read_data)
        yield patch('pathlib.Path.open', mock_file), patch('pathlib.Path.exists', return_value=exists)

    def _add_test_redirect(self, shortcut: str, url: str) -> None:
        """Helper method to add a test redirect"""
        redirect_map[shortcut] = url

    def _assert_redirect_response(self, config: TestConfig) -> None:
        """
        Assert redirect response matches expected values
        Args:
            config: Test configuration containing expected values
        """
        response = self.app.get(f'/go/{config.shortcut}')
        self.assertEqual(response.status_code, config.expected_status)
        if config.expected_data:
            self.assertEqual(response.location, config.expected_data)

    def test_redirect_not_found(self) -> None:
        """
        Test that requesting a non-existent redirect returns a 404 error.
        Verifies the error handling functionality.
        """
        config = TestConfig(
            shortcut='nonexistent',
            url='',
            expected_status=404
        )
        self._assert_redirect_response(config)

    def test_redirect_success(self) -> None:
        """
        Test successful URL redirection.
        - Adds a test redirect
        - Verifies the redirect response
        - Checks the redirect location
        """
        config = TestConfig(
            shortcut='test',
            url='example.com',
            expected_status=302,
            expected_data='https://example.com'
        )
        self._add_test_redirect(config.shortcut, config.url)
        self._assert_redirect_response(config)

    def test_show_config_empty(self) -> None:
        """
        Test viewing an empty configuration.
        - Verifies the config view endpoint
        - Checks that empty config returns empty JSON
        """
        response = self.app.get('/go/👀')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {})

    def test_show_config_with_data(self) -> None:
        """
        Test viewing configuration with data.
        - Adds a test redirect
        - Verifies the config view shows the correct data
        """
        self._add_test_redirect('test', 'example.com')
        response = self.app.get('/go/👀')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'test': 'example.com'})

    def test_save_missing_parameters(self) -> None:
        """
        Test saving redirects with missing parameters.
        - Tests missing 'p' parameter
        - Tests missing 'u' parameter
        - Tests missing both parameters
        Verifies proper error handling (400 Bad Request)
        """
        test_cases = [
            TestConfig('', '', 400),
            TestConfig('test', '', 400),
            TestConfig('', 'example.com', 400)
        ]
        
        for config in test_cases:
            with self.subTest(config=config):
                params = f"?p={config.shortcut}&u={config.url}" if config.shortcut or config.url else ""
                response = self.app.get(f'/save{params}')
                self.assertEqual(response.status_code, config.expected_status)

    def test_save_success(self) -> None:
        """
        Test successful save of a new redirect.
        - Mocks file operations
        - Saves a new redirect
        - Verifies the redirect is stored
        - Checks file write operation
        """
        config = TestConfig('test', 'example.com', 200)
        mock_file = mock_open()
        with patch('pathlib.Path.open', mock_file):
            response = self.app.get(f'/save?p={config.shortcut}&u={config.url}')
            self.assertEqual(response.status_code, config.expected_status)
            self.assertEqual(response.data.decode(), '👍')
            self.assertEqual(redirect_map[config.shortcut], config.url)
            mock_file.assert_called_once()
            mock_file().write.assert_called_once_with(f'{config.shortcut}:{config.url}\n')

    def test_load_config_empty(self) -> None:
        """
        Test loading an empty config file.
        - Mocks an empty file
        - Verifies no redirects are loaded
        """
        with next(self._mock_file_operations(read_data='', exists=True))[0]:
            self._clear_redirect_map()
            load_config()
            self.assertEqual(len(redirect_map), 0)

    def test_load_config_with_data(self) -> None:
        """
        Test loading a config file with valid data.
        - Mocks a file with two valid redirects
        - Verifies both redirects are loaded correctly
        """
        test_data = 'test1:example1.com\ntest2:example2.com\n'
        with next(self._mock_file_operations(read_data=test_data, exists=True))[0]:
            self._clear_redirect_map()
            load_config()
            self.assertEqual(len(redirect_map), 2)
            self.assertEqual(redirect_map['test1'], 'example1.com')
            self.assertEqual(redirect_map['test2'], 'example2.com')

    def test_load_config_malformed(self) -> None:
        """
        Test loading a config file with malformed data.
        - Mocks a file with one malformed line
        - Verifies valid lines are loaded
        - Verifies malformed line is skipped
        """
        test_data = 'test1:example1.com\nmalformed\ntest2:example2.com\n'
        with next(self._mock_file_operations(read_data=test_data, exists=True))[0]:
            self._clear_redirect_map()
            load_config()
            self.assertEqual(len(redirect_map), 2)
            self.assertEqual(redirect_map['test1'], 'example1.com')
            self.assertEqual(redirect_map['test2'], 'example2.com')

    def test_config_file_creation(self) -> None:
        """
        Test config file creation when it doesn't exist.
        - Mocks file existence check
        - Verifies file creation is attempted
        - Checks method calls
        """
        mock_exists = MagicMock(return_value=False)
        mock_touch = MagicMock()
        with patch('pathlib.Path.exists', mock_exists):
            with patch('pathlib.Path.touch', mock_touch):
                self._clear_redirect_map()
                load_config()
                self.assertEqual(len(redirect_map), 0)
                mock_exists.assert_called_once()
                mock_touch.assert_called_once()

if __name__ == '__main__':
    unittest.main() 