# FileSentinel AI

FileSentinel AI is a file-system monitoring and anomaly-detection project. It combines a Linux monitoring agent, a FastAPI backend, and a React dashboard to display file events and flag suspicious patterns.

The project uses behavioral rules to detect bulk file operations and an Isolation Forest model to assess unusual activity.

## Features

- Captures file creation, modification, deletion, rename, and access events on Linux.
- Records captured events in CSV format.
- Displays event counts and individual records in a React dashboard.
- Flags bursts of modifications, deletions, renames, and creations.
- Provides machine-learning anomaly assessments.
- Includes interactive API documentation and health checks.
- Provides a synthetic event simulation script.
- Includes automated backend tests and a GitHub Actions test workflow.

## Contents

- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Local Setup](#local-setup)
- [Run the Linux Monitoring Agent](#run-the-linux-monitoring-agent)
- [Configuration](#configuration)
- [Choose an Event Log](#choose-an-event-log)
- [Verified Multipass VM Setup](#verified-multipass-vm-setup)
- [Automated Tests](#automated-tests)
- [Frontend Production Build](#frontend-production-build)
- [Verification Results](#verification-results)
- [Model Training and Evaluation](#model-training-and-evaluation)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Author](#author)

## Screenshots

### Dashboard

Displays file activity, anomaly assessments, and rule alerts.

![FileSentinel dashboard](docs/images-filesentinel/dashboard/filesentinel-dashboard-01.png)

### API Documentation

Interactive documentation for the backend endpoints.

![API documentation](docs/images-filesentinel/screenshots/filesentinel-api-docs-01.png)

### Health Check

Shows backend status and readiness of the event store and model.

![Backend health check](docs/images-filesentinel/screenshots/filesentinel-api-health.png)

### Linux Agent Verification

The Linux agent captured file activity on October 12, 2026. The dashboard was verified with the saved event log on October 13, 2026.

The verification covered all five supported activity types:

- CREATE
- MODIFY
- DELETE
- ACCESS
- RENAME

The log contains six records because one rename operation produces two records: `RENAMED_FROM` and `RENAMED_TO`.

The dashboard displayed:

- API HEALTHY status
- Six event records
- All five activity types
- Zero rule alerts
- An ML anomaly assessment with a displayed score of 73/100

The anomaly score describes the model's assessment of this test activity. It is not a measure of model accuracy or a validated probability of infection.

The dashboard read a saved verification CSV. This screenshot documents a completed test; continuous monitoring requires the backend to read the CSV being updated by the agent.

![Linux agent verification dashboard](docs/images-filesentinel/dashboard/filesentinel-linux-verification-dashboard.png)

[Browse all screenshots](docs/images-filesentinel)

## Tech Stack

| Component | Technologies |
| --- | --- |
| Monitoring agent | C, Linux inotify |
| Backend | Python, FastAPI |
| Data processing | pandas, NumPy |
| Machine learning | scikit-learn, Isolation Forest, joblib |
| Frontend | React, JavaScript, Vite |
| Testing | pytest |
| Continuous integration | GitHub Actions |
| Version control | Git, GitHub |

## Project Structure

| Location | Purpose |
| --- | --- |
| `agent/` | Linux monitoring agent, Makefile, and instructions |
| `backend/` | API, event processing, and detection logic |
| `data/` | Event CSV files |
| `frontend/` | React dashboard |
| `ml/` | Training code, model artifacts, and metadata |
| `scripts/` | Simulation and utility scripts |
| `Automated tests/` | Python test suite |
| `.github/workflows/` | GitHub Actions workflow configuration |
| `docs/images-filesentinel/` | Project screenshots |
| `docs/verification/` | Saved verification evidence |
| `README.md` | Main project documentation |

## How It Works

1. The Linux agent watches a selected directory for file activity.
2. Captured events are written to a CSV file.
3. The backend reads event data and calculates activity statistics.
4. Behavioral rules check for bulk-operation patterns.
5. The machine-learning model assesses activity features for anomalies.
6. The dashboard displays the backend results.

The agent and backend must have access to the same event data. When they run in separate environments, the CSV must be explicitly shared or transferred.

Behavioral rules and the machine-learning model assess activity separately. An ML anomaly assessment can appear even when no rule threshold is exceeded.

## Requirements

- Python 3, pip, and virtual environment support
- Node.js and npm
- Git
- Linux, GCC, and Make for the monitoring agent
- Multipass if using the VM workflow described below

The C monitoring agent requires Linux because it uses inotify.

On macOS, run the agent inside a Linux virtual machine. The backend and frontend can run on the Mac or inside the VM.

The commands below use a macOS or Linux shell. Unless a section says otherwise, run project commands from the main project directory.

## Local Setup

This setup runs the backend and frontend on the machine where the commands are entered.

The backend uses port `8000`, and the frontend uses port `5173`.

### 1. Open the Project

For a new checkout:

```bash
git clone https://github.com/leslieraya555/FileSentinel-AI.git
cd FileSentinel-AI
```

If you already have the project, open its existing main directory instead.

### 2. Install Backend Dependencies

From the main project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
```

### 3. Start the Backend

From the main project directory:

```bash
.venv/bin/python -m uvicorn backend.main:app --reload --port 8000
```

Leave this terminal running. This is the backend terminal.

Open the interactive API documentation:

[http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Start the Frontend

Open another terminal in the main project directory:

```bash
cd frontend
npm install
VITE_API_BASE_URL="http://localhost:8000" npm run dev -- --port 5173 --strictPort
```

Leave this terminal running. This is the frontend terminal.

Open the dashboard:

[http://localhost:5173](http://localhost:5173)

These URLs work while the corresponding local services are running.

### 5. Generate Simulated Events

Open a third terminal in the main project directory:

```bash
.venv/bin/python scripts/test_simulation.py
```

The simulation appends synthetic records to `data/events.csv`. It includes normal activity and bursts intended to exercise the detection rules.

The script generates event records; it does not perform the described file operations on real files.

Refresh the dashboard to inspect event counts and alerts. Repeated runs add more records.

The backend must be reading `data/events.csv` to display these simulated records. If it is reading a saved verification log, restart it with the standard backend command first.

## Run the Linux Monitoring Agent

Run these commands inside Linux, starting from the main project directory:

```bash
make -C agent
mkdir -p watch_folder data
./agent/monitor watch_folder data/events.csv
```

Leave the monitoring terminal running.

In another Linux terminal, open the same project directory and perform file operations inside `watch_folder`.

See the [agent README](agent/README.md) for detailed setup, file-operation tests, and troubleshooting.

The backend must read the event CSV produced by the agent to display those events.

## Configuration

| Variable | Used by | Purpose |
| --- | --- | --- |
| `FILESENTINEL_EVENTS_FILE` | Backend | Selects the event CSV to read |
| `FILESENTINEL_ALLOWED_ORIGINS` | Backend | Sets a comma-separated list of allowed frontend origins |
| `VITE_API_BASE_URL` | Frontend | Sets the backend API base URL |

An origin includes the protocol, hostname or IP address, and port.

For example:

```text
http://localhost:5173
http://192.168.252.2:5173
```

Set these variables before starting the corresponding service. Restart the service after changing its configuration.

## Choose an Event Log

Run one backend instance per port. Stop the existing backend with **Control + C** before starting it with another event file.

### Default Event Log

The standard backend command uses `data/events.csv`:

```bash
.venv/bin/python -m uvicorn backend.main:app --reload --port 8000
```

### Saved Linux Verification Log

To display the archived Linux verification records, run this command from the main project directory:

```bash
FILESENTINEL_EVENTS_FILE="$PWD/docs/verification/linux-agent-verification-20261012.csv" \
.venv/bin/python -m uvicorn backend.main:app --reload --port 8000
```

Refresh the dashboard to inspect the saved records.

### Event Log Copied from a Linux VM

If the agent runs inside a Linux VM and the backend runs on the Mac, transfer the event CSV into the Mac project.

For example, after copying it to `data/live-events.csv`, run:

```bash
FILESENTINEL_EVENTS_FILE="$PWD/data/live-events.csv" \
.venv/bin/python -m uvicorn backend.main:app --reload --port 8000
```

Refresh the dashboard to display the copied records.

A manually copied CSV is a snapshot. New events captured in the VM require another transfer before they appear on the Mac dashboard.

To return to `data/events.csv`, stop the backend and restart it with the standard backend command.

## Verified Multipass VM Setup

This setup runs the backend and frontend inside a Linux VM while the browser runs on the Mac.

The verified setup uses:

- Multipass VM: `memorymedic`
- Project directory inside the VM: `~/filesentinel-verification-20261012`
- Backend port: `8001`
- Frontend port: `5173`

These commands assume the VM already exists and the project dependencies are installed inside it.

For another installation, adjust the VM name and project directory. Complete the backend dependency installation and frontend `npm install` inside the VM checkout before starting these services.

### 1. Start the VM and Check Its Address

Run these commands in a Mac terminal:

```bash
multipass start memorymedic
multipass info memorymedic
```

Note the VM's IPv4 address.

The startup commands below select the first address returned by `hostname -I` inside the VM.

### 2. Start the Backend

Run this command in a Mac terminal:

```bash
multipass exec memorymedic -- bash -lc '
cd "$HOME/filesentinel-verification-20261012" &&
fs_vm_ip=$(hostname -I) &&
fs_vm_ip=${fs_vm_ip%% *} &&
FILESENTINEL_ALLOWED_ORIGINS="http://$fs_vm_ip:5173,http://localhost:5173,http://127.0.0.1:5173" \
FILESENTINEL_EVENTS_FILE="$PWD/docs/verification/linux-agent-verification-20261012.csv" \
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
'
```

Leave this terminal running.

The allowed origins include the dashboard's VM address so the browser can request backend data.

This command displays the saved Linux verification CSV. To display ongoing agent activity, point `FILESENTINEL_EVENTS_FILE` to the CSV being updated by the agent.

### 3. Start the Frontend

Open another Mac terminal and run:

```bash
multipass exec memorymedic -- bash -lc '
cd "$HOME/filesentinel-verification-20261012/frontend" &&
fs_vm_ip=$(hostname -I) &&
fs_vm_ip=${fs_vm_ip%% *} &&
VITE_API_BASE_URL="http://$fs_vm_ip:8001" \
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
'
```

Leave this terminal running.

`VITE_API_BASE_URL` points the dashboard to the backend inside the VM.

### 4. Open the Application

The verified VM used `192.168.252.2`. Replace this address with the current IPv4 address reported by `multipass info`.

| Page | Example address |
| --- | --- |
| Dashboard | http://192.168.252.2:5173/ |
| API documentation | http://192.168.252.2:8001/docs |
| Health check | http://192.168.252.2:8001/health |

When browsing from the Mac, use the VM's address. `localhost` refers to the Mac itself.

If a service is already running, stop it in its existing terminal with **Control + C** before starting a replacement on the same port.

## Automated Tests

From the main project directory:

```bash
.venv/bin/python -m pytest "Automated tests" -q
```

If pytest is not installed:

```bash
.venv/bin/python -m pip install pytest
```

Then run the test command again.

The recorded local test run on October 1, 2026 completed with **12 passed and 2 dependency deprecation warnings**.

A successful GitHub Actions run was observed on October 13, 2026 for commit `57ba7e3`.

[View GitHub Actions](https://github.com/leslieraya555/FileSentinel-AI/actions)

## Frontend Production Build

From the main project directory:

```bash
cd frontend
npm run build
```

The build generates production assets in `frontend/dist/`.

The recorded build on October 13, 2026 completed successfully. This verifies that the frontend compiled for production.

## Verification Results

| Check | Observed result |
| --- | --- |
| Local automated tests | 12 passed in the recorded local run |
| GitHub Actions | Successful workflow run observed for commit `57ba7e3` on October 13, 2026 |
| Frontend production build | `npm run build` completed successfully on October 13, 2026 |
| Synthetic event simulation | Events appeared on the dashboard |
| Behavioral detection rules | Simulation produced four rule alerts |
| Linux agent compilation | Compiled successfully in a Linux VM |
| Real file activity | CREATE, MODIFY, DELETE, ACCESS, and RENAME were captured |
| Rename handling | One rename produced RENAMED_FROM and RENAMED_TO records |
| Backend and dashboard integration | Displayed six saved Linux verification records with API HEALTHY status |
| Verification-log rule assessment | Zero rule alerts |
| Verification-log ML assessment | Anomaly assessment displayed with a score of 73/100 |
| Saved model evaluation | Synthetic validation metrics were reviewed |
| README screenshots | All four embedded images were confirmed to display on GitHub |

These results describe the recorded local verification and observed CI run. They do not establish real-world detection accuracy.

Check GitHub Actions for the status of newer commits.

## Model Training and Evaluation

### Train the Model

From the main project directory:

```bash
.venv/bin/python ml/train_model.py
```

The training script:

- Uses a fixed random seed for reproducible dataset generation and fitting.
- Fits an Isolation Forest model on synthetic normal activity.
- Evaluates it using separate synthetic normal and attack-like examples.
- Writes the model to `ml/model.pkl`.
- Writes validation metrics and metadata to `ml/model_metadata.json`.

Running training overwrites these artifacts. Restart the backend after replacing its model.

### Inspect the Saved Metadata

From the main project directory:

```bash
.venv/bin/python -m json.tool ml/model_metadata.json
```

[View the saved model metadata](ml/model_metadata.json)

### Recorded Synthetic Validation Results

The metadata reviewed on October 13, 2026 records a training run from October 12, 2026.

| Setting | Recorded value |
| --- | --- |
| Algorithm | Isolation Forest |
| Random seed | 42 |
| Training rows | 1,500 |
| Validation rows | 600 |

The recorded input features are:

- `modify_count`
- `delete_count`
- `rename_count`
- `create_count`
- `access_count`
- `events_per_second`

| Metric | Recorded result |
| --- | ---: |
| Precision | 97.72% |
| Recall | 100% |
| F1 score | 98.85% |
| False-positive rate | 2.33% |

These results apply to the synthetic validation data used in that run.

They do not establish real-world detection accuracy. Model behavior requires further evaluation with representative file-system activity.

The dashboard's displayed anomaly score is separate from these evaluation metrics.

## API Endpoints

Open `/docs` on the running backend for interactive documentation and request parameters.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Backend home endpoint |
| GET | `/health` | Backend health status |
| GET | `/events` | Event records |
| GET | `/stats` | Activity statistics |
| GET | `/alerts/rules` | Behavioral rule alerts |
| GET | `/alerts/ml` | Machine-learning assessment |
| GET | `/overview` | Combined dashboard data |

## Troubleshooting

### A Port Is Already in Use

An existing process may already be running the service.

Stop that service in its existing terminal with **Control + C** before starting another instance on the same port.

The local setup uses backend port `8000`. The verified VM setup uses backend port `8001`. Both frontend examples use port `5173`.

### Dashboard Cannot Connect to the API

Confirm that:

- The backend terminal shows successful startup.
- The frontend is using the correct backend address and port.
- The API documentation page opens in the browser.
- Browser and backend logs do not show connection errors.

For the local setup, the frontend API address is:

```text
http://localhost:8000
```

For the verified VM setup, the frontend API address was:

```text
http://192.168.252.2:8001
```

Use the VM's current IP address when accessing its services from the Mac.

Set `VITE_API_BASE_URL` before starting the frontend. Restart the frontend after changing this value.

### Browser Reports a CORS Error

The backend's allowed origins must include the exact frontend origin, including its protocol, hostname or IP address, and port.

Use `FILESENTINEL_ALLOWED_ORIGINS` to configure a comma-separated list of allowed origins.

When accessing the dashboard through a VM IP address, include that dashboard origin and restart the backend.

### Expected Events Do Not Appear

Confirm that:

- The agent was running when the file operation occurred.
- The operation occurred inside the monitored directory.
- The event was recorded in the CSV.
- The backend is reading the intended CSV.
- A new transfer was completed if using the VM snapshot workflow.

A backend reading the archived verification CSV continues to display that saved data.

Refresh the dashboard after checking the event data.

### The Agent Does Not Compile on macOS

Compile and run the agent inside Linux.

The Linux inotify headers are not available natively on macOS.

### README Images Do Not Display

Confirm that image filenames and folder paths match the Markdown links exactly, including capitalization.

Project screenshots are stored under:

```text
docs/images-filesentinel/
```

Commit and push the image files together with the README changes.

### Git Says “Nothing to Commit”

Save the edited file in VS Code before running the Git commands.

If Git still reports a clean working tree, the saved content may already match the latest commit.

## Limitations

- The monitoring agent requires Linux.
- It watches one directory without recursively monitoring subdirectories.
- Events are captured only while the agent is running.
- Manual CSV transfer does not provide continuous synchronization.
- Saved verification logs represent recorded activity.
- Synthetic training data requires calibration against representative activity.
- An anomaly or rule alert is a reason to investigate, not proof of malware.
- Displayed risk scores are not validated probabilities of infection.
- The project does not automatically block processes or recover deleted files.

## Author

**Leslie Raya**

- [GitHub profile](https://github.com/leslieraya555)
- [Project repository](https://github.com/leslieraya555/FileSentinel-AI)