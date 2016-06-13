.. figure:: /img/RxPY/misc/under-construction-icon.png
    :align: center
    
    Under construction...

.. currentmodule:: rx

.. _operator_merge:
.. _operator_merge_all:
.. _operator_merge_observable:


Merge
=====

.. raw:: html

   <div id="merge-example"></div>
   <script>
   var M = Marbles
   var E = M.examples.marbles
   var f = M.functions.f

   var A = M.Observable(true, "p", E.abcd, 1.0);
   var X = M.Observable(true, "q", E.xyz, 1.0);
   var opMerge = M.Operator("p.merge(q)", M.operators.merge, [A, X]);
   opMerge.render("merge-example", 600, 60);
   </script>


.. automethod:: Observable.merge

    
    .. image:: /img/reactivex/operators/merge.png
        :align: center
    

.. automethod:: Observable.merge_all

    
    .. image:: /img/reactivex/operators/merge_all.png
        :align: center
    

.. automethod:: Observable.merge_observable

    
