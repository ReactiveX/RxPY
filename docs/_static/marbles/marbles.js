Marbles = {
  utils: {},
  svg: {},
  examples: {
    marbles: {},
    observables: {}
  },
  operators: {},
  functions: {}
}

Marbles.utils.disableSelection = function(target){

    if (typeof target.onselectstart!="undefined") //IE route
        target.onselectstart=function(){return false}

    else if (typeof target.style.MozUserSelect!="undefined") //Firefox route
        target.style.MozUserSelect="none"

    else //All other route (ie: Opera)
        target.onmousedown=function(){return false}

    target.style.cursor = "default"
}


Marbles.svg.arrow = function(elt, x1, y1, x2, y2, w, h) {
  var g;
  g = elt.group()
  g.line(x1, y1, x2, y2).stroke({width: 1});
  g.line(x2, y2, x2 - w, y2 + h).stroke({width: 1});
  g.line(x2, y2, x2 - w, y2 - h).stroke({width: 1});
  return g;
}

Marbles.svg.completion = function(elt, x, y, h) {
  return elt.line(x, y+h, x, y-h).stroke({width: 1});
}


Marbles.svg.align = function(dir, elt, x, y) {
  var X = x || elt.x();
  var Y = y || elt.y();
  var bbox = elt.bbox();
  if (dir == "right") {
    elt.x(X - bbox.width);
  } else if (dir == "left") {
    elt.x(X + bbox.width);
  } else if (dir == "top") {
    elt.y(Y - bbox.height);
  } else if (dir == "bottom") {
    elt.y(Y - bbox.height);
  }
}


Marbles.Observable = function(input, name, marbles, complete) {
  return {
    name: name,
    marbles: Marbles.utils.clone(marbles),
    complete: complete,
    operator: false,
    input: input,
    drawing: {},
    control: {
      dragging: false
    },
    render: function(svg, width, x, y) {
      this.drawing.width=width;
      this.drawing.minX=x;
      this.drawing.maxX=x + (this.complete * width);
      this.drawing.arrowEnd = x + width;
      this.drawing.y=y;
      this.drawing.radius=8;
      this.control.dragging=false;
      this.shadowAttrs = {fill: '#ddd', stroke: 'gray'};
      Marbles.svg.arrow(svg, this.drawing.minX, y,
                        this.drawing.arrowEnd + 0.1*width, y,
                        20, 7);
      Marbles.svg.completion(svg, this.drawing.maxX,
                             y, this.drawing.radius*1.5);

      // Name:
      if (this.name) {
        Marbles.svg.align('right',
                          svg.text(name).font({family: 'mono'}).cy(y),
                          x - 8);
      }

      this.drawing.shadowLayer = svg.group()
      var n = this.marbles.length;
      for (var i=0; i < n; i++) {
        this.addMarble(this, svg, i, this.marbles[i]);
      }
    },
    
    connect: function(obj, index) {
      this.operator = obj;
      this.operator.index = index
    },

    addMarble: function(self, svg, index, marb) {
      var x = self.drawing.minX + marb.t * self.drawing.width;
      var y = self.drawing.y
      var marble = svg.circle()
            .radius(self.drawing.radius)
            .attr({ fill: marb.color || '#f06', stroke: 'black' })
            .center(x, y);
      marble.index = index;
      var text = svg.text(marb.value + "")
                       .font({ family: 'mono', size: 'small' })
                       .center(x, y - self.drawing.radius*2.5);
      // Marbles.utils.disableSelection(text);
      if (marb.interval) {
        var interval = Marbles.svg.renderInterval(
                           svg,
                           marb,
                           self.drawing.width, x, y);
      }
      
      if (self.input) {
        marble.draggable();
        marble.mouseover(function(e) {
          document.body.style.cursor = 'move';
        });
        marble.mouseout(function(e) {
          if (!self.dragging) {
            document.body.style.cursor = 'initial';
          }
        });
        marble.on('beforedrag', function(e) {
          self.control.dragging=true;
          self.shadow = marble.clone();
          self.drawing.shadowLayer.add(self.shadow);
          self.shadow.cy(self.y);
          self.shadow.attr(self.shadowAttrs);
          text.fill('#ddd');
        });
        marble.on('dragmove', function(e){
          var x = marble.cx();
          if (x > self.drawing.maxX) {
            x = self.drawing.maxX;
          } else if (x < self.drawing.minX) {
            x = self.drawing.minX;
          }
          text.cx(x)
          if (marb.inteval) {
            Marbles.svg.align("left", interval, x);
          }
          self.shadow.cx(x);
        });
        marble.on('dragend', function(e) {
          var x;
          x = self.shadow.cx();
          self.marbles[marble.index].t = 
                  (x - self.drawing.minX)/self.drawing.width
          self.shadow.animate(120).radius(0);
          marble.animate(120).center(x, self.drawing.y);
          text.fill('initial');
          document.body.style.cursor = 'initial';
          self.control.dragging=false;
          if (self.operator) {
            self.operator.renderOutput()
          }
        });
      }
    }
  }
};

