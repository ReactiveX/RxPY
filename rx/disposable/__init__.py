from rx.internal import noop
from rx.core import typing

from .anonymousdisposable import AnonymousDisposable
from .booleandisposable import BooleanDisposable
from .compositedisposable import CompositeDisposable
from .singleassignmentdisposable import SingleAssignmentDisposable
from .multipleassignmentdisposable import MultipleAssignmentDisposable
from .serialdisposable import SerialDisposable
from .refcountdisposable import RefCountDisposable
from .scheduleddisposable import ScheduledDisposable

def empty() -> typing.Disposable:
    return AnonymousDisposable(noop)

def create(action) -> typing.Disposable:
    return AnonymousDisposable(action)
