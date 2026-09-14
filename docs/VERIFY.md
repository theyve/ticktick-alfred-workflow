# Manual verification: Alfred 5.8 / TickTick 8.2

Import `TickTick-Inbox-2.0.0-beta.4.alfredworkflow` and disable older versions with overlapping keywords.

1. `ttn Inbox Test` → Return: one task in Inbox, no priority, no picker.
2. `ttn List Test` → ⌥Return: allow Alfred automation access if macOS asks. Check that non-archived task lists appear, Inbox first. Archived lists must be absent. Type to filter, select a list, then Return: one task in that list, no priority.
3. `ttn Priority Test` → ⌘Return → High: one task in Inbox with high priority. Repeat for None, Low, and Medium.
4. `ttn Both Test` → ⌥Return → select a list → ⌘Return → choose a priority: one task in the chosen list with that priority. Test a list whose name contains an emoji.
5. Repeat using the title `Äpfel & Brot #1 + 50% | "Test" ?list=Other`. Check the exact title, destination, and priority.
6. Cancel the list or priority picker with Escape: no task must be created.
7. Rename or archive a test list in TickTick, then reopen the picker and check it updates.
8. Select text in another app and invoke **Add to TickTick Inbox** through Universal Actions. Test Return, ⌥Return, and ⌘Return. Files and multiple selections should not show the action.
9. Test `tti`, `ttt`, and `tt7`. `tti` was already confirmed by the user. There is no `ttc`.
10. Remove test tasks in TickTick.

Automated checks cover package contents, routing, and the list reader with synthetic data. Live list reading was also checked locally. Creating tasks and the complete Alfred interaction still need this manual check.

Before Gallery submission, record tested app versions, add current screenshots, and gather forum feedback.
