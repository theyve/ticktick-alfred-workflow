# TickTick Inbox for Alfred

## Usage

```text
ttn Buy milk
```

- **↵:** add task
- **⌥ + ↵:** choose list
- **⌘ + ↵:** choose priority

List and priority are optional. Lists come from TickTick; priorities are None, Low, Medium, High. TickTick opens on add.

| Keyword          | Action           |
| ---------------- | ---------------- |
| `ttn Task title` | Add a task       |
| `tti`            | Open Inbox       |
| `ttt`            | Open Today       |
| `tt7`            | Open Next 7 Days |

Alternatively, select text and use **Add to TickTick Inbox** in Universal Actions. The same optional modifiers apply.

## Setup

Requires Alfred with Powerpack and the TickTick Mac app, signed in.

1. Open the `.alfredworkflow` file to install.
2. On first list selection, allow Alfred to control TickTick if macOS asks.

Change keywords in **Configure Workflow**.

[Development](docs/DEVELOPMENT.md)

[MIT License](LICENSE)
