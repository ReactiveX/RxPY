import reactivex


def test_for_in_reusable_values_on_second_subscription() -> None:
    def mapper(value: int) -> reactivex.Observable[int]:
        return reactivex.just(value)

    source = reactivex.for_in([1, 2], mapper)
    first: list[int | str] = []
    second: list[int | str] = []

    source.subscribe(first.append, on_completed=lambda: first.append("done"))
    source.subscribe(second.append, on_completed=lambda: second.append("done"))

    assert first == [1, 2, "done"]
    assert second == [1, 2, "done"]
