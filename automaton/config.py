import multiprocessing

worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
keepalive = 2
timeout = 10
graceful_timeout = 10