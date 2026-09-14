"""Create a reproducible, credential-free .alfredworkflow archive."""

import hashlib
from pathlib import Path
import plistlib
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = ("icon.png", "LICENSE")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
SECTION_RE = re.compile(r"^##\s+(\d+\.\d+\.\d+)\s*$", re.MULTILINE)


def read_version(root=ROOT):
    version = plistlib.loads((root / "info.plist").read_bytes())["version"]
    if not VERSION_RE.fullmatch(version):
        raise ValueError("info.plist version must be semantic (MAJOR.MINOR.PATCH).")
    return version


def write_version(version, root=ROOT):
    if not VERSION_RE.fullmatch(version):
        raise ValueError("Version must be semantic (MAJOR.MINOR.PATCH).")
    path = root / "info.plist"
    text = path.read_text()
    updated, count = re.subn(
        r"(<key>name</key>\s*<string>TickTick Inbox</string>\s*<key>version</key>\s*<string>)[^<]+(</string>)",
        rf"\g<1>{version}\2",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError("Could not update the workflow version in info.plist.")
    path.write_text(updated)


def bump_version(version, part):
    if not VERSION_RE.fullmatch(version):
        raise ValueError("Version must be semantic (MAJOR.MINOR.PATCH).")
    major, minor, patch = (int(piece) for piece in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError("Release type must be major, minor, or patch.")


def changelog_sections(text):
    matches = list(SECTION_RE.finditer(text))
    sections = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        notes = [line[2:].strip() for line in body.splitlines() if line.startswith("- ")]
        notes = [note for note in notes if note]
        sections[match.group(1)] = notes
    return sections


def require_changelog(version, root=ROOT):
    path = root / "CHANGELOG.md"
    if not path.is_file():
        raise ValueError("CHANGELOG.md is required before packaging.")
    notes = changelog_sections(path.read_text()).get(version)
    if not notes:
        raise ValueError(
            f"CHANGELOG.md needs a ## {version} section with at least one '- ' note "
            "before this version can be packaged."
        )
    return notes


def prepend_changelog(version, notes, root=ROOT):
    if not notes:
        raise ValueError("Changelog notes are required.")
    path = root / "CHANGELOG.md"
    existing = path.read_text() if path.is_file() else "# Changelog\n"
    if version in changelog_sections(existing):
        raise ValueError(f"CHANGELOG.md already has a ## {version} section.")
    block = f"## {version}\n\n" + "\n".join(f"- {note}" for note in notes) + "\n"
    if existing.startswith("# Changelog"):
        rest = existing.split("\n", 1)[1].lstrip("\n")
        path.write_text("# Changelog\n\n" + block + ("\n" + rest if rest else ""))
    else:
        path.write_text("# Changelog\n\n" + block + "\n" + existing.lstrip())


def build(root=ROOT, output=None):
    manifest = plistlib.loads((root / "info.plist").read_bytes())
    keywords = {"new_keyword", "today_keyword", "week_keyword", "inbox_keyword"}
    if manifest.get("variables") or any(
        c["variable"] not in keywords for c in manifest["userconfigurationconfig"]
    ):
        raise ValueError("Only keyword configuration belongs in this workflow.")
    require_changelog(manifest["version"], root)
    manifest["readme"] = (root / "README.md").read_text()
    for obj in manifest["objects"]:
        if obj["type"] == "alfred.workflow.input.scriptfilter":
            obj["config"]["script"] = (root / "scripts" / "lists.js").read_text()
    files = {"info.plist": plistlib.dumps(manifest, sort_keys=False)}
    paths = [root / name for name in PUBLIC_FILES]
    paths.extend(sorted((root / "images").glob("*.png")))
    for path in paths:
        if path.is_symlink():
            raise ValueError("Refusing to package symlink: " + str(path))
        files[path.relative_to(root).as_posix()] = path.read_bytes()
    output = output or root / "dist" / ("TickTick-Inbox-" + manifest["version"] + ".alfredworkflow")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(digest + "  " + output.name + "\n")
    return output


if __name__ == "__main__":
    print(build())
