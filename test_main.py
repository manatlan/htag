import sys,subprocess
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock

from htag.__main__ import command, BooleanOptionalAction

def test_main_help():
    cmds=[sys.executable,"-m","htag","-h"]
    stdout = subprocess.run(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
    assert "--gui" in stdout
    assert "--no-gui" in stdout

@pytest.fixture
def mock_args_jules():
    with patch('argparse.ArgumentParser.parse_args') as mock_parse_args:
        yield mock_parse_args

def test_boolean_optional_action_jules():
    # This is a helper class, so a simple test should be enough
    parser = MagicMock()
    namespace = MagicMock()
    action = BooleanOptionalAction(option_strings=['--gui'], dest='gui')

    action(parser, namespace, values=None, option_string='--gui')
    assert namespace.gui is True

    action(parser, namespace, values=None, option_string='--no-gui')
    assert namespace.gui is False

def test_command_create_mode_new_file_jules(mock_args_jules, capsys):
    mock_args_jules.return_value = MagicMock(file=None)
    with patch('os.path.isfile', return_value=False):
        with patch('builtins.open', mock_open()) as mocked_file:
            command()
            mocked_file.assert_called_once_with('main.py', 'w+')
            captured = capsys.readouterr()
            assert "HTag App file created" in captured.out

def test_command_create_mode_file_exists_jules(mock_args_jules, capsys):
    mock_args_jules.return_value = MagicMock(file=None)
    with patch('os.path.isfile', return_value=True):
        command()
        captured = capsys.readouterr()
        assert "already got a 'main.py' file" in captured.out

def test_command_run_mode_file_not_found_jules(mock_args_jules, capsys):
    mock_args_jules.return_value = MagicMock(file='non_existent.py')
    with patch('os.path.isfile', return_value=False):
        command()
        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "not found" in captured.out

@patch('htag.runners.Runner')
def test_command_run_mode_with_app_class_jules(mock_runner, mock_args_jules, capsys):
    mock_args_jules.return_value = MagicMock(file='app_with_class.py', dev=True, gui=True, host='127.0.0.1', port='8000')

    # Mock the module and its 'App' class
    mock_module = MagicMock()
    mock_module.App = MagicMock()
    delattr(mock_module, 'app') # ensure app attribute is not present

    with patch('os.path.isfile', return_value=True):
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec', return_value=mock_module):
                with patch('sys.modules', {}):
                    command()
                    mock_runner.assert_called_once_with(
                        mock_module.App,
                        reload=True,
                        debug=True,
                        host='127.0.0.1',
                        port='8000',
                        interface=1
                    )
                    captured = capsys.readouterr()
                    assert "Found 'App' (tag class), will run it" in captured.out

@patch('htag.runners.Runner', new_callable=lambda: type('MockRunner', (MagicMock,), {}))
def test_command_run_mode_with_app_instance_jules(mock_runner_class, mock_args_jules, capsys):
    mock_args_jules.return_value = MagicMock(file='app_with_instance.py')

    # Mock the module and its 'app' instance
    mock_module = MagicMock()
    mock_runner_instance = mock_runner_class()
    mock_module.app = mock_runner_instance
    delattr(mock_module, 'App') # ensure App attribute is not present

    with patch('os.path.isfile', return_value=True):
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec', return_value=mock_module):
                with patch('sys.modules', {}):
                    with patch('sys.exit') as mock_exit:
                        command()
                        mock_runner_instance.run.assert_called_once()
                        captured = capsys.readouterr()
                        assert "Found 'app' (new Runner), will run it" in captured.out
                        mock_exit.assert_called_once_with(0)

def test_command_run_mode_no_app_jules(mock_args_jules, capsys):
    mock_args_jules.return_value = MagicMock(file='empty.py')

    mock_module = MagicMock()
    delattr(mock_module, 'App')
    delattr(mock_module, 'app')

    with patch('os.path.isfile', return_value=True):
        with patch('importlib.util.spec_from_file_location'):
            with patch('importlib.util.module_from_spec', return_value=mock_module):
                with patch('sys.modules', {}):
                    command()
                    captured = capsys.readouterr()
                    assert "doesn't contain 'App' (tag class)" in captured.out

def test_command_run_mode_with_exception_jules(mock_args_jules, capsys):
    mock_args_jules.return_value = MagicMock(file='buggy.py')
    with patch('os.path.isfile', return_value=True):
        with patch('importlib.util.spec_from_file_location', side_effect=Exception("Test Exception")):
            command()
            captured = capsys.readouterr()
            assert "ERROR" in captured.out
            assert "Test Exception" in captured.out