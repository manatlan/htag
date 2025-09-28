import sys
import os
import pytest
import webbrowser
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to allow imports from htag
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from htag.runners.chromeappmode import ChromeApp, FULLSCREEN

@patch('htag.runners.chromeappmode.subprocess.Popen')
class TestChromeApp:

    def test_init_no_chrome_found_jules(self, mock_popen):
        with patch('sys.platform', 'linux'):
            with patch('webbrowser.get', side_effect=webbrowser.Error):
                with pytest.raises(Exception, match="no chrome browser, no app-mode !"):
                    ChromeApp("http://localhost:8000")

    @patch('webbrowser.get')
    def test_init_linux_jules(self, mock_wb_get, mock_popen):
        mock_wb_get.return_value.name = "google-chrome"
        with patch('sys.platform', 'linux'):
            app = ChromeApp("http://localhost:8000")
            assert app._p is not None
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert args[0] == "google-chrome"
            assert "--app=http://localhost:8000" in args

    @patch('htag.runners.chromeappmode.find_chrome_win', return_value='chrome.exe')
    def test_init_windows_jules(self, mock_find_win, mock_popen):
        with patch('sys.platform', 'win32'):
            app = ChromeApp("http://localhost:8000")
            assert app._p is not None
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert args[0] == 'chrome.exe'

    @patch('htag.runners.chromeappmode.find_chrome_mac', return_value='chrome_mac')
    def test_init_mac_jules(self, mock_find_mac, mock_popen):
        with patch('sys.platform', 'darwin'):
            app = ChromeApp("http://localhost:8000")
            assert app._p is not None
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert args[0] == 'chrome_mac'

    @patch('webbrowser.get')
    def test_init_with_size_jules(self, mock_wb_get, mock_popen):
        mock_wb_get.return_value.name = "google-chrome"
        with patch('sys.platform', 'linux'):
            ChromeApp("http://localhost:8000", size=(800, 600))
            args = mock_popen.call_args[0][0]
            assert "--window-size=800,600" in args

    @patch('webbrowser.get')
    def test_init_with_fullscreen_jules(self, mock_wb_get, mock_popen):
        mock_wb_get.return_value.name = "google-chrome"
        with patch('sys.platform', 'linux'):
            ChromeApp("http://localhost:8000", size=FULLSCREEN)
            args = mock_popen.call_args[0][0]
            assert "--start-fullscreen" in args

    @patch('webbrowser.get')
    def test_init_with_lock_port_jules(self, mock_wb_get, mock_popen):
        mock_wb_get.return_value.name = "google-chrome"
        with patch('sys.platform', 'linux'):
            app = ChromeApp("http://localhost:8000", lockPort=9999)
            assert app.cacheFolderToRemove is None
            args = mock_popen.call_args[0][0]
            assert "--remote-debugging-port=9999" in args
            assert any("--disk-cache-dir=" in s for s in args)
            assert any("--user-data-dir=" in s for s in args)

    @patch('webbrowser.get')
    @patch('shutil.rmtree')
    def test_del_jules(self, mock_rmtree, mock_wb_get, mock_popen):
        mock_wb_get.return_value.name = "google-chrome"
        with patch('sys.platform', 'linux'):
            app = ChromeApp("http://localhost:8000")
            cache_folder = app.cacheFolderToRemove
            app.__del__()
            mock_rmtree.assert_called_once_with(cache_folder, ignore_errors=True)
            app._p.kill.assert_called_once()

    @patch('webbrowser.get')
    def test_wait_jules(self, mock_wb_get, mock_popen):
        mock_wb_get.return_value.name = "google-chrome"
        with patch('sys.platform', 'linux'):
            app = ChromeApp("http://localhost:8000")
            app.wait(None)
            app._p.wait.assert_called_once()

    @patch('webbrowser.get')
    def test_exit_jules(self, mock_wb_get, mock_popen):
        mock_wb_get.return_value.name = "google-chrome"
        with patch('sys.platform', 'linux'):
            app = ChromeApp("http://localhost:8000")
            app.exit()
            app._p.kill.assert_called_once()