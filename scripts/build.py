"""Create a reproducible, credential-free .alfredworkflow archive."""

import hashlib
from pathlib import Path
import plistlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = ("icon.png", "LICENSE")


def build(root=ROOT, output=None):
    manifest = plistlib.loads((root / "info.plist").read_bytes())
    keywords = {"new_keyword", "today_keyword", "week_keyword", "inbox_keyword"}
    if manifest.get("variables") or any(
        c["variable"] not in keywords for c in manifest["userconfigurationconfig"]
    ):
        raise ValueError("Only keyword configuration belongs in this workflow.")
    manifest["readme"] = (root / "README.md").read_text()
    for obj in manifest["objects"]:
        if obj["type"] == "alfred.workflow.input.scriptfilter":
            obj["config"]["script"] = (root / "scripts" / "lists.js").read_text()
    files = {"info.plist": plistlib.dumps(manifest, sort_keys=False)}
    paths = [root / name for name in PUBLIC_FILES]
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
