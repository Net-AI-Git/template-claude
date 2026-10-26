# Splunk SPL Queries — <PROJECT_DISPLAY_NAME> Health Alerts

These are the Splunk alert queries that fire when any dependency health-check raises in one of the microservices. Each query covers BOTH `/applicative-health-check` and `/redis-queues-check` failures because all health-check probes live inside the repos/services that perform the actual probe and emit ERROR events with `process` set to the calling function name (`is_healthy`, `is_healthy_*`).

All queries assume:
- `index="<SPLUNK_INDEX>"` — the Splunk index where the apps log
- Health-check ERRORs are emitted by `splunk_repository.py` via `SplunkRepository.log_event(...)`. The `process` field is auto-detected from the calling function name.

> **Important**: Validate the `index` name with the actual production Splunk setup before publishing the alerts.

---

## Alert — `<ALERT_NAME>`

**Trigger**: any health-check ERROR event from `<microservice_slug>` in the last 15 minutes.

```spl
index="<SPLUNK_INDEX>" sourcetype="<SPLUNK_SOURCETYPE>" earliest=-15m
| spath path=process output=proc_name
| spath path=status output=evt_status
| search proc_name="is_healthy*" evt_status="ERROR"
| spath path=content.error output=error
| stats latest(_time) as last_failure latest(error) as last_error count by proc_name
| where count > 0
| eval last_failure=strftime(last_failure, "%Y-%m-%d %H:%M:%S")
| sort -count
```

**Alert condition**: trigger if `count >= 1` for any row.

---

## Bonus Alert (optional, recommended) — Application Down

Detects when a microservice has not produced **any** logs in 15 minutes — indicating the app itself is down (not just one of its dependencies).

```spl
| tstats count where index="<SPLUNK_INDEX>" sourcetype IN ("<SPLUNK_SOURCETYPE>", ...) earliest=-15m by sourcetype
| append [
    | makeresults
    | eval sourcetype=split("<SPLUNK_SOURCETYPE>,...", ",")
    | mvexpand sourcetype
    | eval count=0
    | fields sourcetype count
]
| stats max(count) as count by sourcetype
| where count=0
```

**Alert condition**: trigger if any row remains.

---

## Sample log structure (what the queries are reading)

Successful Oracle check (FINISHED event emitted by `OracleRepository.is_healthy*`):
```json
{
  "status": "FINISHED",
  "level": "INFO",
  "process": "is_healthy",
  "content": {},
  "flow_id": "9b5c-..."
}
```

Successful Redis queue check (FINISHED event emitted by `RedisRepository.is_healthy`):
```json
{
  "status": "FINISHED",
  "level": "INFO",
  "process": "is_healthy",
  "content": {
    "queue_id": "<REDIS_QUEUE_CONST_NAME>",
    "queue_depth": 0
  },
  "flow_id": "9b5c-..."
}
```

Failed check (ERROR event emitted by the repo / azure_healthcheck_service — the probe catches the exception internally, logs it, and returns `(False, error_message)`):
```json
{
  "status": "ERROR",
  "level": "ERROR",
  "process": "is_healthy",
  "content": {
    "error": "ConnectionError('Cannot connect to redis-host:6379')",
    "queue_id": "<REDIS_QUEUE_CONST_NAME>"
  },
  "flow_id": "9b5c-..."
}
```

Endpoint summary (one per `/monitor/*` call, emitted by `routes/monitor.py`):
```json
{
  "status": "FINISHED",
  "level": "INFO",
  "process": "applicative_health_check",
  "content": {
    "results_count": 3
  },
  "flow_id": "9b5c-..."
}
```
