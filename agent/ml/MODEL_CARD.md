FileSentinel AI Model Card

Author: Leslie Raya
Model: Isolation Forest anomaly detector

Intended use

The model prioritizes short windows of unusual file-system activity for analyst review. Input features summarize creates, modifications, deletions, renames, accesses, and event throughput during a ten-second window.

Training and evaluation

The training pipeline generates a reproducible normal-activity baseline with a fixed random seed. Separately generated ransomware-like bursts are used for validation only. Running python3 -m ml.train_model records current evaluation results in model_metadata.json.

Interpretation

A negative Isolation Forest decision value is anomalous.

The API maps the decision value to a bounded, human-readable risk score.

Feature evidence is returned with every successful prediction.

An anomaly is an investigation signal, not a malware verdict.

Limitations

Synthetic activity cannot represent every workstation, server, or business workflow.

Software builds, backups, updates, migrations, and archive extraction may resemble attacks.

The current features do not identify the responsible process, user, file entropy, or content.

Production use requires representative baselines, privacy review, drift monitoring, and analyst feedback.

Appropriate next evaluation

Split real telemetry by host and time, measure precision/recall at the incident level, compare against transparent rule baselines, and report false-positive rates separately for workstations, build systems, file servers, and database hosts.