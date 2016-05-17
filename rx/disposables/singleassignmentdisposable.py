from .booleandisposable import BooleanDisposable


class SingleAssignmentDisposable(BooleanDisposable):
    """Represents a disposable resource which only allows a single assignment
    of its underlying disposable resource. If an underlying disposable resource
    has already been set, future attempts to set the underlying disposable
    resource will throw an Error."""

    def __init__(self):
        super(SingleAssignmentDisposable, self).__init__(True)
