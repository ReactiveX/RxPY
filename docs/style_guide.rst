.. _style_guide:

Style Guide: Fluent vs Functional
==================================

RxPY supports two equally valid syntax styles for composing observable sequences:
**fluent** (method chaining) and **functional** (pipe-based). This guide will help
you understand the differences and choose the right style for your project.

Both Styles Are First-Class Citizens
-------------------------------------

Starting with RxPY v4.x, both fluent and functional styles are fully supported,
type-safe, and equally performant. There is **no performance difference** between
the two styles - fluent methods internally delegate to the pipe operators.

You can:

* Use fluent style exclusively
* Use functional style exclusively
* Mix both styles in the same pipeline
* Choose different styles for different parts of your codebase

The choice is entirely based on your team's preferences and coding standards.

Fluent Style (Method Chaining)
-------------------------------

The fluent style uses method chaining directly on Observable instances:

.. code:: python

    import reactivex as rx

    result = (rx.of(1, 2, 3, 4, 5)
        .map(lambda x: x * 2)
        .filter(lambda x: x > 5)
        .reduce(lambda acc, x: acc + x, 0)
    )
    result.subscribe(print)  # Output: 24

**Advantages:**

* **Pythonic and intuitive** - Familiar to Python developers
* **Better IDE support** - Autocomplete shows all available operators
* **Easier discoverability** - No need to import ``operators as ops``
* **Less boilerplate** - No ``pipe()`` calls or operator imports
* **Cleaner for simple chains** - More readable for short pipelines

**When to use:**

* Small to medium-sized projects
* Teams new to ReactiveX
* Interactive notebooks and examples
* Quick prototyping and experimentation
* When IDE autocomplete is important

Functional Style (Pipe-Based)
------------------------------

The functional style uses the ``pipe()`` method with operator functions:

.. code:: python

    import reactivex as rx
    from reactivex import operators as ops

    result = rx.of(1, 2, 3, 4, 5).pipe(
        ops.map(lambda x: x * 2),
        ops.filter(lambda x: x > 5),
        ops.reduce(lambda acc, x: acc + x, 0)
    )
    result.subscribe(print)  # Output: 24

**Advantages:**

* **Familiar to RxJS/RxJava developers** - Standard Rx style
* **Better for complex pipelines** - Visual grouping of operators
* **Easier to create custom operators** - Composable operator functions
* **Explicit imports** - Clear which operators are being used
* **Better for large chains** - More manageable when 10+ operators

**When to use:**

* Large enterprise projects
* Teams familiar with RxJS or other Rx libraries
* Complex operator pipelines (10+ operators)
* When creating custom operators
* Migrating from RxJS or RxJava

Mixing Both Styles
------------------

You can freely mix fluent and functional styles in the same pipeline:

.. code:: python

    import reactivex as rx
    from reactivex import operators as ops

    result = (rx.of(1, 2, 3, 4, 5)
        .map(lambda x: x * 2)           # Fluent
        .pipe(                          # Switch to functional
            ops.filter(lambda x: x > 5),
            ops.take(2)
        )
        .reduce(lambda acc, x: acc + x, 0)  # Back to fluent
    )

This is particularly useful when:

* Using a custom operator (which must be used with ``pipe()``)
* Grouping related operators for readability
* Gradually migrating from one style to another

Comparison Examples
-------------------

Simple Transformation
.....................

**Fluent:**

.. code:: python

    result = source.map(lambda x: x * 2).filter(lambda x: x > 10)

**Functional:**

.. code:: python

    result = source.pipe(
        ops.map(lambda x: x * 2),
        ops.filter(lambda x: x > 10)
    )

Both produce identical results. The fluent style is more concise for simple chains.

Complex Pipeline
................

**Fluent:**

.. code:: python

    result = (source
        .map(lambda x: x * 2)
        .filter(lambda x: x > 10)
        .group_by(lambda x: x % 3)
        .flat_map(lambda group: group.pipe(
            ops.reduce(lambda acc, x: acc + x, 0)
        ))
        .to_list()
    )

**Functional:**

.. code:: python

    result = source.pipe(
        ops.map(lambda x: x * 2),
        ops.filter(lambda x: x > 10),
        ops.group_by(lambda x: x % 3),
        ops.flat_map(lambda group: group.pipe(
            ops.reduce(lambda acc, x: acc + x, 0)
        )),
        ops.to_list()
    )

