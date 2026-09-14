#!/usr/bin/env python3
"""Bump the version, require changelog notes, build, and optionally publish on GitHub."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        print()
        sys.exit(1)


def ask_choice(prompt, choices):
    choices = list(choices)
    while True:
        answer = ask(prompt).lower()
        if answer in choices:
            return answer
        print("Choose one of: " + ", ".join(choices))


def ask_yes_no(prompt):
    return ask_choice(prompt + " [y/n]: ", ("y", "n")) == "y"


def ask_notes():
    print("Changelog notes for users (one bullet per line, empty line to finish):")
    notes = []
    while True:
        line = ask("> ")
        if not line:
            if notes:
                return notes
            print("At least one note is required.")
            continue
        notes.append(line.lstrip("- ").strip())


def run(command, **kwargs):
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True, **kwargs)


def github_release(version, notes, package):
    body = "\n".join(f"- {note}" for note in notes) + "\n"
    checksum = package.with_suffix(package.suffix + ".sha256")
    run([
        "gh", "release", "create", version,
        "--title", version,
        "--notes", body,
        str(package),
        str(checksum),
    ])


def main():
    current = build.read_version()
    print(f"Current version: {current}")
    part = ask_choice("Release type [major/minor/patch]: ", ("major", "minor", "patch"))
    version = build.bump_version(current, part)
    print(f"Next version: {version}")
    notes = ask_notes()
    print()
    print(f"## {version}")
    for note in notes:
        print(f"- {note}")
    print()
    if not ask_yes_no("Write version + changelog and build"):
        print("Aborted.")
        return 1

    build.prepend_changelog(version, notes)
    build.write_version(version)
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    package = build.build()
    print(package)
    print(package.with_suffix(package.suffix + ".sha256"))

    if ask_yes_no("Create GitHub release " + version):
        github_release(version, notes, package)
        print(f"Published https://github.com/theyve/ticktick-alfred-workflow/releases/tag/{version}")
    else:
        print("Build is ready in dist/. Commit the version bump and CHANGELOG when you want.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
