# Multi-stage build for production-ready AI Agent

# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

LABEL maintainer="team@aiagent.com"
LABEL description="Advanced AI Agent with Memory and Learning"
LABEL version="0.1.0"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agent

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=agent:agent agent/ ./agent/
COPY --chown=agent:agent examples/ ./examples/
COPY --chown=agent:agent setup.py ./
COPY --chown=agent:agent README.md ./

# Create data directories
RUN mkdir -p /app/data/memory /app/logs && \
    chown -R agent:agent /app/data /app/logs

# Switch to non-root user
USER agent

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENT_ENV=production \
    AGENT_LOG_LEVEL=INFO \
    AGENT_MEMORY_PATH=/app/data/memory

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from agent.core.agent import AdvancedAgent; print('healthy')" || exit 1

# Volume for persistent data
VOLUME ["/app/data", "/app/logs"]

# Expose port (if needed for API)
EXPOSE 8000

# Default command
CMD ["python", "-m", "agent.cli"]
