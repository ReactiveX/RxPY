.. raw:: html

  <div id="with_latest_from-generic-f-example"></div>

  <script>
    var M = Marbles
    var E = M.examples.marbles
    var f = M.functions.f

    var A = M.Observable(true, "p", E.abcd, 1.0);
    var X = M.Observable(true, "q", E.xyz, 1.0);
    var opMerge = M.Operator("p.with_latest_from(q, f)",
                   M.operators.withLatestFrom(f), [A, X]);
    opMerge.render("with_latest_from-generic-f-example", 600, 60);
  </script>