Marbles.svg.renderInterval = function(elt, label, ta, tb, width, x, y) {
  var xa = x + ta*width;
  var xb = x + tb*width;
  var yi = y + 15;
  var g = elt.group()
  g.line(xa, yi,   xb, yi).stroke({width: 1});
  g.line(xa, yi+3, xa, yi-3).stroke({width: 1});
  g.line(xb, yi+3, xb, yi-3).stroke({width: 1});
  return g;
};

Marbles.Operator = function(label, func, observables) {
  return {
    inputs: observables,
    func: func,
    label: label,
    drawing: {output: {}},
    render: function(elementId, width, separation, x, y) {
      var y = y || 33;
      var x = x || 20;
      var n;
      n = this.inputs.length;
      var svg = SVG(elementId).size('100%', separation*(n+1.75));
      this.drawing.svg = svg;
      
      // Operator Label:
      svg.text(this.label)
            .font({family: 'mono'})
            .center((x + (x+width))/2,
                    y + separation * (n-0.25));

      for (var i=0; i < n; i++) {
        this.inputs[i].connect(this);
        this.inputs[i].render(svg, width, x, y + (separation*i));
      }
      this.drawing.output.g = svg.group();
      this.drawing.output.x = x;
      this.drawing.output.y = y + separation * (0.75 + n);
      this.drawing.width = width;
      this.renderOutput();
      return svg;
    },
    
    renderOutput: function() {
      this.drawing.output.g.remove();
      this.drawing.output.g = this.drawing.svg.group();
      var result = this.func(this.inputs);
      this.output = Marbles.Observable(
          false, "", result.marbles, result.complete);
      this.output.render(this.drawing.output.g,
                         this.drawing.width,
                         this.drawing.output.x,
                         this.drawing.output.y);
    }
  };
};

Marbles.operators.merge = function(observables) {
  var marbles = [];
  var m, n;
  m = observables.length;
  for (var i=0; i < m; i++) {
    n = observables[i].marbles.length;
    for (var j=0; j < n; j++) {
      marbles.push(observables[i].marbles[j]);
    }
  }
  return {
    marbles: marbles,
    complete: 1.0
  };
}

Marbles.utils.sortedMarbles = function(observables) {
  var result = [];
  var m, n;
  m = observables.length;
  for (var i=0; i<m; i++) {
    var row = [];
    row = observables[i].marbles
            .slice().sort(function(m1, m2){
                            return m1.t - m2.t;
                          });
    result.push(row);
  }
  return result;
}

Marbles.operators.zip = function(func) {
  return function(observables) {
    var marbles = [];
    var m, n, minLength;
    var sorted = Marbles.utils.sortedMarbles(observables);
    m = sorted.length;
    for (var i=1; i < m; i++) {
      minLength = Math.min(minLength || 99999,
                           sorted[i].length);
    }
    for (var j=0; j < minLength; j++) {
      var args = [];
      var tMax = 0;
      for (var i=0; i < m; i++) {
        var marble = sorted[i][j]
        tMax = Math.max(tMax, marble.t);
        args.push(marble.value);
      }
      var color = sorted[0][j].color || undefined
      marbles.push({t: tMax, value: func(args), color: color})
    }
    return {
      marbles: marbles,
      complete: 1.0
    };
  };
}

