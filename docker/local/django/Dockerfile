# Build stage
FROM python:3.10-slim-bookworm as builder

WORKDIR /app

# Install system dependencies required for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim-bookworm as runtime

# Set environment variables
ENV APP_HOME=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH="/opt/venv/bin:$PATH"

WORKDIR $APP_HOME

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        netcat-openbsd \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash appuser

# Create directories with proper permissions
RUN mkdir -p $APP_HOME/staticfiles $APP_HOME/mediafiles && \
    chown -R appuser:appuser $APP_HOME

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Copy and fix entrypoint scripts
COPY --chown=appuser:appuser ./docker/local/django/entrypoint /entrypoint
COPY --chown=appuser:appuser ./docker/local/django/start /start
COPY --chown=appuser:appuser ./docker/local/django/celery/worker/start /start-celeryworker
COPY --chown=appuser:appuser ./docker/local/django/celery/flower/start /start-flower

# Fix line endings and make scripts executable
RUN sed -i 's/\r$//g' /entrypoint /start /start-celeryworker /start-flower && \
    chmod +x /entrypoint /start /start-celeryworker /start-flower

# Set ownership and permissions
RUN chown -R appuser:appuser $APP_HOME && \
    chmod -R 755 $APP_HOME && \
    chmod -R 755 /entrypoint /start /start-celeryworker /start-flower

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Expose port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/entrypoint"]