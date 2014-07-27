import six

class ExtensionMethod(type):
    def __new__(cls, name, bases, namespace):
        assert len(bases) == 1, "Exactly one base class required"
        base = bases[0]
        for name, value in six.iteritems(namespace):
            if name == "__init__":
                base.initializers.append(value)

            if not name.startswith("__"):
                setattr(base, name, value)
        return base
