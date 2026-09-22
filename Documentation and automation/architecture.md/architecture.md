Architecture and Security Decisions

Author: Leslie Raya

Data flow

The Linux agent receives kernel inotify events for one authorized directory.

The agent normalizes event categories, adds UTC timestamps, escapes CSV fields, and flushes each record.

The backend rejects malformed timestamps, unknown event categories, and incomplete schemas.

Rule and ML detectors analyze the same recent event window.

/overview returns aligned statistics, events, and alerts to the dashboard.

Trust boundaries

Boundary

Present control

Production requirement

Agent → store

CSV escaping and schema validation

Mutual authentication and encrypted ingestion

Store → API

Type normalization and malformed-row rejection

Database permissions, retention policy, and integrity controls

Browser → API

Explicit CORS origins and read-only methods

Authentication, authorization, TLS, and rate limiting

Model → analyst

Feature evidence and bounded risk score

Model registry, drift monitoring, and analyst feedback

Important tradeoffs

CSV makes the prototype easy to inspect but does not provide transactions, concurrency guarantees, or centralized retention.

inotify is efficient for local Linux monitoring but does not attach process identity and does not monitor recursively without registering additional watches.

Isolation Forest is appropriate for an unlabeled baseline, but an anomaly is not automatically malicious.

Anchoring the analysis window to the newest event enables repeatable offline demonstrations; a streaming deployment would use event-time windows and late-arrival handling.