For complex pipelines, the functional style provides better visual grouping.

With Custom Operators
.....................

.. code:: python

    import reactivex
    from reactivex import operators as ops

    def length_more_than_5():
        return reactivex.compose(
            ops.map(lambda s: len(s)),
            ops.filter(lambda i: i >= 5),
        )

    # Must use pipe() for custom operators
    result = source.pipe(
        length_more_than_5(),
        ops.take(3)
    )

    # But you can mix with fluent style
    result = source.pipe(
        length_more_than_5()
    ).take(3).distinct()

Type Safety
-----------

Both styles are fully type-safe with ``pyright`` strict mode:

.. code:: python

    from reactivex import Observable

    # Fluent - fully typed
    source: Observable[int] = rx.of(1, 2, 3)
    result: Observable[str] = source.map(lambda x: str(x))

    # Functional - fully typed
    from reactivex import operators as ops
    source: Observable[int] = rx.of(1, 2, 3)
    result: Observable[str] = source.pipe(ops.map(lambda x: str(x)))

All 149 operators have complete type annotations in both styles.

Migration from RxPY v4.x
-------------------------

RxPY v4.x only supported the functional (pipe-based) style. All existing v4.x
code continues to work without any changes:

.. code:: python

    # RxPY v4.x code - still works in v5.x
    from reactivex import operators as ops

    result = source.pipe(
        ops.map(lambda x: x * 2),
        ops.filter(lambda x: x > 5)
    )

You can gradually adopt the fluent style in new code while keeping existing
code unchanged. There are **no breaking changes**.

Migration from RxJS/RxJava
--------------------------

If you're coming from RxJS or RxJava, the fluent style will feel very familiar:

**RxJS:**

.. code:: javascript

    source
        .map(x => x * 2)
        .filter(x => x > 5)
        .subscribe(x => console.log(x));

**RxPY Fluent (similar to RxJS):**

.. code:: python

    (source
        .map(lambda x: x * 2)
        .filter(lambda x: x > 5)
        .subscribe(lambda x: print(x))
    )

The main differences are:

* Use ``lambda`` instead of arrow functions
* Method names use ``snake_case`` instead of ``camelCase``
* Some operators have different names (see :doc:`migration`)

Recommendations
---------------

**For new projects:**

* **Small projects (<1000 lines):** Use fluent style for simplicity
* **Medium projects (1000-10000 lines):** Choose based on team preference
* **Large projects (>10000 lines):** Consider functional style for better organization

**For teams:**

* **Python-first teams:** Fluent style feels more Pythonic
* **RxJS/RxJava teams:** Fluent style for familiarity, or functional for consistency
* **Mixed backgrounds:** Document your choice and be consistent

**For libraries:**

* Support both styles in examples
* Document which style is used in your codebase
* Consider functional style for better custom operator composition

**General principles:**

* **Be consistent** within a file or module
* **Document your choice** in team coding standards
* **Use what feels natural** - both styles are equally valid
* **Don't mix styles randomly** - have a reason for switching

Performance Considerations
--------------------------

There is **zero performance difference** between fluent and functional styles:

.. code:: python

    # These are EXACTLY equivalent in performance:
    result1 = source.map(lambda x: x * 2).filter(lambda x: x > 5)

    result2 = source.pipe(
        ops.map(lambda x: x * 2),
        ops.filter(lambda x: x > 5)
    )

The fluent methods internally call ``self.pipe(ops.operator_name(...))``, so
there is no additional overhead. The choice is purely stylistic.

Conclusion
----------

RxPY v4.x gives you the freedom to choose the syntax that works best for your
project. Both fluent and functional styles are:

* ✅ Fully supported and maintained
* ✅ Type-safe with complete annotations
* ✅ Equally performant (zero overhead)
* ✅ Well-documented with examples
* ✅ Compatible with all 149+ operators

Choose the style that makes your code most readable and maintainable for your
team. When in doubt, start with the fluent style - it's more Pythonic and easier
to discover operators through IDE autocomplete.

For more information, see:

* :doc:`get_started` - Introduction to RxPY
* :doc:`operators` - Complete operator reference
* :doc:`migration` - Migrating from RxPY v3.x or RxJS
* :doc:`reference_operators` - API reference with both styles
