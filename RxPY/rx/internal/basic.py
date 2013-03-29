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

def default_key_sSerializer(x):
    return str(x)

def default_error(err):
    raise Exception(err)

# Errors
sequence_contains_no_elements = 'Sequence contains no elements.'
argument_out_of_range = 'Argument out of range'
object_isposed = 'Object has been disposed'

def checkDisposed(self):
    if (self.is_disposed):
        raise Exception(object_isposed)