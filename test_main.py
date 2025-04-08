import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import json
from main import app, redirect_map, CONFIG_FILE

class TestRedirector(unittest.TestCase):
    def setUp(self):
        """Set up test client and clear redirect map before each test"""
        self.app = app.test_client()
        redirect_map.clear()
        # Create a temporary config file for testing
        self.test_config = Path("test_config")
        if self.test_config.exists():
            self.test_config.unlink()

    def tearDown(self):
        """Clean up after each test"""
        if self.test_config.exists():
            self.test_config.unlink()

    def test_redirect_not_found(self):
        """Test redirect to non-existent path returns 404"""
        response = self.app.get('/go/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_redirect_success(self):
        """Test successful redirect"""
        redirect_map['test'] = 'example.com'
        response = self.app.get('/go/test')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://example.com')

    def test_show_config_empty(self):
        """Test showing empty config"""
        response = self.app.get('/go/👀')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {})

    def test_show_config_with_data(self):
        """Test showing config with data"""
        redirect_map['test'] = 'example.com'
        response = self.app.get('/go/👀')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'test': 'example.com'})

    def test_save_missing_parameters(self):
        """Test saving with missing parameters"""
        response = self.app.get('/save')
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/save?p=test')
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/save?u=example.com')
        self.assertEqual(response.status_code, 400)

    def test_save_success(self):
        """Test successful save"""
        with patch('builtins.open', mock_open()) as mock_file:
            response = self.app.get('/save?p=test&u=example.com')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode(), '👍')
            self.assertEqual(redirect_map['test'], 'example.com')
            mock_file.assert_called_once()
            mock_file().write.assert_called_once_with('test:example.com\n')

    def test_load_config_empty(self):
        """Test loading empty config file"""
        with patch('builtins.open', mock_open(read_data='')):
            redirect_map.clear()
            self.assertEqual(len(redirect_map), 0)

    def test_load_config_with_data(self):
        """Test loading config file with data"""
        test_data = 'test1:example1.com\ntest2:example2.com\n'
        with patch('builtins.open', mock_open(read_data=test_data)):
            redirect_map.clear()
            self.assertEqual(len(redirect_map), 2)
            self.assertEqual(redirect_map['test1'], 'example1.com')
            self.assertEqual(redirect_map['test2'], 'example2.com')

    def test_load_config_malformed(self):
        """Test loading config file with malformed data"""
        test_data = 'test1:example1.com\nmalformed\ntest2:example2.com\n'
        with patch('builtins.open', mock_open(read_data=test_data)):
            redirect_map.clear()
            self.assertEqual(len(redirect_map), 2)
            self.assertEqual(redirect_map['test1'], 'example1.com')
            self.assertEqual(redirect_map['test2'], 'example2.com')

    def test_config_file_creation(self):
        """Test config file is created if it doesn't exist"""
        with patch.object(Path, 'exists', return_value=False) as mock_exists:
            with patch.object(Path, 'touch') as mock_touch:
                redirect_map.clear()
                self.assertEqual(len(redirect_map), 0)
                mock_exists.assert_called_once()
                mock_touch.assert_called_once()

if __name__ == '__main__':
    unittest.main() 