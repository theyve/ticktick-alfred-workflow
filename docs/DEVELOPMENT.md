# Development

Edit `info.plist` for the workflow, `scripts/lists.js` for the local list reader, and `docs/WORKFLOW.md` for its embedded Readme. The build embeds the JavaScript directly in the Script Filter.

Build with Python 3.10+ (only needed for development):

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

The workflow and SHA-256 checksum are written to `dist/`. The package contains only the manifest, icon, Readme, and license.

References: [TickTick URL Scheme](https://help.ticktick.com/articles/7055781515422072832), [Alfred Open URL](https://www.alfredapp.com/help/workflows/actions/open-url/), [Gallery submission](https://alfred.app/submit/).

Complete the [Mac test checklist](VERIFY.md) before a stable release. For the Gallery, add current screenshots and gather forum feedback first.

## Local list selection

The only runtime code is `scripts/lists.js`, run directly by Alfred as JavaScript for Automation. It uses TickTick’s `projects` command, documented in the app’s scripting dictionary (`TickTick.app/Contents/Resources/TickTick.sdef`). The returned `closed` and `kind` fields were verified with the installed app. No task data is read or written by this script, and no lists are saved in the workflow or a cache.

Alfred handles text filtering; each new picker invocation reloads lists. Only open TASK lists appear. The documented Add Task URL uses list names, so duplicate names are shown as unavailable to prevent ambiguous delivery. Titles and list names are encoded by native Open URL objects. Variable inputs are kept separate from script source.

The JXA Script Filter configuration follows Alfred’s official [example workflow](https://github.com/alfredapp/openai-workflow/blob/main/Workflow/info.plist). Argument storage, list filters, and modifier connections follow Alfred’s bundled examples. The `tti` URL was tested successfully by the user; the calendar URL was not and is omitted.
