import gevent.monkey
gevent.monkey.patch_all()

# rest of your gunicorn config
workers = 1
bind = "0.0.0.0:10000"
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"