# Development

Edit `README.md` for usage and setup, `info.plist` for the workflow, and `scripts/lists.js` for the local list reader. The build embeds the Readme and JavaScript in the packaged manifest without changing the source manifest. Always import the built `.alfredworkflow` file.

Build with Python 3.10+ (only needed for development):

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

The workflow and SHA-256 checksum are written to `dist/`. The package contains only the manifest, icon, and license. The Readme appears inside Alfred and is maintained only in `README.md`.

References: [TickTick URL Scheme](https://help.ticktick.com/articles/7055781515422072832), [Alfred Open URL](https://www.alfredapp.com/help/workflows/actions/open-url/)


## Local list selection

The only runtime code is `scripts/lists.js`, run directly by Alfred as JavaScript for Automation. It uses TickTick’s `projects` command, documented in the app’s scripting dictionary (`TickTick.app/Contents/Resources/TickTick.sdef`). No lists are saved in the workflow or a cache.

The JXA Script Filter configuration follows Alfred’s official [example workflow](https://github.com/alfredapp/openai-workflow/blob/main/Workflow/info.plist). Argument storage, list filters, and modifier connections follow Alfred’s bundled examples.