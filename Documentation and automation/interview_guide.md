FileSentinel AI Interview Guide

Author: Leslie Raya

Thirty-second explanation

“I built FileSentinel AI to connect systems programming, backend engineering, machine learning, and security analysis. A C agent captures Linux file events with inotify. FastAPI validates and aggregates the telemetry. An explainable rule engine catches known bulk-operation patterns, while an Isolation Forest identifies behavior outside a learned baseline. A React dashboard shows the event evidence, risk score, and recommended response.”

Strong technical points

Rule-based and ML detection complement each other: rules are transparent for known patterns; anomaly detection can surface unfamiliar behavior.

The model trains only on baseline observations and evaluates against separate normal and attack-like scenarios.

Feature order is an explicit contract shared by training and inference.

CSV fields are escaped in the C agent, preventing commas, quotes, or newlines in filenames from corrupting telemetry.

The dashboard calls /overview so every displayed value comes from one consistent event snapshot.

Tests cover malformed data, threshold behavior, model feature extraction, and public API contracts.

Questions to expect

Why Isolation Forest?

It supports unlabeled baseline data, isolates rare observations efficiently, and provides a decision score. It is a practical prototype choice when confirmed attack labels are limited.

What causes false positives?

Legitimate bulk operations such as software updates, backups, builds, data migrations, and archive extraction. Host-specific baselines, process context, allowlists, and analyst feedback would reduce noise.

Why is synthetic training a limitation?

Synthetic distributions demonstrate the pipeline but cannot capture the diversity of production workloads. The model metadata states this clearly. A deployment would collect privacy-reviewed baseline telemetry across host roles, split data by time and host, and monitor drift.

How would a bank use it?

Agents would send signed, encrypted events to a central ingestion service rather than a local CSV. Detection results would flow to a SIEM and case-management system. Controls would include strong device identity, least-privilege roles, immutable audit logs, retention policies, regional data controls, and human review before containment.

What would you build next?

Process attribution using eBPF or fanotify, a durable event pipeline, authenticated agents, file-entropy features, host-specific model calibration, analyst feedback, and incident timelines.