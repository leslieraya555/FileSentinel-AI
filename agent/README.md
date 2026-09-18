# Linux Monitoring Agent

**Author:** Leslie Raya  
**Project:** FileSentinel AI

## Overview

The FileSentinel AI monitoring agent is a C program that uses Linux
`inotify` to capture file-system events in a selected directory.

The agent records events in a CSV file for the project's backend and
detection components to analyze. Suspicious activity detection is
handled by other parts of FileSentinel AI.

## Files

| File | Purpose |
| --- | --- |
| `monitor.c` | Source code for the Linux monitoring agent. |
| `Makefile` | Instructions for compiling the agent. |
| `README.md` | Setup, usage, and testing instructions. |

## Requirements

- Linux with `inotify` support.
- A C compiler, such as GCC.
- GNU Make.
- Permission to monitor the selected directory.
- Permission to write to the event-output directory.

### Running from macOS

The agent cannot run directly on macOS because it depends on Linux
`inotify`.

On a Mac, use a Linux virtual machine or a Multipass Linux instance.
Run the build and monitoring commands inside that Linux environment,
where a copy of the project must be available.

## Build the Agent

Starting from the main FileSentinel AI project directory, run:

```bash
cd agent
make
```

The build should create an executable named `monitor`.

## Start Monitoring

From the `agent` directory, create the test directory and the directory
for event output:

```bash
mkdir -p ../watch_folder ../data
```

Start the agent:

```bash
./monitor ../watch_folder ../data/events.csv
```

This command uses two arguments:

| Argument | Purpose |
| --- | --- |
| `../watch_folder` | Directory to monitor. |
| `../data/events.csv` | CSV file where captured events are written. |

These relative paths assume that the command is run from the
`agent` directory.

Leave the terminal open while the agent is running.

## Test File Activity

Open a second terminal in the same Linux environment.

Navigate to the main FileSentinel AI project directory, then run
the following commands one at a time.

Use a dedicated test directory. Before running these commands, ensure
that the sample filenames do not belong to files you want to keep.

### Create a Test File

```bash
touch watch_folder/filesentinel_test.txt
```

### Modify the Test File

```bash
echo "FileSentinel AI monitoring test" >> watch_folder/filesentinel_test.txt
```

### Rename the Test File

```bash
mv watch_folder/filesentinel_test.txt watch_folder/filesentinel_test_renamed.txt
```

### Delete the Test File

```bash
rm watch_folder/filesentinel_test_renamed.txt
```

## Inspect Recorded Events

From the main project directory, run:

```bash
cat data/events.csv
```

Check the output for events associated with the test files.

The exact event labels and CSV fields are defined by `monitor.c`.
A single file operation may generate multiple events.

## Stop the Agent

Press **Ctrl+C** in the terminal where the agent is running.

## How the Agent Fits into FileSentinel AI

1. The agent observes activity in the selected directory.
2. Captured events are written to the CSV output.
3. The backend and detection components use the event data.
4. The frontend displays information provided by the backend.

The agent and backend must be configured to use the same event file.
When they run in separate environments, the file must be shared or
transferred through an explicitly configured mechanism.

## Limitations

- Requires Linux; it does not run directly on macOS or Windows.
- Monitors one directory without recursively monitoring subdirectories.
- Captures events only while the agent is running.
- Does not independently classify activity as malicious.
- Does not automatically block file operations or recover deleted files.

## Troubleshooting

### Compilation Fails on macOS

Build inside a Linux environment. Linux-specific headers such as
`sys/inotify.h` are not provided natively by macOS.

### The `make` Command Is Missing

Install the build tools for your Linux distribution, including Make
and a C compiler.

### The `monitor` Executable Is Missing

Run `make` from the directory containing the agent's `Makefile`.
Check the compiler output for errors.

### The Monitored Directory Cannot Be Opened

Confirm that the directory exists and that your user has permission
to access it.

### The CSV File Cannot Be Written

Confirm that the output directory exists and is writable.

### No Test Events Appear

Confirm that:

- The agent is still running.
- Your test commands operate on the directory being monitored.
- You are inspecting the same CSV file passed to the agent.
- The test terminal and agent use the same Linux environment.
- The test files are directly inside the monitored directory.

## Related Components

- [Main README](../README.md): Main project documentation.
- [Backend](../backend/): Backend and detection components.
- [Machine Learning](../ml/): Machine-learning components.
- [Frontend](../frontend/): Frontend dashboard.
- [Scripts](../scripts/): Project utility and simulation scripts.