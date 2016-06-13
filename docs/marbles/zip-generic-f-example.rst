.. raw:: html

   <div id="zip-generic-f-example"></div>
   <script>
     var M = Marbles
     var E = M.examples.marbles
     var f = M.functions.f

     var A = M.Observable(true, "p", E.abcd, 1.0);
     var X = M.Observable(true, "q", E.xyz, 1.0);
     var opMerge = M.Operator("p.combine_latest(q, f)",
                      M.operators.zip(f), [A, X]);
     opMerge.render("with_latest_from-example", 600, 60);
   </script>
