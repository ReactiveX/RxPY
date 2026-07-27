"""Transformation operators mixin for Observable."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

from typing_extensions import TypeVarTuple, Unpack

from reactivex import typing
from reactivex.internal.utils import NotSet

if TYPE_CHECKING:
    from reactivex.observable import Observable

_T = TypeVar("_T", covariant=True)
_A = TypeVar("_A")
_B = TypeVar("_B")
_Ts = TypeVarTuple("_Ts")


class TransformationMixin(Generic[_T]):
    """Mixin providing transformation operators for Observable.

    This mixin adds operators that transform elements in various ways,
    including mapping, flattening, and accumulation.

    Generic over _T to preserve the Observable's element type and provide
    full type safety without Any types.
    """

    def _as_observable(self) -> Observable[_T]:
        """Cast mixin instance to Observable preserving type parameter.

        This is safe because this mixin is only ever used as part of the Observable
        class through multiple inheritance. At runtime, `self` in mixin methods will
        always be an Observable[_T] instance. The type checker cannot infer this
        because it analyzes mixins in isolation.

        Returns:
            The instance cast to Observable[_T] for type-safe method access.
        """
        return cast("Observable[_T]", self)

    def map(self, mapper: typing.Mapper[_T, _B]) -> Observable[_B]:
        """Map each element to a new value.

        Projects each element of an observable sequence into a new form by applying
        a transform function to each element.

        Examples:
            Fluent style:
            >>> result = source.map(lambda x: x * 2)
            >>> result = source.map(str)  # Transform int to str

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.map(lambda x: x * 2))

        Args:
            mapper: A transform function to apply to each source element.

        Returns:
            An observable sequence whose elements are the result of invoking
            the transform function on each element of the source.

        See Also:
            - :func:`map <reactivex.operators.map>`
            - :meth:`map_indexed`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.map(mapper))

    @overload
    def reduce(self, accumulator: typing.Accumulator[_T, _T]) -> Observable[_T]: ...

    @overload
    def reduce(
        self, accumulator: typing.Accumulator[_A, _T], seed: _A
    ) -> Observable[_A]: ...

    def reduce(
        self,
        accumulator: typing.Accumulator[_A, _T],
        seed: _A | type[NotSet] = NotSet,
    ) -> Observable[_T] | Observable[_A]:
        """Apply an accumulator function and return the final accumulated result.

        Applies an accumulator function over an observable sequence, returning the
        result of the aggregation as a single element in the result sequence.

        Examples:
            Fluent style:
            >>> result = source.reduce(lambda acc, x: acc + x)
            >>> result = source.reduce(lambda acc, x: acc + x, 0)
            >>> # Concatenate strings
            >>> result = source.reduce(lambda acc, x: acc + x, "")

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.reduce(lambda acc, x: acc + x))
            >>> result = source.pipe(ops.reduce(lambda acc, x: acc + x, 0))

        Args:
            accumulator: An accumulator function to be invoked on each element.
            seed: Optional initial accumulator value.

        Returns:
            An observable sequence containing a single element with the final
            accumulated value.

        See Also:
            - :func:`reduce <reactivex.operators.reduce>`
            - :meth:`scan`
        """
        from reactivex import operators as ops

        if seed is NotSet:
            return self._as_observable().pipe(ops.reduce(accumulator))
        # After the guard above, seed is guaranteed to be _A (not type[NotSet]).
        # Cast is needed because pyright doesn't narrow union types with `is` checks.
        seed_value = cast(_A, seed)
        return self._as_observable().pipe(ops.reduce(accumulator, seed_value))

    @overload
    def scan(self, accumulator: typing.Accumulator[_T, _T]) -> Observable[_T]: ...

    @overload
    def scan(
        self, accumulator: typing.Accumulator[_A, _T], seed: _A
    ) -> Observable[_A]: ...

    def scan(
        self,
        accumulator: typing.Accumulator[_A, _T],
        seed: _A | type[NotSet] = NotSet,
    ) -> Observable[_T] | Observable[_A]:
        """Apply an accumulator function and return each intermediate result.

        Applies an accumulator function over an observable sequence and returns
        each intermediate result. Similar to reduce, but emits the current
        accumulation after each element.

        Examples:
            Fluent style:
            >>> result = source.scan(lambda acc, x: acc + x)
            >>> result = source.scan(lambda acc, x: acc + x, 0)
            >>> result = source.scan(lambda acc, x: acc + [x], [])  # Collect into list

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.scan(lambda acc, x: acc + x))
            >>> result = source.pipe(ops.scan(lambda acc, x: acc + x, 0))

        Args:
            accumulator: An accumulator function to be invoked on each element.
            seed: Optional initial accumulator value.

        Returns:
            An observable sequence containing the accumulated values.

        See Also:
            - :func:`scan <reactivex.operators.scan>`
            - :meth:`reduce`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.scan(accumulator, seed))

    @overload
    def flat_map(self, mapper: typing.Mapper[_T, Observable[_B]]) -> Observable[_B]: ...

    @overload
    def flat_map(self, mapper: None = None) -> Observable[object]: ...

    def flat_map(
        self,
        mapper: typing.Mapper[_T, Observable[_B]] | None = None,
    ) -> Observable[_B]:
        """Transform elements into observables and flatten (also known as merge_map).

        Projects each element of an observable sequence to an observable sequence
        and merges the resulting observable sequences into one observable sequence.

        Examples:
            Fluent style:
            >>> result = source.flat_map(lambda x: rx.of(x, x * 2))
            >>> result = rx.of(rx.of(1, 2), rx.of(3, 4)).flat_map()  # Flatten

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.flat_map(lambda x: rx.of(x, x * 2)))

        Args:
            mapper: A transform function to apply to each element, or None to
                flatten nested observables.

        Returns:
            An observable sequence whose elements are the result of invoking the
            one-to-many transform function on each element of the input sequence
            and merging all the resulting sequences.

        See Also:
            - :func:`flat_map <reactivex.operators.flat_map>`
            - :meth:`concat_map`
            - :meth:`switch_map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.flat_map(mapper))

    def concat_map(self, project: typing.Mapper[_T, Observable[_B]]) -> Observable[_B]:
        """Transform and concatenate observables in order.

        Projects each source value to an observable which is merged in the output
        observable, in a serialized fashion waiting for each one to complete before
        merging the next.

        Examples:
            Fluent style:
            >>> result = source.concat_map(lambda x: rx.of(x, x * 2))
            >>> result = source.concat_map(lambda x: delayed_observable(x))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.concat_map(lambda x: rx.of(x, x * 2)))

        Args:
            project: A transform function to apply to each element.

        Returns:
            An observable sequence whose elements are the result of invoking the
            transform function on each element and concatenating all the sequences.

        See Also:
            - :func:`concat_map <reactivex.operators.concat_map>`
            - :meth:`flat_map`
            - :meth:`switch_map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.concat_map(project))

    def switch_map(self, project: typing.Mapper[_T, Observable[_B]]) -> Observable[_B]:
        """Transform and switch to the latest observable.

        Projects each source value to an observable which is merged in the output
        observable, emitting values only from the most recently projected observable.

        Examples:
            Fluent style:
            >>> result = source.switch_map(lambda x: rx.of(x, x * 2))
            >>> result = source.switch_map(lambda x: delayed_observable(x))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.switch_map(lambda x: rx.of(x, x * 2)))

        Args:
            project: A transform function to apply to each element.

        Returns:
            An observable sequence whose elements are the result of invoking the
            transform function on each element and merging only the most recent
            inner observable sequence.

        See Also:
            - :func:`switch_map <reactivex.operators.switch_map>`
            - :meth:`flat_map`
            - :meth:`concat_map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.switch_map(project))

    def map_indexed(
        self, mapper_indexed: typing.MapperIndexed[_T, _B] | None = None
    ) -> Observable[_B]:
        """Map each element to a new value with its index.

        Projects each element of an observable sequence into a new form by
        incorporating the element's index.

        Examples:
            Fluent style:
            >>> result = source.map_indexed(lambda x, i: f"{i}: {x}")
            >>> result = source.map_indexed(lambda x, i: x * i)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.map_indexed(lambda x, i: f"{i}: {x}"))

        Args:
            mapper_indexed: A transform function to apply to each element and
                its index. The function receives (value, index) and returns the
                transformed value.

        Returns:
            An observable sequence whose elements are the result of invoking
            the indexed transform function on each element of the source.

        See Also:
            - :func:`map_indexed <reactivex.operators.map_indexed>`
            - :meth:`map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.map_indexed(mapper_indexed))

    def flat_map_indexed(
        self, mapper_indexed: typing.MapperIndexed[_T, Observable[_B]] | None = None
    ) -> Observable[_B]:
        """Transform elements into observables and flatten, with index.

        Projects each element of an observable sequence to an observable sequence
        by incorporating the element's index, and merges the resulting observable
        sequences into one observable sequence.

        Examples:
            Fluent style:
            >>> result = source.flat_map_indexed(lambda x, i: rx.of(x, i))
            >>> result = source.flat_map_indexed(lambda x, i: fetch_data(x, i))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.flat_map_indexed(lambda x, i: rx.of(x, i)))

        Args:
            mapper_indexed: A transform function to apply to each element and its
                index. The function receives (value, index) and returns an Observable.

        Returns:
            An observable sequence whose elements are the result of invoking the
            indexed transform function on each element and merging all sequences.

        See Also:
            - :func:`flat_map_indexed <reactivex.operators.flat_map_indexed>`
            - :meth:`flat_map`
            - :meth:`map_indexed`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.flat_map_indexed(mapper_indexed))

    def flat_map_latest(
        self, mapper: typing.Mapper[_T, Observable[_B]]
    ) -> Observable[_B]:
        """Transform and flatten, canceling previous inner observables.

        Projects each element to an observable, merges the resulting observables,
        and emits only from the most recently projected observable.

        Examples:
            Fluent style:
            >>> result = source.flat_map_latest(lambda x: fetch_data(x))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.flat_map_latest(lambda x: fetch_data(x)))

        Args:
            mapper: A transform function to apply to each element.

        Returns:
            An observable sequence containing the merged results from the
            most recent inner observable.

        See Also:
            - :func:`flat_map_latest <reactivex.operators.flat_map_latest>`
            - :meth:`flat_map`
            - :meth:`switch_map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.flat_map_latest(mapper))

    def switch_map_indexed(
        self, mapper_indexed: typing.MapperIndexed[_T, Observable[_B]]
    ) -> Observable[_B]:
        """Transform and switch to latest observable, with index.

        Projects each element to an observable by incorporating the element's index,
        and emits values only from the most recently projected observable.

        Examples:
            Fluent style:
            >>> result = source.switch_map_indexed(lambda x, i: fetch_data(x, i))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(
            ...     ops.switch_map_indexed(lambda x, i: fetch_data(x, i))
            ... )

        Args:
            mapper_indexed: A transform function to apply to each element and its index.

        Returns:
            An observable sequence whose elements are the result of invoking the
            indexed transform function and switching to the most recent sequence.

        See Also:
            - :func:`switch_map_indexed <reactivex.operators.switch_map_indexed>`
            - :meth:`switch_map`
            - :meth:`flat_map_indexed`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.switch_map_indexed(mapper_indexed))

    @overload
    def starmap(self: TransformationMixin[_T]) -> Observable[_T]:
        """Identity overload when no mapper provided."""
        ...

    @overload
    def starmap(
        self: TransformationMixin[tuple[Unpack[_Ts]]],
        mapper: Callable[[Unpack[_Ts]], _B],
    ) -> Observable[_B]:
        """Typed overload with variadic generics."""
        ...

    def starmap(self, mapper: Any = None) -> Observable[Any]:
        """Unpack arguments from tuples and apply to mapper function.

        Projects each element of an observable sequence of tuples into a new form
        by unpacking the tuple as arguments to a function.

        Examples:
            Fluent style:
            >>> result = rx.of((1, 2), (3, 4)).starmap(lambda x, y: x + y)
            >>> result = rx.of(("a", 1), ("b", 2)).starmap(lambda s, n: s * n)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.starmap(lambda x, y: x + y))

        Args:
            mapper: A transform function that receives unpacked tuple elements.
                If not provided, returns the tuple unchanged.

        Returns:
            An observable sequence whose elements are the result of invoking
            the transform function with unpacked tuple arguments.

        See Also:
            - :func:`starmap <reactivex.operators.starmap>`
            - :meth:`map`
        """
        from reactivex import operators as ops

        # Cast is safe: The overloads above provide type safety for callers.
        # The implementation uses Any because variadic generics can't be
        # perfectly expressed in the implementation signature.
        source = cast("Observable[Any]", self._as_observable())
        return source.pipe(ops.starmap(mapper))

    @overload
    def starmap_indexed(
        self: TransformationMixin[tuple[Unpack[_Ts]]],
        mapper_indexed: Callable[[Unpack[_Ts], int], _B],
    ) -> Observable[_B]: ...

    @overload
    def starmap_indexed(self, mapper_indexed: None = None) -> Observable[Any]: ...

    def starmap_indexed(self, mapper_indexed: Any = None) -> Observable[Any]:
        """Unpack tuple arguments and apply to indexed mapper function.

        Projects each element of an observable sequence of tuples into a new form
        by unpacking the tuple as arguments to a function, with index.

        Examples:
            Fluent style:
            >>> result = rx.of((1, 2), (3, 4)).starmap_indexed(
            ...     lambda x, y, i: (x + y) * i
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.starmap_indexed(lambda x, y, i: (x + y) * i))

        Args:
            mapper_indexed: A transform function that receives unpacked tuple
                elements and the index.

        Returns:
            An observable sequence whose elements are the result of invoking
            the indexed transform function with unpacked tuple arguments.

        See Also:
            - :func:`starmap_indexed <reactivex.operators.starmap_indexed>`
            - :meth:`starmap`
            - :meth:`map_indexed`
        """
        from reactivex import operators as ops

        # Cast is safe: The overload above provides type safety for callers.
        # The implementation uses Any because variadic generics can't be
        # perfectly expressed in the implementation signature.
        source = cast("Observable[Any]", self._as_observable())
        return source.pipe(ops.starmap_indexed(mapper_indexed))

    def pluck(self, key: str) -> Observable[Any]:
        """Extract a property from each element.

        Returns an observable sequence of values corresponding to a property
        with the given name from all elements in the source sequence.

        Examples:
            Fluent style:
            >>> result = source.pluck("name")
            >>> result = rx.of({"x": 1}, {"x": 2}).pluck("x")

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.pluck("name"))

        Args:
            key: The property name to extract.

        Returns:
            An observable sequence of property values.

        See Also:
            - :func:`pluck <reactivex.operators.pluck>`
            - :meth:`pluck_attr`
            - :meth:`map`
        """
        from reactivex import operators as ops

        # Cast is safe: pluck expects Observable[dict[str, Any]] but
        # we have Observable[_T]. The fluent API allows calling this
        # on sequences of dictionaries.
        source: Observable[Any] = cast("Observable[Any]", self._as_observable())
        return ops.pluck(key)(source)

    def pluck_attr(self, attr: str) -> Observable[Any]:
        """Extract an attribute from each element.

        Returns an observable sequence of values corresponding to an attribute
        with the given name from all elements in the source sequence.

        Examples:
            Fluent style:
            >>> result = source.pluck_attr("name")
            >>> result = source.pluck_attr("value")

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.pluck_attr("name"))

        Args:
            attr: The attribute name to extract.

        Returns:
            An observable sequence of attribute values.

        See Also:
            - :func:`pluck_attr <reactivex.operators.pluck_attr>`
            - :meth:`pluck`
            - :meth:`map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.pluck_attr(attr))

    def expand(self, mapper: typing.Mapper[_T, Observable[_T]]) -> Observable[_T]:
        """Recursively expand observable sequences.

        Recursively projects each source value to an observable which is merged
        in the output observable.

        Examples:
            Fluent style:
            >>> result = rx.of(1).expand(
            ...     lambda x: rx.of(x + 1) if x < 10 else rx.empty()
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(
            ...     ops.expand(lambda x: rx.of(x + 1) if x < 10 else rx.empty())
            ... )

        Args:
            mapper: A transform function to apply to each element, returning an
                observable sequence.

        Returns:
            An observable sequence containing all values from the source and
            recursively expanded observables.

        See Also:
            - :func:`expand <reactivex.operators.expand>`
            - :meth:`flat_map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.expand(mapper))

    def exclusive(self) -> Observable[_T]:
        """Projects and merges observables exclusively.

        Projects each element of the source observable to an observable,
        emitting only from the first inner observable until it completes.

        Examples:
            Fluent style:
            >>> result = source_of_observables.exclusive()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.exclusive())

        Returns:
            An observable sequence containing elements from the first inner
            observable until completion, then the next, and so on.

        See Also:
            - :func:`exclusive <reactivex.operators.exclusive>`
            - :meth:`concat_map`
        """
        from reactivex import operators as ops

        # Cast is safe: exclusive expects Observable[Observable[T]] but
        # we have Observable[_T]. The fluent API allows calling this on
        # sequences of observables.
        source: Observable[Any] = cast("Observable[Any]", self._as_observable())
        return cast("Observable[_T]", ops.exclusive()(source))
