from datetime import datetime

# Defaults
def noop():
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
    raise Exception(err)

# Errors
SEQUENCE_CONTAINS_NO_ELEMENTS = "Sequence contains no elements"
ARGUMENT_OUT_OF_RANGE = "Argument out of range"
OBJECT_IS_DISPOSED = "Object has been disposed"
