from rx.core import Disposable
from rx.disposables import BooleanDisposable, SingleAssignmentDisposable
from rx.disposables import CompositeDisposable, SerialDisposable
from rx.disposables import RefCountDisposable


def test_anonymousdisposable_create():
    def action():
        pass

    disposable = Disposable.create(action)
    assert disposable


def test_anonymousdisposable_dispose():
    disposed = [False]

    def action():
        disposed[0] = True

    d = Disposable.create(action)
    assert not disposed[0]
    d.dispose()
    assert disposed[0]


def test_emptydisposable():
    d = Disposable.empty()
    assert d
    d.dispose()


def test_booleandisposable():
    d = BooleanDisposable()
    assert not d.is_disposed
    d.dispose()
    assert d.is_disposed
    d.dispose()
    assert d.is_disposed


def test_future_disposable_setnone():
    d = SingleAssignmentDisposable()
    d.disposable = None
    assert d.disposable == None

def test_futuredisposable_disposeafterset():
    d = SingleAssignmentDisposable()
    disposed = [False]

    def action():
        disposed[0] = True

    dd = Disposable.create(action)
    d.disposable = dd
    assert dd == d.disposable
    assert not disposed[0]

    d.dispose()
    assert disposed[0]
    d.dispose()
    assert disposed[0]

def test_futuredisposable_disposebeforeset():
    disposed = [False]

    def dispose():
        disposed[0] = True

    d = SingleAssignmentDisposable()
    dd = Disposable.create(dispose)

    assert not disposed[0]
    d.dispose()
    assert not disposed[0]
    d.disposable = dd
    assert d.disposable == None
    assert disposed[0]
    d.dispose()
    assert disposed[0]

def test_groupdisposable_contains():
    d1 = Disposable.empty()
    d2 = Disposable.empty()

    g = CompositeDisposable(d1, d2)

    assert g.length == 2
    assert g.contains(d1)
    assert g.contains(d2)

def test_groupdisposable_add():
    d1 = Disposable.empty()
    d2 = Disposable.empty()

    g = CompositeDisposable(d1)

    assert g.length == 1
    assert g.contains(d1)
    g.add(d2)
    assert g.length == 2
    assert g.contains(d2)

def test_groupdisposable_addafterdispose():
    disp1 = [False]
    disp2 = [False]

    def action1():
        disp1[0] = True

    d1 = Disposable.create(action1)

    def action2():
        disp2[0] = True

    d2 = Disposable.create(action2)

    g = CompositeDisposable(d1)
    assert g.length == 1
    g.dispose()
    assert disp1[0]
    assert g.length == 0
    g.add(d2)
    assert disp2[0]
    assert g.length == 0

def test_groupdisposable_remove():
    disp1 = [False]
    disp2 = [False]

    def action1():
        disp1[0] = True
    d1 = Disposable.create(action1)

    def action2():
        disp2[0] = True
    d2 = Disposable.create(action2)

    g = CompositeDisposable(d1, d2)

    assert g.length == 2
    assert g.contains(d1)
    assert g.contains(d2)
    assert g.remove(d1)
    assert g.length == 1
    assert not g.contains(d1)
    assert g.contains(d2)
    assert disp1[0]
    assert g.remove(d2)
    assert not g.contains(d1)
    assert not g.contains(d2)
    assert disp2[0]

    disp3 = [False]

    def action3():
        disp3[0] = True
    d3 = Disposable.create(action3)
    assert not g.remove(d3)
    assert not disp3[0]

def test_groupdisposable_clear():
    disp1 = [False]
    disp2 = [False]
    def action1():
        disp1[0] = True
    d1 = Disposable.create(action1)

    def action2():
        disp2[0] = True
    d2 = Disposable.create(action2)

    g = CompositeDisposable(d1, d2)
    assert g.length == 2

    g.clear()
    assert disp1[0]
    assert disp2[0]
    assert not g.length

    disp3 = [False]
    def action3():
        disp3[0] = True
    d3 = Disposable.create(action3)
    g.add(d3);
    assert not disp3[0]
    assert g.length == 1

def test_mutabledisposable_ctor_prop():
    m = SerialDisposable()
    assert not m.disposable

def test_mutabledisposable_replacebeforedispose():
    disp1 = [False]
    disp2 = [False]
    m = SerialDisposable()

    def action1():
        disp1[0] = True
    d1 = Disposable.create(action1)
    m.disposable = d1

    assert d1 == m.disposable
    assert not disp1[0]

    def action2():
        disp2[0] = True
    d2 = Disposable.create(action2)
    m.disposable = d2

    assert d2 == m.disposable
    assert disp1[0]
    assert not disp2[0]

def test_mutabledisposable_replaceafterdispose():
    disp1 = [False]
    disp2 = [False]
    m = SerialDisposable()
    m.dispose()

    def action1():
        disp1[0] = True
    d1 = Disposable.create(action1)
    m.disposable = d1

    assert m.disposable == None
    assert disp1[0]

    def action2():
        disp2[0] = True
    d2 = Disposable.create(action2)
    m.disposable = d2

    assert m.disposable == None
    assert disp2[0]

def test_mutabledisposable_dispose():
    disp = [False]
    m = SerialDisposable()

    def action():
        disp[0] = True
    d = Disposable.create(action)
    m.disposable = d

    assert d == m.disposable
    assert not disp[0]
    m.dispose()
    assert disp[0]
    assert m.disposable == None

def test_refcountdisposable_singlereference():
    d = BooleanDisposable()
    r = RefCountDisposable(d)

    assert not d.is_disposed
    r.dispose()
    assert d.is_disposed
    r.dispose()
    assert d.is_disposed

def test_refcountdisposable_refcounting():
    d = BooleanDisposable()
    r = RefCountDisposable(d)
    assert not d.is_disposed
    d1 = r.disposable
    d2 = r.disposable
    assert not d.is_disposed
    d1.dispose()
    assert not d.is_disposed
    d2.dispose()
    assert not d.is_disposed
    r.dispose()
    assert d.is_disposed
    d3 = r.disposable
    d3.dispose()

def test_refcountdisposable_primarydisposesfirst():
    d = BooleanDisposable()
    r = RefCountDisposable(d)
    assert not d.is_disposed;
    d1 = r.disposable
    d2 = r.disposable
    assert not d.is_disposed
    d1.dispose()
    assert not d.is_disposed
    r.dispose()
    assert not d.is_disposed
    d2.dispose()
    assert d.is_disposed