Marbles.utils.previousBefore = function(t, marbles) {
  var n = marbles.length;
  var current = null;
  for (var i=0; i < n; i++) {
    if (marbles[i].t <= t) {
      current = marbles[i];
    } else {
      return current;
    }
  }
  return current;
}

Marbles.utils.combinedArgs = function(j, marb, sorted) {
  var args = [];
  var t = marb.t;
  var marble;
  var n = sorted.length;
  for (var i=0; i < n; i++) {
    if (i == j) {
      args.push(marb.value);
    } else {
      marble = Marbles.utils.previousBefore(t, sorted[i]);
      if (marble == null) {
        return null;
      } else {
        args.push(marble.value)
      }
    }
  }
  return args;
}

Marbles.operators.combineLatest = function(func) {
  return function(observables) {
    var marbles = [];
    var m, marb, marble;
    var observable;
    var nrOfObservables = observables.length;
    var sorted = Marbles.utils.sortedMarbles(observables);
    for (var i=0; i < nrOfObservables; i++) {
      observable = observables[i];
      m = observable.marbles.length;
      for (var j=0; j < m; j++) {
        marb = observable.marbles[j];
        var args = Marbles.utils.combinedArgs(i, marb, sorted);
        if (args != null) {
          var marble = {t: marb.t,
                        value: func(args),
                        color: marb.color};
          marbles.push(marble);
        }
      }
    }
    return {
      marbles: marbles,
      complete: 1.0
    };
  };
}

Marbles.operators.withLatestFrom = function(func) {
  return function(observables) {
    var marbles = [];
    var m, marb, marble;
    var sorted = Marbles.utils.sortedMarbles(observables);
    m = observables[0].marbles.length;
    for (var j=1; j < m; j++) {
      marb = observables[0].marbles[j];
      var args = Marbles.utils.combinedArgs(0, marb, sorted);
      if (args != null) {
        var marble = {t: marb.t,
                      value: func(args),
                      color: marb.color};
        marbles.push(marble);
      }
    }
    return {
      marbles: marbles,
      complete: 1.0
    };
  };
}


Marbles.operators.filter = function(func) {
  var helper = function(observables) {
    var marbles = [];
    var n = observables[0].marbles.length;
    for (var j=0; j < n; j++) {
      if (func(observables[0].marbles[j].value)) {
        marbles.push(observables[0].marbles[j]);
      }
    }
    return {
      marbles: marbles,
      complete: 1.0
    };
  }
  return helper;
}

Marbles.operators.average = function(observables) {
  var args = [];
  var n = observables[0].marbles.length;
  for (var j=0; j < n; j++) {
    args.push(observables[0].marbles[j].value);
  }
  var marb = {
    t: observables[0].complete,
    value: Marbles.functions.average(args),
  };
  return {
    marbles: [marb],
    complete: observables[0].complete
  };
}

Marbles.utils.clone = function(obj) {
    if(obj == null || typeof(obj) != 'object')
        return obj;    
    var temp = new obj.constructor(); 
    for(var key in obj)
        temp[key] = Marbles.utils.clone(obj[key]);    
    return temp;
}

Marbles.operators.map = function(func) {
  var helper = function(observables, first, inputIndex, marbleIndex) {
    var marbles = [];
    var n = observables[0].marbles.length;
    for (var j=0; j < n; j++) {
      var marble = Marbles.utils.clone(observables[0].marbles[j]);
      marble.value = func(observables[0].marbles[j].value)
      marbles.push(marble);
    }
    return {
      marbles: marbles,
      complete: 1.0
    };
  }
  return helper;
}

// Example Functions
Marbles.functions.generic = function(fname, sep) {
  return function(args) {
    var n = args.length;
    var result = fname + "(" + args[0];
    for (var i=1; i < n; i++) {
      result = result + (sep || ",") + args[i];
    }
    // result = 'f(a_1, a_2, ..., a_n)'
    result = result + ")";
    return result;
  };
}

Marbles.functions.sum = function(xs) {
  var total = 0;
  var n = xs.length;
  for (var i=0; i<n; i++) {
    total = total + xs[i];
  }
  return total;
}

