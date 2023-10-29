import functools
import inspect
import logging
import os
import threading
import uuid

import flask

logging.basicConfig(level=logging.INFO,
                    # filename='/var/log/raspiot/raspiot-server.log',
                    format='%(asctime)s %(levelname)s [pid:%(process)d] [tid:%(thread)d] %(message)s')


def log_decorator(func):
    def get_request_id():
        req_id = flask.has_request_context() and flask.g.get('request_id')
        req_id = req_id or (hasattr(threading.current_thread(), 'request_id') and threading.current_thread().request_id)
        if not req_id:
            req_id = str(uuid.uuid4())
            threading.current_thread().request_id = req_id

        return req_id

    @functools.wraps(func)
    def wrapper(msg, *args, **kwargs):
        request_id = get_request_id()
        frame = inspect.currentframe().f_back
        filename = os.path.basename(inspect.getframeinfo(frame, context=1).filename)
        lineno = inspect.getframeinfo(frame, context=1).lineno
        func_name = frame.f_code.co_name
        extra_info = '[%(filename)s:%(lineno)d] [%(func_name)s] [%(request_id)s] ' % {
            'filename': filename, 'lineno': lineno, 'func_name': func_name, 'request_id': request_id}

        msg = extra_info + msg
        func(msg, *args, **kwargs)
    return wrapper


debug = log_decorator(logging.debug)
info = log_decorator(logging.info)
warning = log_decorator(logging.warning)
error = log_decorator(logging.error)
exception = log_decorator(logging.exception)
