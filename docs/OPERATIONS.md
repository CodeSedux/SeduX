# Operations Runbook

## Setup and Validation

```bash
cp .env.example .env
python -m pip install '.[dev]'
python -m unittest discover -s tests -v
docker compose --profile cpu up --build
```

Use `docker compose --profile gpu up gpu-worker` only on a host with the NVIDIA container runtime. Validate `/health`, `/readiness`, and `/metrics` before routing traffic.

## Backup and Restore

Create encrypted PostgreSQL backups with `pg_dump --format=custom`; snapshot model/config volumes separately. Test restores into an isolated database before each release. Redis is treated as rebuildable cache/queue state; durable task definitions remain in PostgreSQL.

### Backup command

```bash
export DATABASE_URL="postgresql://sedux:sedux@postgres:5432/sedux"
pg_dump --format=custom --dbname="$DATABASE_URL" --file="./backups/sedux-$(date +%Y%m%d-%H%M%S).dump" --verbose --clean --if-exists
```

### Restore validation

```bash
createdb sedux_restore
pg_restore --clean --if-exists --dbname=sedux_restore ./backups/sedux-<timestamp>.dump
python -m unittest discover -s tests -v
```

### Deployment validation

```bash
python - <<'PY'
from shared.operations import validate_deployment_environment
required = {
    'SEDUX_ENV': 'production',
    'SEDUX_AUTH_SECRET': 'a-very-long-and-strong-secret-value-12345',
    'DATABASE_URL': 'postgresql://sedux:sedux@postgres:5432/sedux',
    'REDIS_URL': 'redis://redis:6379/0',
}
print(validate_deployment_environment(required))
PY
```

## Rollback

Retain the previous immutable image and migration backup. Stop ingress, roll application containers back first, and reverse a migration only when its matching down migration has been rehearsed. Otherwise restore the database backup, then rerun health and end-to-end checks.

### Rollback sequence

1. Freeze new deploy traffic and preserve current logs.
2. Revert the gateway and worker container image to the last known good tag.
3. Restore the database from the validated backup only if the release introduced incompatible schema changes.
4. Restart services with `docker compose --profile cpu up -d --no-deps gateway`.
5. Re-run `/health`, `/readiness`, and `/metrics` checks before traffic restoration.

## Incident Controls

Disable screen and home scopes first for suspected compromise. Rotate `SEDUX_AUTH_SECRET` and external credentials, revoke active sessions, preserve redacted audit logs, and restore service only after readiness and consent-path tests pass.