// TickTick's installed scripting dictionary documents the read-only projects command.
// Alfred runs this directly as JavaScript for Automation; no shell or API token.
function listItems(projects) {
    if (!Array.isArray(projects) || !projects.every(function (p) {
        return p && typeof p.name === 'string' && p.name.length > 0 &&
            typeof p.id === 'string' && typeof p.closed === 'boolean';
    })) {
        throw new Error('Unexpected project format');
    }
    const active = projects.filter(function (p) {
        return !p.closed && p.kind === 'TASK';
    });
    active.sort(function (a, b) {
        if (a.name === 'Inbox') return -1;
        if (b.name === 'Inbox') return 1;
        return a.name.localeCompare(b.name);
    });
    return active.map(function (p) {
        // The documented URL selects by name. Do not silently choose between duplicates.
        const unique = projects.filter(function (other) { return other.name === p.name; }).length === 1;
        return {
            uid: p.id,
            title: p.name,
            arg: p.name,
            valid: unique,
            subtitle: unique ? 'Return: add task · ⌘Return: choose priority' :
                'Duplicate list name — rename it in TickTick before using this action'
        };
    });
}

function run() {
    try {
        const projects = JSON.parse(Application('TickTick').projects());
        const items = listItems(projects);
        if (!items.length) {
            items.push({title: 'No active task lists', subtitle: 'Check your lists in TickTick.', valid: false});
        }
        return JSON.stringify({items: items, skipknowledge: true});
    } catch (error) {
        return JSON.stringify({items: [{
            title: 'Could not read TickTick lists',
            subtitle: 'Open TickTick and allow Alfred to control it in macOS Settings → Privacy & Security → Automation.',
            valid: false
        }]});
    }
}
