# FileSentinel AI Agent

This folder contains the C-based Linux file-system monitoring agent.

The agent uses Linux `inotify` to watch a folder for file activity.

It detects:

- File creation
- File modification
- File deletion
- File rename events
- File access events

## Build

```bash
make