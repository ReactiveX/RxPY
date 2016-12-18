import rx
from rx.testing import marbles

def test_alias():
    assert rx.Observable.from_string == rx.Observable.from_marbles

def test_from_to_marbles():
    for marbles in '0-1-(10)-|', '0|', '(10)(20)|':
        stream = rx.Observable.from_string(marbles)
        assert stream.to_blocking().to_marbles() == marbles



