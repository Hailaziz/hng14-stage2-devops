# --- Builder Stage ---
FROM python:3.11-alpine AS builder
# ... your builder steps (pip install, etc.) ...

# --- Final Stage ---
FROM python:3.11-alpine AS final

# 1. Patch OS vulnerabilities immediately
RUN apk update && apk upgrade --no-cache

# 2. Setup non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# ... the rest of your final stage instructions (COPY, USER, CMD, etc.)
