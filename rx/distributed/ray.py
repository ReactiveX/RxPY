from typing import Callable, Any, Tuple
from collections import deque
import rx
from rx.subject import Subject
from rx.core.notification import OnNext, OnError, OnCompleted
import rx.operators as ops

import ray


def murmur2(data):
    """Pure-python Murmur2 implementation.
    cloned from the python kafka client:
    https://github.com/dpkp/kafka-python/blob/master/kafka/partitioner/default.py
    """
    length = len(data)
    seed = 0x9747b28c
    # 'm' and 'r' are mixing constants generated offline.
    # They're not really 'magic', they just happen to work well.
    m = 0x5bd1e995
    r = 24

    # Initialize the hash to a random value
    h = seed ^ length
    length4 = length // 4

    for i in range(length4):
        i4 = i * 4
        k = ((data[i4 + 0] & 0xff) +
            ((data[i4 + 1] & 0xff) << 8) +
            ((data[i4 + 2] & 0xff) << 16) +
            ((data[i4 + 3] & 0xff) << 24))
        k &= 0xffffffff
        k *= m
        k &= 0xffffffff
        k ^= (k % 0x100000000) >> r # k ^= k >>> r
        k &= 0xffffffff
        k *= m
        k &= 0xffffffff

        h *= m
        h &= 0xffffffff
        h ^= k
        h &= 0xffffffff

    # Handle the last few bytes of the input array
    extra_bytes = length % 4
    if extra_bytes >= 3:
        h ^= (data[(length & ~3) + 2] & 0xff) << 16
        h &= 0xffffffff
    if extra_bytes >= 2:
        h ^= (data[(length & ~3) + 1] & 0xff) << 8
        h &= 0xffffffff
    if extra_bytes >= 1:
        h ^= (data[length & ~3] & 0xff)
        h &= 0xffffffff
        h *= m
        h &= 0xffffffff

    h ^= (h % 0x100000000) >> 13 # h >>> 13;
    h &= 0xffffffff
    h *= m
    h &= 0xffffffff
    h ^= (h % 0x100000000) >> 15 # h >>> 15;
    h &= 0xffffffff

    return h


def round_robin():
    """Partitions items in a round robin way

    Each received item will be distributed on actors in a round robin way. Use
    this partitioner when no relation exist between items. This partitioner
    garantees the order of arrival is the same than the order of emission.

    Returns:
        A partition selector function.
    """
    def _round_robin(state, actor_count, batch_size, i):

        if state is None:
            state = (0, 0)

        active_actor, count = state
        count += 1
        if count == batch_size + 1:
            active_actor += 1
            count = 1
            if active_actor == actor_count:
                active_actor = 0

        return active_actor, (active_actor, count)

    return _round_robin


def partition_by_key(key_selector):
    """Partitions items by key

    The key returned by the key selector must be an integer or a hashabe
    object. This partitioner garantees the order of arrival per key.

    Args:
        key_selectr: A function that takes an item as input and return
                    the key to use for partitioning

    Returns:
        A partition selector function.
    """
    def _partition_by_key(state, actor_count, batch_size, i):
        key = key_selector(i)
        if type(key) == int:
            idx = key
        else:
            idx = murmur2(key)
            idx &= 0x7fffffff
        idx %= actor_count
        return idx, None

    return _partition_by_key


@ray.remote
class RemotePipeline(object):
    def __init__(self, pipeline):
        self.subject = Subject()
        self.item_queue = []

        self.disposable = self.subject.pipe(
            pipeline,
            ops.materialize(),
        ).subscribe(
            on_next=self.item_queue.append,
        )

    def on_next_batch(self, b):
        for i in b:
            self.subject.on_next(i)
        r = list(self.item_queue)
        self.item_queue.clear()
        return r

    def on_completed(self):
        self.subject.on_completed()
        r = self.item_queue
        self.item_queue.clear()
        return r


class ActorState(object):
    def __init__(self, pipeline, batch_size, queue_size):
        self.actor = RemotePipeline.remote(pipeline)
        self.queue_size = queue_size
        self.batch_size = batch_size
        self.batch = []
        self.tasks = deque()
        self.round = queue_size

    def push_next(self, i):
        self.batch.append(i)
        batch = self.pop_batch()
        if batch is not None:
            f = self.actor.on_next_batch.remote(batch)
            self.tasks.append(f)
            if self.round == 0:
                t = self.tasks.popleft()
                i = ray.get(t)
                return i

        return None

    def push_completed(self):
        flushed = False
        if len(self.batch) > 0:
            flushed = True
            f = self.actor.on_next_batch.remote(self.batch)
            self.batch = []
            self.tasks.append(f)
        f = self.actor.on_completed.remote()
        self.tasks.append(f)
        return flushed

    def pop_batch(self):
        if len(self.batch) >= self.batch_size:
            b = self.batch
            self.batch = []
            if self.round > 0:
                self.round -= 1
            return b
        else:
            None

    def drain_one(self):
        if len(self.tasks) > 0:
            t = self.tasks.popleft()
            i = ray.get(t)
            return i

        return None


def compute_actor_count(requested_actor_count):
    actor_count = 1
    if requested_actor_count <= 0:
        resources = ray.available_resources()
        if 'CPU' in resources:
            resource_count = resources['CPU']
            if resource_count > abs(requested_actor_count):
                actor_count = resource_count + requested_actor_count

    else:
        actor_count = requested_actor_count

    return int(actor_count)


def distribute(
               pipeline,
               partition_selector: Callable[[Any, int, Any], Tuple[int, Any]]=round_robin(),
               actor_count=0, batch_size=1, queue_size=3):

    actor_count = compute_actor_count(actor_count)    

    def _ray_pipe(source):
        def on_subscribe(observer, scheduler):
            actors = [ActorState(pipeline, batch_size, queue_size) for _ in range(actor_count)]
            completed = [False for _ in range(actor_count)]
            selector_state = None
            actor_index = None

            def process_batch(i, actor_index):
                for ii in i:
                    if type(ii) is OnNext:
                        observer.on_next(ii.value)
                    elif type(ii) is OnError:
                        observer.on_error(ii.exception)
                    elif type(ii) is OnCompleted:
                        completed[actor_index] = True
                        if all(completed):
                            observer.on_completed()
                    else:
                        raise ValueError("Unknow materialized type")

            def on_next(i):
                nonlocal selector_state
                nonlocal actor_index

                actor_index, selector_state = partition_selector(
                    selector_state, actor_count, batch_size, i
                )
                r = actors[actor_index].push_next(i)
                if r is not None:
                    process_batch(r, actor_index)

            def on_error(e):
                #for actor_index in range(actor_count):
                #    for t in tasks[actor_index]:
                #        i = ray.kill(t)
                #    tasks[actor_index].clear()
                observer.on_error(e)

            def on_completed():
                flushed = False
                for i in range(actor_count):
                    flushed = flushed | actors[i].push_completed()

                flushed = int(not flushed)
                # always drain the actors in round robin order. This garantees
                # total ordering with round robind partitioning and also
                # partition ordering on other partiioning schemes.
                while True:
                    has_next = False
                    for i in range(actor_count):                        
                        index = actor_index + i + flushed
                        if index < 0 or index >= actor_count - 1:
                            index = index % actor_count
                        batch = actors[index].drain_one()
                        if batch is not None:
                            process_batch(batch, index)
                            has_next = True

                    if has_next is False:
                        break
                observer.on_completed()

            return source.subscribe(
                on_next=on_next,
                on_error=on_error,
                on_completed=on_completed
            )

        return rx.create(on_subscribe)

    return _ray_pipe
