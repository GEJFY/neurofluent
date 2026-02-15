"""Gunicorn production configuration for FluentEdge Backend"""

import multiprocessing
import os

# Worker settings
workers = int(
    os.getenv("GUNICORN_WORKERS", min(2 * multiprocessing.cpu_count() + 1, 4))
)
worker_class = "uvicorn.workers.UvicornWorker"
worker_tmp_dir = "/dev/shm"

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Timeout (LLM API calls can take up to 60s)
timeout = 120
graceful_timeout = 30
keepalive = 5

# Worker lifecycle (memory leak prevention)
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Preload for memory sharing
preload_app = True

# Proxy
forwarded_allow_ips = "*"
