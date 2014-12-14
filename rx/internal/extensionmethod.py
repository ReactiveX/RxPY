def extends(base):
    """Class decorator that extends base with methods from the decorated
    class.

    Keyword arguments:
    base -- Base class to extend with methods from cls

    Returns a function that takes the class to be decorated.
    """

    def inner(cls):
        """This function is returned by the outer extends()

        cls -- Class to be decorated
        """
        for name in dir(cls):
            value = getattr(cls, name)
            iscallable = callable(value)
            if iscallable and not name.endswith("__") or name == "__getitem__":
                if hasattr(value, "__func__") and value.__self__ != cls:
                    # For Py2 bound methods we need to take the function
                    setattr(base, name, value.__func__)
                else:
                    # classmethods, staticmethods, and Py3
                    setattr(base, name, value)
        return cls
    return inner
