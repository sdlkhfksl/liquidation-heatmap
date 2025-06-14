#############################
# Multi-stage Dockerfile for
# Liquidation Heatmap Streamlit App
#############################

# ---- 1st Stage: Builder ----
FROM python:3.11-slim AS builder

# Set working dir and copy dependencies
WORKDIR /app
COPY requirements.txt .

# Install build tools and Python deps into /install
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc g++ \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*


# ---- 2nd Stage: Final Image ----
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home appuser
WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local
# Copy application source
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check on custom route
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl --fail http://localhost:8501/healthz || exit 1

# Switch to non-root user
USER appuser

# Run Streamlit in headless mode, with custom health route
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.healthCheckRoute=/healthz"]
