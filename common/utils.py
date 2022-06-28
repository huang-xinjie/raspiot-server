def wrap_and_log_exception(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print('occur exception while exec %(func)s: %(reason)s' %
                  {'func': func.__name__, 'reason': e})

    return wrapped
