def extends(base):
    """Class decorator that extends base with methods from the decorated
    class.

    Keyword arguments:
    base -- Base class to extend with methods from cls
    needs_init -- If true, then init method of cls will be run by base init

    Returns a function that takes the class to be decorated.
    """

    def inner(cls):
        for name in dir(cls):
            value = getattr(cls, name)
            iscallable = callable(value)
            if iscallable and not name.endswith("__"):
                if hasattr(value, "__func__") and value.__self__ != cls:
                    # For normal methods we take the function
                    setattr(base, name, value.__func__)
                else:
                    # classmethods
                    setattr(base, name, value)
        return cls
    return inner