Marbles.functions.average = function(xs) {
  var total = 0;
  var n = xs.length;
  for (var i=0; i<n; i++) {
    total = total + xs[i];
  }
  return total/n;
}

Marbles.functions.concat = function(xs) {
  var total = "";
  var n = xs.length;
  for (var i=0; i<n; i++) {
    total = total + xs[i];
  }
  return total;
}

Marbles.functions.odd = function(n) {
  return n % 2 == 1;
}

Marbles.functions.even = function(n) {
  return n % 2 == 0;
}

Marbles.functions.times = function(c) {
  var helper = function(x) {
    return c*x;
  }
  return helper;
}

Marbles.functions.f = Marbles.functions.generic('f', ',')
Marbles.functions.g = Marbles.functions.generic('g', ',')
Marbles.functions.h = Marbles.functions.generic('h', ',')

// Example marbles
Marbles.examples.marbles.abcd = [
  {t: 0.05, value: "a", color: 'pink'},
  {t: 0.20, value: "b", color: 'red'},
  {t: 0.70, value: "c", color: 'orange'},
  {t: 0.92, value: "d", color: 'yellow'},
];

Marbles.examples.marbles.xyz = [
  {t: 0.10, value: "x", color: 'green'},
  {t: 0.30, value: "y", color: 'cyan'},
  {t: 0.50, value: "z", color: 'blue'},
];

Marbles.examples.marbles.uvw = [
  {t: 0.18, value: "u", color: 'darkgreen'},
  {t: 0.34, value: "v", color: 'cyan'},
  {t: 0.66, value: "w", color: 'navy'},
];

Marbles.examples.marbles._12345 = [
  {t: 0.15, value: 1},
  {t: 0.29, value: 2},
  {t: 0.60, value: 3},
  {t: 0.78, value: 4},
  {t: 0.95, value: 5},
];

Marbles.examples.marbles._20_30_70 = [
  {t: 0.16, value: 20},
  {t: 0.37, value: 30},
  {t: 0.68, value: 70},
];

var M = Marbles
var E = M.examples.marbles

var f = M.functions.f

var A = M.Observable(true, "p", M.examples.marbles.abcd, 1.0);
var X = M.Observable(true, "q", M.examples.marbles.xyz, 1.0);
var opMap = M.Operator("p.map(f)",
      M.operators.map(f),
      [M.Observable(true, "p", E.abcd, 1.0),
       M.Observable(true, "q", E.xyz, 1.0)])

var opFilter = M.Operator("p.filter(lambda x: x % 2 == 0)",
    M.operators.filter(M.functions.even),
    [M.Observable(true, "p", E._12345, 1.0)])

var A = M.Observable(true, "p", M.examples.marbles.abcd, 1.0);
var X = M.Observable(true, "q", M.examples.marbles.xyz, 1.0);
var opMerge = M.Operator("p.merge(q)", M.operators.merge, [A, X]);

var A = M.Observable(true, "p", M.examples.marbles.abcd, 1.0);
var X = M.Observable(true, "q", M.examples.marbles.xyz, 1.0);
var opZip = M.Operator("p.zip(q, f)", M.operators.zip(f), [A, X]);

var A = M.Observable(true, "p", M.examples.marbles.abcd, 1.0);
var X = M.Observable(true, "q", M.examples.marbles.xyz, 1.0);
var opCombineLatest = M.Operator("p.combineLatest(q, f)",
    Marbles.operators.combineLatest(f), [A, X]);

var A = M.Observable(true, "p", M.examples.marbles.abcd, 1.0);
var X = M.Observable(true, "q", M.examples.marbles.xyz, 1.0);
var opWithLatestFrom = M.Operator("p.withLatestFrom(q, f)",
    Marbles.operators.withLatestFrom(f), [A, X]);

var opAverage = M.Operator("p.average()",
      M.operators.average,
      [M.Observable(true, "p", E._20_30_70, 0.8)]);

opMap.render("map", 500, 60);
opFilter.render("filter", 500, 60);
opMerge.render("merge", 500, 60);
opZip.render("zip", 500, 60);
opCombineLatest.render("combineLatest", 500, 60);
opWithLatestFrom.render("withLatestFrom", 500, 60);
opAverage.render("average", 500, 60);
