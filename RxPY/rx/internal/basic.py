from datetime import datetime

# Defaults
def noop(*args, **kw):
   pass

def identity(x):
    return x

def default_now():
    return datetime.utcnow()

def default_comparer(x, y):
    return x == y

def default_sub_comparer(x, y):
    return x - y

def default_key_serializer(x):
    return str(x)

def default_error(err):
    if isinstance(err, BaseException):
        raise err
    else:
        raise Exception(err)


