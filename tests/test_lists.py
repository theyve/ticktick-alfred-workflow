"""Run the actual JXA with a fake TickTick application; no account access."""

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == 'darwin', 'JXA is supplied by macOS')
class ListReaderTests(unittest.TestCase):
    def run_reader(self, response):
        source = (ROOT / 'scripts/lists.js').read_text()
        # Scope a fake bridge locally; JXA's global Application is read-only.
        source = ('function run() { return (function (Application) {\n' + source +
                  '\nreturn run();\n})(function () { return {projects: function () { return ' +
                  json.dumps(json.dumps(response)) + '; }}; }); }')
        result = subprocess.run(['/usr/bin/osascript', '-l', 'JavaScript'], input=source,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)['items']

    def test_archived_and_note_lists_excluded_names_preserved_inbox_first(self):
        name = '🏡 Project & "Design" + 50%'
        items = self.run_reader([
            {'id': 'a', 'name': name, 'closed': False, 'kind': 'TASK'},
            {'id': 'b', 'name': 'Archived', 'closed': True, 'kind': 'TASK'},
            {'id': 'c', 'name': 'Notes', 'closed': False, 'kind': 'NOTE'},
            {'id': 'i', 'name': 'Inbox', 'closed': False, 'kind': 'TASK'},
        ])
        self.assertEqual([i['title'] for i in items], ['Inbox', name])
        self.assertEqual([i['arg'] for i in items], ['Inbox', name])
        self.assertTrue(all(i['valid'] for i in items))

    def test_duplicate_name_cannot_silently_select_wrong_list(self):
        items = self.run_reader([
            {'id': 'a', 'name': 'Same', 'closed': False, 'kind': 'TASK'},
            {'id': 'b', 'name': 'Same', 'closed': True, 'kind': 'TASK'},
        ])
        self.assertEqual(len(items), 1)
        self.assertFalse(items[0]['valid'])

    def test_empty_or_malformed_response_cannot_create_tasks(self):
        for response in ([], {'error': 'PRIVATE_SENTINEL'}, [{'id': 'a'}]):
            with self.subTest(response=response):
                items = self.run_reader(response)
                self.assertTrue(items)
                self.assertTrue(all(not i['valid'] for i in items))
                self.assertNotIn('PRIVATE_SENTINEL', json.dumps(items))
