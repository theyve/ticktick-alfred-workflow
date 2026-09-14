"""Check the distributable, especially exclusion of old code and preferences."""

import importlib.util
from pathlib import Path
import plistlib
import shutil
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "scripts" / "build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PackageTests(unittest.TestCase):
    def test_archive_is_reproducible_and_excludes_private_and_runtime_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", "prefs.plist"))
            (root / "prefs.plist").write_text("PRIVATE_SENTINEL")
            (root / "legacy.py").write_text("PRIVATE_SENTINEL")
            source_manifest = (root / "info.plist").read_bytes()
            source = plistlib.loads(source_manifest)
            self.assertNotIn("readme", source)
            for obj in source["objects"]:
                if obj["type"] == "alfred.workflow.input.scriptfilter":
                    script = obj["config"]["script"]
                    self.assertIn("PLACEHOLDER", script)
                    self.assertIn("scripts/lists.js", script)
                    self.assertNotEqual(script, (root / "scripts/lists.js").read_text())
            readme = root / "README.md"
            readme.write_text(readme.read_text() + "\nUpdated build instructions.\n")
            output = builder.build(root)
            self.assertEqual((root / "info.plist").read_bytes(), source_manifest)
            self.assertEqual(output.read_bytes(), builder.build(root).read_bytes())
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), {
                    "info.plist", "icon.png", "LICENSE",
                    "images/add.png", "images/priority.png", "images/next7.png"})
                for name in archive.namelist():
                    self.assertNotIn(b"PRIVATE_SENTINEL", archive.read(name))
                manifest = plistlib.loads(archive.read("info.plist"))
                self.assertEqual(manifest["readme"], readme.read_text())
                objects = {o["uid"]: o for o in manifest["objects"]}
                self.assertEqual({o["type"] for o in objects.values()}, {
                    "alfred.workflow.input.keyword", "alfred.workflow.action.openurl",
                    "alfred.workflow.trigger.universalaction", "alfred.workflow.utility.argument",
                    "alfred.workflow.input.listfilter", "alfred.workflow.input.scriptfilter"})
                for uid, edges in manifest["connections"].items():
                    self.assertIn(uid, objects)
                    for edge in edges:
                        self.assertIn(edge["destinationuid"], objects)
                for obj in objects.values():
                    if obj["type"] == "alfred.workflow.action.openurl":
                        self.assertTrue(obj["config"]["url"].startswith("ticktick://"))
                        self.assertFalse(obj["config"]["skipqueryencode"])
                        self.assertFalse(obj["config"]["skipvarencode"])
                    if obj["type"] == "alfred.workflow.input.scriptfilter":
                        self.assertEqual(obj["config"]["type"], 7)  # Native JXA, no shell.
                        self.assertEqual(obj["config"]["script"], (root / "scripts/lists.js").read_text())
                capture = next(o for o in objects.values()
                               if o["config"].get("keyword") == "{var:new_keyword}")
                universal = next(o for o in objects.values()
                                 if o["type"] == "alfred.workflow.trigger.universalaction")
                self.assertEqual(manifest["connections"][capture["uid"]],
                                 manifest["connections"][universal["uid"]])
                self.assertTrue(universal["config"]["acceptstext"])
                for key in ("acceptsfiles", "acceptsurls", "acceptsmulti"):
                    self.assertFalse(universal["config"][key])

    def test_capture_defaults_and_optional_routes(self):
        manifest = plistlib.loads((ROOT / "info.plist").read_bytes())
        objects = {o["uid"]: o for o in manifest["objects"]}
        def destination(obj, modifier=0):
            edges = manifest["connections"][obj["uid"]]
            edge = next(e for e in edges if e["modifiers"] == modifier)
            return objects[edge["destinationuid"]]
        capture = next(o for o in objects.values() if o["config"].get("keyword") == "{var:new_keyword}")
        default = destination(capture)
        self.assertEqual(default["config"]["url"], "ticktick://x-callback-url/v1/add_task?title={query}")
        list_store = destination(capture, 524288)
        self.assertEqual(list_store["config"]["variables"]["task_title"], "{query}")
        self.assertEqual(list_store["config"]["argument"], "")
        lists = destination(list_store)
        self.assertEqual(lists["type"], "alfred.workflow.input.scriptfilter")
        self.assertIn("title={var:task_title}&list={query}", destination(lists)["config"]["url"])
        inbox_store = destination(capture, 1048576)
        self.assertEqual(inbox_store["config"]["variables"], {"task_title": "{query}", "task_list": "inbox"})
        list_priority_store = destination(lists, 1048576)
        self.assertEqual(list_priority_store["config"]["variables"], {"task_list": "{query}"})
        priority = destination(inbox_store)
        self.assertEqual(priority["uid"], destination(list_priority_store)["uid"])
        import json
        self.assertEqual([i["arg"] for i in json.loads(priority["config"]["items"])], ["0", "1", "3", "5"])
        self.assertIn("title={var:task_title}&list={var:task_list}&priority={query}", destination(priority)["config"]["url"])

    def test_build_rejects_accidental_credential_configuration(self):
        for field in ("variables", "userconfigurationconfig"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest = plistlib.loads((ROOT / "info.plist").read_bytes())
                if field == "variables":
                    manifest[field] = {"api_token": "PRIVATE_SENTINEL"}
                else:
                    manifest[field].append({"variable": "api_token", "config": {"default": "PRIVATE_SENTINEL"}})
                (root / "info.plist").write_bytes(plistlib.dumps(manifest))
                with self.assertRaisesRegex(ValueError, "Only keyword configuration"):
                    builder.build(root)


if __name__ == "__main__":
    unittest.main()
