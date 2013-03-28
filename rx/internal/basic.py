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
    raise err

# Errors
sequenceContainsNoElements = 'Sequence contains no elements.'
argumentOutOfRange = 'Argument out of range'
objectDisposed = 'Object has been disposed'

def checkDisposed(self):
    if (self.is_disposed):
        raise Excdeption(object_isposed)