import os

bind = "0.0.0.0:8000"
workers = 1 + os.cpu_count() # Also could multiply by * 2
timeout = 30
graceful_timeout = 30
accesslog = "-"
errorlog = "-"