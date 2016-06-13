.. include:: operator-aliases.rst


.. figure:: /img/RxPY/misc/under-construction-icon.png
    :align: center
    
    Under construction...

.. currentmodule:: rx

Combine latest
==============

   When an item is emitted by either of two Observables, combine the latest
   item emitted by each Observable via a specified function and emit items
   based on the results of this function

The |combine_latest| operator behaves in a similar way to |zip|, but while
|zip| emits items only when each of the zipped source Observables have emitted
a previously unzipped item, |combine_latest| emits an item whenever any of the
source Observables emits an item (so long as each of the source Observables has
emitted at least one item). When any of the source Observables emits an item,
|combine_latest| combines the most recently emitted items from each of the other
source Observables, using a function you provide, and emits the return value
from that function.

.. include:: /marbles/combine_latest-generic-f-example.rst

Besides |combine_latest|, RxPY also defines a related operator,
|with_latest_from|.  It is similar to |combine_latest|, but only emits items when
the single source Observable emits an item (not when *any* of the Observables
that are passed to the operator do, as |combine_latest| does). 

.. include:: /marbles/with_latest_from-generic-f-example.rst


.. seealso::

  - |zip|
  - Official ReactiveX documentation:
    `CombineLatest <http://reactivex.io/documentation/operators/combinelatest.html>`_
  - RxMarbles: combineLatest
  - RxMarbles: withLatestFrom

.. _operator_combine_latest:

.. automethod:: Observable.combine_latest
    
   .. image:: /img/reactivex/operators/combineLatest.png
       :align: center
   
.. _operator_with_latest_from:

.. automethod:: Observable.with_latest_from

    .. image:: /img/reactivex/operators/withLatestFrom.png
        :align: center
