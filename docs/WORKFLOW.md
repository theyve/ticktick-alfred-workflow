## Usage

```text
ttn Buy milk
```

* **Return:** add to Inbox, without priority.
* **⌥Return:** choose a list. Then Return to add, or ⌘Return to choose a priority.
* **⌘Return:** choose a priority and add to Inbox.

List and priority selection are optional. The list picker reads all non-archived task lists from TickTick. Priority choices are None, Low, Medium, and High. TickTick opens when you add the task.

| Keyword | Action |
| --- | --- |
| `ttn Task title` | Add a task |
| `tti` | Open Inbox |
| `ttt` | Open Today |
| `tt7` | Open Next 7 Days |

Alternatively, select text and use **Add to TickTick Inbox** in Universal Actions. The same optional modifiers apply.

## Setup

Requires Alfred with Powerpack and the TickTick Mac app, signed in.

1. Open the `.alfredworkflow` file to install. Disable older workflows using the same keywords.
2. On first list selection, allow Alfred to control TickTick if macOS asks.
3. Add a test task and check its destination and priority.

Change keywords in **Configure Workflow**. No extra software or API token needed.

Beta: the new selection flow still needs testing in Alfred.
