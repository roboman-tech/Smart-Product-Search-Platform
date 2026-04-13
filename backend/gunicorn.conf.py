# Gunicorn configuration for production VPS deployment.
# Run with: gunicorn -c gunicorn.conf.py ecommerce.wsgi:application

import multiprocessing

# Bind to all interfaces on port 8000; nginx reverse-proxies from 443 → 8000.
bind = "127.0.0.1:8000"

# 2-4 workers is typical for a small VPS (adjust to CPU count).
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Kill and restart a worker after this many requests to prevent memory leaks.
max_requests = 1000
max_requests_jitter = 100

# Seconds to wait for a request before timing out.
timeout = 60
keepalive = 5

# Log to stdout/stderr (systemd/journald will capture them).
errorlog = "-"
accesslog = "-"
loglevel = "info"
