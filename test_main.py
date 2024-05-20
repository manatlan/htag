import sys,subprocess

def test_main_help():
    cmds=[sys.executable,"-m","htag","-h"]
    stdout = subprocess.run(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
    assert "--gui" in stdout
    assert "--no-gui" in stdout
