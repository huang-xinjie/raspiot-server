from datetime import datetime, timedelta

import log


def wrap_and_log_exception(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.exception(f'occur exception while exec {func.__name__}: {e}')

    return wrapped


def is_exceeded(date_time, delta):
    current_time = datetime.now()
    time_diff = current_time - date_time
    return time_diff > timedelta(seconds=delta)
