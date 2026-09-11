# FileSentinel AI

FileSentinel AI is an AI-powered Linux file-system security monitor.

It uses a C-based Linux agent to monitor file-system events, a Python machine learning model to detect abnormal behavior, a FastAPI backend to serve alerts, and a React dashboard to visualize security activity.

## Features

- C-based Linux file-system monitor
- File creation, modification, deletion, rename, and access tracking
- Rule-based suspicious activity detection
- ML-based anomaly detection with Isolation Forest
- FastAPI backend
- React dashboard
- Safe ransomware-like simulation script
- Docker Compose starter setup

## Tech Stack

- C
- Linux
- Python
- FastAPI
- scikit-learn
- pandas
- React
- Vite
- Docker
- CSV storage

## Project Structure

```text
FileSentinel-AI/
├── agent/
├── backend/
├── frontend/
├── data/
├── ml/
├── scripts/
├── README.md
├── .gitignore
└── docker-compose.yml