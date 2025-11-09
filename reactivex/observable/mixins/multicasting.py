"""Multicasting operators mixin for Observable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, cast, overload

from reactivex import abc, typing

if TYPE_CHECKING:
    from reactivex.observable import Observable
    from reactivex.observable.connectableobservable import ConnectableObservable

_T = TypeVar("_T", covariant=True)
_R = TypeVar("_R")


class MulticastingMixin(Generic[_T]):
    """Mixin providing multicasting operators for Observable.

    This mixin adds operators that share a single subscription among
    multiple observers, including publish, replay, and multicast.
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

    def share(self) -> Observable[_T]:
        """Share a single subscription among multiple observers.

        This is an alias for a composed publish() and ref_count().
        As long as there is at least one subscriber, this observable
        will be subscribed and emitting data. When all subscribers have
        unsubscribed, it will unsubscribe from the source.

        Examples:
            Fluent style:
            >>> shared = source.share()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> shared = source.pipe(ops.share())

        Returns:
            An observable that shares a single subscription to the
            underlying source.

        See Also:
            - :func:`share <reactivex.operators.share>`
            - :meth:`publish`
            - :meth:`ref_count`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.share())

    @overload
    def publish(self) -> ConnectableObservable[_T]: ...

    @overload
    def publish(
        self, mapper: typing.Mapper[Observable[_T], Observable[_R]]
    ) -> Observable[_R]: ...

    def publish(
        self, mapper: typing.Mapper[Observable[_T], Observable[_R]] | None = None
    ) -> Observable[_R] | ConnectableObservable[_T]:
        """Returns a connectable observable or maps through a selector.

        Returns an observable sequence that is the result of invoking the
        mapper on a connectable observable sequence that shares a single
        subscription to the underlying sequence.

        Examples:
            Fluent style:
            >>> connectable = source.publish()
            >>> result = source.publish(lambda x: x.take(5))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> connectable = source.pipe(ops.publish())

        Args:
            mapper: Optional selector function which can use the
                multicasted source sequence.

        Returns:
            An observable sequence that contains the elements of a
            sequence produced by multicasting the source sequence within
            a mapper function, or a connectable observable if no mapper
            is specified.

        See Also:
            - :func:`publish <reactivex.operators.publish>`
            - :meth:`share`
            - :meth:`multicast`
        """
        from reactivex import operators as ops

        if mapper is None:
            return self._as_observable().pipe(ops.publish())
        return self._as_observable().pipe(ops.publish(mapper))

    @overload
    def replay(
        self,
        buffer_size: int | None = None,
        window: typing.RelativeTime | None = None,
        *,
        scheduler: abc.SchedulerBase | None = None,
    ) -> ConnectableObservable[_T]: ...

    @overload
    def replay(
        self,
        buffer_size: int | None = None,
        window: typing.RelativeTime | None = None,
        *,
        mapper: typing.Mapper[Observable[_T], Observable[_R]],
        scheduler: abc.SchedulerBase | None = None,
    ) -> Observable[_R]: ...

    def replay(
        self,
        buffer_size: int | None = None,
        window: typing.RelativeTime | None = None,
        *,
        mapper: typing.Mapper[Observable[_T], Observable[_R]] | None = None,
        scheduler: abc.SchedulerBase | None = None,
    ) -> Observable[_R] | ConnectableObservable[_T]:
        """Replay emissions to new subscribers.

        Returns an observable sequence that is the result of invoking the
        mapper on a connectable observable sequence that shares a single
        subscription to the underlying sequence and starts with an initial
        value. Replays values to new subscribers.

        Examples:
            Fluent style:
            >>> connectable = source.replay()
            >>> connectable = source.replay(buffer_size=3)
            >>> result = source.replay(mapper=lambda x: x.take(5))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> connectable = source.pipe(ops.replay())

        Args:
            buffer_size: Maximum element count of the replay buffer.
            window: Maximum time length of the replay buffer.
            mapper: Selector function which can use the multicasted source.
            scheduler: Scheduler to use for replay timing.

        Returns:
            An observable sequence that contains the elements of a
            sequence produced by multicasting the source sequence within
            a mapper function, or a connectable observable if no mapper
            is specified.

        See Also:
            - :func:`replay <reactivex.operators.replay>`
            - :meth:`publish`
            - :meth:`share`
        """
        from reactivex import operators as ops

        if mapper is None:
            return self._as_observable().pipe(
                ops.replay(buffer_size, window, scheduler=scheduler)
            )
        return self._as_observable().pipe(
            ops.replay(buffer_size, window, mapper=mapper, scheduler=scheduler)
        )

    def multicast(
        self,
        subject: abc.SubjectBase[_T] | None = None,
    ) -> Observable[_T]:
        """Multicast through a subject.

        Multicasts the source sequence notifications through an
        instantiated subject.

        Examples:
            Fluent style:
            >>> from reactivex.subject import Subject
            >>> connectable = source.multicast(Subject())

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> connectable = source.pipe(ops.multicast(Subject()))

        Args:
            subject: The subject to multicast through. If None, creates
                a new subject.

        Returns:
            A connectable observable sequence that upon connection causes
            the source sequence to push results into the specified subject.

        See Also:
            - :func:`multicast <reactivex.operators.multicast>`
            - :meth:`publish`
            - :meth:`share`
        """
        from reactivex import operators as ops

        if subject is None:
            return self._as_observable().pipe(ops.multicast())
        return self._as_observable().pipe(ops.multicast(subject))

    def ref_count(self) -> Observable[_T]:
        """Manage subscriptions to a connectable observable.

        Returns an observable sequence that stays connected to the
        source as long as there is at least one subscription to the
        observable sequence.

        Examples:
            Fluent style:
            >>> result = source.publish().ref_count()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.publish(), ops.ref_count())

        Returns:
            An observable sequence that stays connected to the source.

        See Also:
            - :func:`ref_count <reactivex.operators.ref_count>`
            - :meth:`share`
            - :meth:`publish`
        """
        from reactivex import operators as ops

        # Cast is safe: ref_count is meant to be called on ConnectableObservable
        # instances (the result of publish/multicast). The fluent API allows
        # chaining this after publish(). We call the operator directly to avoid
        # type variance issues with pipe's generic parameters.
        source = cast("ConnectableObservable[_T]", self._as_observable())
        return ops.ref_count()(source)
