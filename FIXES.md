# FIXES.md — Bug Report & Resolutions

## BUG 1 — `api/main.py` line 6: Hardcoded `localhost` for Redis host
**Problem:** `redis.Redis(host="localhost")` hardcodes the Redis host. Inside a Docker container, `localhost` refers to the container itself, not the Redis service. This causes a connection failure at runtime.
**Fix:** Changed to `host=os.getenv("REDIS_HOST", "redis")` so the host is read from an environment variable, defaulting to `redis` (the Docker Compose service name).

## BUG 2 — `api/main.py` line 6: Redis password environment variable never used
**Problem:** `api/.env` defines `REDIS_PASSWORD` but the Redis client in `main.py` never reads or passes it. Redis would reject all connections if configured with a password.
**Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to the Redis client constructor.

## BUG 3 — `api/.env`: Real secret committed to repository
**Problem:** `api/.env` containing `REDIS_PASSWORD=supersecretpassword123` was committed to the repository. This exposes credentials in version control history.
**Fix:** Removed `api/.env` from git tracking with `git rm --cached api/.env`. Added `.env` and `*.env` to `.gitignore`. Created `.env.example` with placeholder values as the reference template.

## BUG 4 — `worker/worker.py` line 5: Hardcoded `localhost` for Redis host
**Problem:** Same as BUG 1 — `redis.Redis(host="localhost")` will fail inside a container.
**Fix:** Changed to `host=os.getenv("REDIS_HOST", "redis")`.

## BUG 5 — `worker/worker.py` line 5: Redis password environment variable never used
**Problem:** Same as BUG 2 — the worker never passes the Redis password, causing rejected connections.
**Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to the Redis client constructor.

## BUG 6 — `worker/worker.py`: No graceful shutdown on SIGTERM
**Problem:** Docker sends SIGTERM when stopping a container. Without a signal handler, the worker is force-killed after a timeout, potentially corrupting in-progress jobs.
**Fix:** Added `signal.signal(signal.SIGTERM, handle_signal)` and `signal.signal(signal.SIGINT, handle_signal)` with a `running` flag that allows the current job to finish before the process exits.

## BUG 7 — `worker/worker.py`: No `if __name__ == "__main__"` guard
**Problem:** All worker logic executed at import time. Importing this module for unit testing would immediately start an infinite loop.
**Fix:** Wrapped the main loop in `if __name__ == "__main__":` so it only runs when executed directly.

## BUG 8 — `worker/worker.py`: Redis responses not decoded
**Problem:** Without `decode_responses=True`, Redis returns raw bytes. `job_id.decode()` was called manually but inconsistently — missing in other places would cause type errors.
**Fix:** Added `decode_responses=True` to the Redis client so all responses are automatically decoded to strings.

## BUG 9 — `api/main.py`: Redis responses not decoded
**Problem:** Same as BUG 8 — `status.decode()` was called manually in `get_job()` but this fails if `decode_responses` is not set and other fields are added later.
**Fix:** Added `decode_responses=True` to the Redis client, removed manual `.decode()` calls.

## BUG 10 — `api/main.py` & `worker/worker.py`: Mismatched Redis queue name
**Problem:** `api/main.py` pushed jobs to queue named `"job"` (singular) while `worker/worker.py` consumed from `"job"` as well — however this is inconsistent naming that causes silent failures if either is changed independently.
**Fix:** Standardised queue name to `"jobs"` (plural) in both files.

## BUG 11 — `api/requirements.txt`: No version pinning
**Problem:** `fastapi`, `uvicorn`, and `redis` had no version constraints. Unpinned dependencies can silently break when new versions with breaking changes are released.
**Fix:** Pinned to `fastapi==0.111.0`, `uvicorn==0.29.0`, `redis==5.0.4`.

## BUG 12 — `worker/requirements.txt`: No version pinning
**Problem:** `redis` had no version constraint.
**Fix:** Pinned to `redis==5.0.4`.

## BUG 13 — `frontend/app.js` line 5: Hardcoded `localhost` for API URL
**Problem:** `const API_URL = "http://localhost:8000"` hardcodes the API address. Inside a container, this resolves to the frontend container itself, not the API service.
**Fix:** Changed to `const API_URL = process.env.API_URL || "http://api:8000"` so it reads from an environment variable.

## BUG 14 — `api/main.py`: No `/health` endpoint
**Problem:** Docker HEALTHCHECK requires an HTTP endpoint to probe. Without one, container health cannot be verified, breaking the `depends_on: condition: service_healthy` requirement in Docker Compose.
**Fix:** Added `GET /health` endpoint that pings Redis and returns `{"status": "healthy"}`.

## BUG 15 — `frontend/app.js`: No `/health` endpoint
**Problem:** Same as BUG 14 — frontend had no health endpoint for Docker HEALTHCHECK.
**Fix:** Added `GET /health` endpoint returning `{"status": "healthy"}`.
