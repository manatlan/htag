import pytest
import sys
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
from htag import cli

def test_build_missing_entrypoint(capsys):
    with patch("htag.cli.Path.exists", return_value=False):
        with pytest.raises(SystemExit) as e:
            cli.build("missing_app.py")
        assert e.value.code == 1
    
    captured = capsys.readouterr()
    assert "Error:" in captured.out
    assert "Entrypoint 'missing_app.py' not found" in captured.out

def test_build_success(capsys):
    # We mock Path.resolve() because cli.build does entry_path.resolve()
    mock_entry_path = MagicMock()
    mock_entry_path.exists.return_value = True
    mock_entry_path.stem = "my_app"
    mock_entry_path.__str__.return_value = "my_app.py"

    mock_spec_file = MagicMock()
    mock_spec_file.exists.return_value = True

    # Patch Path to return our mocked entry_path for the script and mocked spec for the spec file
    def mock_path_constructor(path_str):
        if path_str == "my_app.py":
            return mock_entry_path
        elif path_str == "my_app.spec":
            return mock_spec_file
        elif path_str == "docs/assets":
            # Mock assets dir as exists to cover --add-data branch
            m = MagicMock()
            m.exists.return_value = True
            m.__str__.return_value = "docs/assets"
            return m
        return Path(path_str) # Default fallback

    with patch("htag.cli.Path", side_effect=mock_path_constructor), \
         patch("htag.cli.subprocess.run") as mock_run:
        
        # We need mock_entry_path.resolve() to return itself
        mock_entry_path.resolve.return_value = mock_entry_path
        
        cli.build("my_app.py")
        
        # Assert subprocess was called correctly
        assert mock_run.called
        call_args = mock_run.call_args[0][0] # The cmd list
        assert "uv" in call_args
        assert "pyinstaller" in call_args
        assert "--name" in call_args
        assert "my_app" in call_args
        assert "--hidden-import" in call_args
        assert "starlette" in call_args # Verify the fastapi -> starlette migration
        assert "my_app.py" in call_args
        
        # Verify cleanup of spec file
        assert mock_spec_file.unlink.called
        
        captured = capsys.readouterr()
        assert "Building" in captured.out
        assert "Successfully built" in captured.out
        assert "Cleaning up" in captured.out

def test_build_subprocess_failure(capsys):
    mock_entry_path = MagicMock()
    mock_entry_path.exists.return_value = True
    mock_entry_path.stem = "failing_app"
    mock_entry_path.resolve.return_value = mock_entry_path
    
    with patch("htag.cli.Path", return_value=mock_entry_path), \
         patch("htag.cli.subprocess.run") as mock_run:
        
        mock_run.side_effect = subprocess.CalledProcessError(returncode=42, cmd=["uv"])
        
        with pytest.raises(SystemExit) as e:
            cli.build("failing_app.py")
        assert e.value.code == 42
        
        captured = capsys.readouterr()
        assert "Build failed" in captured.out

def test_clear_build(capsys):
    mock_dir = MagicMock()
    mock_dir.exists.return_value = True
    mock_dir.is_dir.return_value = True
    
    with patch("htag.cli.Path", return_value=mock_dir), \
         patch("htag.cli.shutil.rmtree") as mock_rmtree:
        
        cli.clear_build()
        
        # Should be called 4 times, once for build, dist, .buildozer, bin
        assert mock_rmtree.call_count == 4
        
        captured = capsys.readouterr()
        assert "Removing" in captured.out
        assert "Cleanup complete" in captured.out

def test_main_help(capsys):
    with patch.object(sys, "argv", ["htagm", "--help"]):
        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.value.code == 0
        
        captured = capsys.readouterr()
        assert "COMMANDS" in captured.out
        assert "build" in captured.out

def test_main_missing_command(capsys):
    with patch.object(sys, "argv", ["htagm"]):
        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.value.code == 1
        
        captured = capsys.readouterr()
        assert "COMMANDS" in captured.out

def test_main_build_command():
    with patch.object(sys, "argv", ["htagm", "build", "app.py"]), \
         patch("htag.cli.build") as mock_build:
        cli.main()
        mock_build.assert_called_once_with("app.py")

def test_main_build_clear_command():
    with patch.object(sys, "argv", ["htagm", "build", "clear"]), \
         patch("htag.cli.clear_build") as mock_clear:
        cli.main()
        mock_clear.assert_called_once()
