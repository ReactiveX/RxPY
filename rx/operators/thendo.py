from rx.core.typing import Mapper
from rx.core import ObservableBase
from rx.joins import Pattern


def then_do(source: ObservableBase, mapper: Mapper) -> ObservableBase:
    """Matches when the observable sequence has an available value and
    projects the value.

    mapper -- Mapper that will be invoked for values in the source
        sequence.

    Returns Plan that produces the projected values, to be fed (with
    other plans) to the when operator.
    """

    return Pattern([source]).then_do(mapper)

