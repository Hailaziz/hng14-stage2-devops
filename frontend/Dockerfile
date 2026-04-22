# Stage 1: Builder - install dependencies
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev

# Stage 2: Final image
FROM node:18-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application code with correct ownership
COPY --chown=appuser:appgroup app.js .
COPY --chown=appuser:appgroup views/ ./views/
COPY --chown=appuser:appgroup package.json .

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
