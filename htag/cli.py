import os
import sys
import subprocess
import shutil
import argparse
import re
from pathlib import Path
import tempfile


class C:
    """Simple ANSI color codes"""

    HEADER = "\x1b[95m"
    BLUE = "\x1b[94m"
    CYAN = "\x1b[96m"
    GREEN = "\x1b[92m"
    YELLOW = "\x1b[93m"
    RED = "\x1b[91m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    END = "\x1b[0m"


def build(entrypoint: str):
    """
    Builds a PyInstaller onefile executable for an htag app using 'uv'.
    """
    entry_path = Path(entrypoint).resolve()
    if not entry_path.exists():
        print(f"{C.RED}{C.BOLD}Error:{C.END} Entrypoint '{entrypoint}' not found.")
        sys.exit(1)

    app_name = entry_path.stem
    print(
        f"🚀 {C.BLUE}Building{C.END} '{C.BOLD}{app_name}{C.END}' from '{entry_path}'..."
    )

    # Identify hidden imports common to htag apps
    hidden_imports = [
        "starlette",
        "uvicorn",
        "websockets",
        "htag",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.loops.uvloop",
        "asyncio",
    ]

    # Command construction
    cmd = [
        "uv",
        "run",
        "--with",
        "pyinstaller",
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name",
        app_name,
    ]

    for hi in hidden_imports:
        cmd.extend(["--hidden-import", hi])

    # Ensure assets directory is bundled if it exists
    assets_dir = Path("assets")
    if assets_dir.exists():
        print(f"📦 {C.CYAN}Bundling assets{C.END} from '{assets_dir}'...")
        # PyInstaller uses different path separators for data depending on OS
        separator = ";" if os.name == "nt" else ":"
        cmd.extend(["--add-data", f"{assets_dir}{separator}assets"])

    cmd.append(str(entry_path))

    print(f"⚙️ {C.YELLOW}Running command:{C.END} {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(
            f"✅ {C.GREEN}{C.BOLD}Successfully built{C.END} '{C.BOLD}{app_name}{C.END}' in 'dist/' directory."
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ {C.RED}{C.BOLD}Build failed{C.END} with return code {e.returncode}")
        sys.exit(e.returncode)
    finally:
        spec_file = Path(f"{app_name}.spec")
        if spec_file.exists():
            print(f"🧹 {C.CYAN}Cleaning up{C.END} '{spec_file}'...")
            spec_file.unlink()


def build_apk(entrypoint: str, is_tv: bool = False):
    """
    Builds an Android APK for an htag app using Docker and Buildozer.
    """
    entry_path = Path(entrypoint).resolve()
    if not entry_path.exists():
        print(f"{C.RED}{C.BOLD}Error:{C.END} Entrypoint '{entrypoint}' not found.")
        sys.exit(1)

    app_name = entry_path.stem

    if not shutil.which("docker"):
        print(f"❌ {C.RED}{C.BOLD}Error:{C.END} Docker is required to build an APK.")
        print("Please install docker: https://docs.docker.com/engine/install/")
        sys.exit(1)

    print(
        f"🚀 {C.BLUE}Building APK{C.END} for '{C.BOLD}{app_name}{C.END}' from '{entry_path}'..."
    )

    DOCKER_IMAGE = "kivy/buildozer"

    # Check if Buildozer image exists
    print(f"🐳 {C.CYAN}Checking Docker image '{DOCKER_IMAGE}'...{C.END}")
    try:
        res = subprocess.run(
            f"docker images {DOCKER_IMAGE} -q",
            shell=True,
            capture_output=True,
            text=True,
        )
        if not res.stdout.strip():
            print(
                f"⬇️  {C.YELLOW}Docker image '{DOCKER_IMAGE}' not found. Building it...{C.END}"
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(
                    f"cd {tmpdir} && git clone https://github.com/kivy/buildozer.git .",
                    shell=True,
                    check=True,
                )
                print(
                    f"⚙️  {C.YELLOW}Building docker image (this may take a while)...{C.END}"
                )
                subprocess.run(
                    f"cd {tmpdir} && docker build --tag={DOCKER_IMAGE} .",
                    shell=True,
                    check=True,
                )
            print(
                f"✅ {C.GREEN}{C.BOLD}Docker image '{DOCKER_IMAGE}' built successfully.{C.END}"
            )
    except subprocess.CalledProcessError:
        print(f"❌ {C.RED}{C.BOLD}Failed to build/check Docker image.{C.END}")
        sys.exit(1)

    # Create buildozer.spec if it doesn't exist
    spec_path = Path("buildozer.spec")
    if not spec_path.exists():
        print(f"📝 {C.CYAN}Generating default 'buildozer.spec'...{C.END}")
        # Adjust settings for Android TV
        orientation = "landscape" if is_tv else "portrait"
        fullscreen = "1" if is_tv else "0"
        android_archs = "armeabi-v7a" if is_tv else "arm64-v8a"

        icon_path_entry = entry_path.parent / "icon.png"
        icon_path_cwd = Path("icon.png")
        icon_path = icon_path_cwd if icon_path_cwd.exists() else icon_path_entry
        icon_setting = (
            "icon.filename = %(source.dir)s/icon.png\n" if icon_path.exists() else ""
        )

        spec_content = f"""[app]
title = {app_name.capitalize()}
package.name = {app_name.lower()}
package.domain = org.htag
version = 1.0

source.dir = .
source.include_exts = py,png,jpg,jpeg,svg,js,css,html

requirements = android,htag2,starlette,uvicorn,websockets,anyio,typing_extensions,click,httpx,h11
orientation = {orientation}
fullscreen = {fullscreen}
android.archs = {android_archs}
android.api = 34
android.minapi = 24
android.ndk = 27c
{icon_setting}
home_app = 1
android.permissions = INTERNET
android.accept_sdk_license = True

p4a.hook = p4a/hook.py
p4a.port = 13333
p4a.bootstrap = webview
p4a.branch = v2024.01.21
[buildozer]
log_level = 2
"""
        spec_path.write_text(spec_content)
        print(f"✅ {C.GREEN}Created 'buildozer.spec'{C.END}")

    # Ensure .buildozer exists locally
    Path(".buildozer").mkdir(exist_ok=True)

    print(f"⚙️ {C.YELLOW}Running buildozer in Docker...{C.END}")

    # Run buildozer in Docker
    cwd = Path.cwd()
    cmd = [
        "docker",
        "run",
        "-it",
        "--rm",
        "-v",
        f"{cwd}/.buildozer:/home/user/.buildozer",
        "-v",
        f"{cwd}:/home/user/hostcwd",
        DOCKER_IMAGE,
        "android",
        "debug",
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {C.GREEN}{C.BOLD}Successfully built APK{C.END} in 'bin/' directory.")
    except subprocess.CalledProcessError as e:
        print(
            f"❌ {C.RED}{C.BOLD}Buildozer failed{C.END} with return code {e.returncode}"
        )
        print(
            f"💡 {C.DIM}Check the logs above for details. You might need to adjust 'buildozer.spec'.{C.END}"
        )
        sys.exit(e.returncode)


def clear_build():
    """Removes build/, dist/, .buildozer/ and bin/ directories, and buildozer.spec"""
    for d in ["build", "dist", ".buildozer", "bin", "buildozer.spec"]:
        path = Path(d)
        if path.exists():
            print(f"🧹 {C.CYAN}Removing{C.END} '{path}'...")
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            except Exception as e:
                print(f"⚠️ {C.YELLOW}Warning:{C.END} Could not remove '{path}': {e}")

    # also remove spec file as part of clear? Up to user preference, leaving it for now so they don't lose config
    print(f"✨ {C.GREEN}{C.BOLD}Cleanup complete.{C.END}")


class UvHelpFormatter(argparse.HelpFormatter):
    """Modern HelpFormatter inspired by uv/cargo"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position=24, width=100)

    def start_section(self, heading):
        return super().start_section(f"\n{C.BOLD}{heading.upper()}{C.END}")

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return (
                f"{C.GREEN}{C.BOLD}{super()._format_action_invocation(action)}{C.END}"
            )
        else:
            parts = [f"{C.CYAN}{s}{C.END}" for s in action.option_strings]
            return ", ".join(parts)

    def _get_help_string(self, action):
        help_text = super()._get_help_string(action)
        return f"{C.DIM}{help_text}{C.END}"

    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            parts = []
            for choice_action in action._choices_actions:
                name = choice_action.dest
                help_text = choice_action.help or ""
                parts.append(
                    f"  {C.GREEN}{C.BOLD}{name:<8}{C.END} {C.DIM}{help_text}{C.END}"
                )
            return "\n".join(parts) + "\n"
        return super()._format_action(action)

    def format_help(self):
        help_text = super().format_help()
        lines = help_text.split("\n")
        new_lines = []
        for line in lines:
            if re.search(r"(usage|Usage):", line, re.IGNORECASE):
                clean_line = re.sub(r"^.*?((usage|Usage):)\s*", "", line).strip()
                clean_line = clean_line.replace(
                    "{build}", f"{C.CYAN}<COMMAND>{C.END}{C.YELLOW}"
                )
                clean_line = clean_line.replace(
                    "{build,apk}", f"{C.CYAN}<COMMAND>{C.END}{C.YELLOW}"
                )
                new_lines.append(
                    f"{C.YELLOW}{C.BOLD}Usage:{C.END} {C.YELLOW}{clean_line}{C.END}"
                )
            else:
                new_lines.append(line)
        return "\n".join(new_lines)


def main():
    parser = argparse.ArgumentParser(
        prog="htagm",
        description=f"{C.BOLD}An htag companion tool.{C.END}",
        formatter_class=UvHelpFormatter,
        add_help=False,
    )

    parser._optionals.title = "Options"

    parser.add_argument(
        "-h", "--help", action="help", help="Display documentation for htagm"
    )

    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # Build command
    build_parser = subparsers.add_parser(
        "build",
        help="Build standalone executables for your htag app.",
        description=f"{C.BOLD}Build standalone executables for your htag app.{C.END}",
        formatter_class=UvHelpFormatter,
        add_help=False,
    )
    build_parser._positionals.title = "Arguments"
    build_parser._optionals.title = "Options"

    build_parser.add_argument(
        "-h", "--help", action="help", help="Display help for the build command"
    )
    build_parser.add_argument(
        "path", help="Path to main script, or 'clear' to reset folders"
    )

    # Apk command
    apk_parser = subparsers.add_parser(
        "apk",
        help="Build Android APKs for your htag app via Docker.",
        description=f"{C.BOLD}Build Android APKs for your htag app via Docker & Buildozer.{C.END}",
        formatter_class=UvHelpFormatter,
        add_help=False,
    )
    apk_parser._positionals.title = "Arguments"
    apk_parser._optionals.title = "Options"

    apk_parser.add_argument(
        "-h", "--help", action="help", help="Display help for the apk command"
    )
    apk_parser.add_argument("path", help="Path to main script to build as APK")
    apk_parser.add_argument(
        "--tv",
        action="store_true",
        help="Build optimized for Android TV (landscape, fullscreen, armeabi-v7a)",
    )

    args = parser.parse_args()

    if args.command == "build":
        if args.path == "clear":
            clear_build()
        else:
            build(args.path)
    elif args.command == "apk":
        if args.path == "clear":
            clear_build()
        else:
            build_apk(args.path, is_tv=args.tv)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
