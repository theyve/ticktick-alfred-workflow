# Development

Edit `README.md` for usage and setup, `CHANGELOG.md` for release notes, `info.plist` for the workflow graph, and `scripts/lists.js` for the local list reader. The source Script Filter `script` field is a placeholder; the build replaces it with `lists.js` (and embeds the Readme) without changing the source. Always import the built `.alfredworkflow` file.

Build with Python 3.10+ (only needed for development):

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

Build refuses to package a version that has no matching `## x.y.z` section with at least one `- ` note in `CHANGELOG.md`.

## Release

```sh
python3 scripts/release.py
```

It asks for major/minor/patch, collects changelog bullets, bumps `info.plist`, updates `CHANGELOG.md`, runs tests, and builds. At the end it can create a GitHub Release with the `.alfredworkflow` and checksum attached (`gh` must be logged in). Commit the bumped files afterwards if you have not already.

The workflow and SHA-256 checksum are written to `dist/`. The package contains the manifest, icon, license, and Readme screenshots under `images/`. The Readme appears inside Alfred and is maintained only in `README.md`.

References: [TickTick URL Scheme](https://help.ticktick.com/articles/7055781515422072832), [Alfred Open URL](https://www.alfredapp.com/help/workflows/actions/open-url/)

## Local list selection

The only runtime code is `scripts/lists.js`, run directly by Alfred as JavaScript for Automation. It uses TickTick’s `projects` command, documented in the app’s scripting dictionary (`TickTick.app/Contents/Resources/TickTick.sdef`). No lists are saved in the workflow or a cache.

The JXA Script Filter configuration follows Alfred’s official [example workflow](https://github.com/alfredapp/openai-workflow/blob/main/Workflow/info.plist). Argument storage, list filters, and modifier connections follow Alfred’s bundled examples.
