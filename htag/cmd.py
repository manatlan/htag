#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import argparse
import re
from pathlib import Path


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


def clear_build():
    """Removes build/ and dist/ directories"""
    for d in ["build", "dist"]:
        path = Path(d)
        if path.exists() and path.is_dir():
            print(f"🧹 {C.CYAN}Removing{C.END} '{path}'...")
            shutil.rmtree(path)
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

    args = parser.parse_args()

    if args.command == "build":
        if args.path == "clear":
            clear_build()
        else:
            build(args.path)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
