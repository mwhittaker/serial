"""
This module provides functions to randomly generate schedules using the
hypothesis python library. It then uses these functions to randomly generate
schedules satisfying different mixes of properties.

If you run this script,
    (1) the short schedules will be written to short.tex,
    (2) their charachterization be written to short-sol.tex,
    (3) the tabularized schedules will be written to tables.tex, and
    (4) the conflict graphs will be written to conflict-graph-i.tex.
"""
from action import *
import hypothesis as hyp
import hypothesis.strategies as st
import random
import serial
import matplotlib.pyplot as plt

def shuffle(xs, ys, r):
    """
    Randomly shuffle two lists xs and ys with hypothesis random r. Here are
    some *possible* outputs.
    >>> shuffle([1, 2, 3], ["a", "b", "c"], r #doctest: +skip
    [1, 2, 'a', 3, 'b', 'c']
    >>> shuffle([1, 2, 3], ["a", "b", "c"], r) #doctest: +skip
    ['a, 'b', 1, 2, 3, 'c']
    >>> shuffle([1, 2, 3], ["a", "b", "c"], r) #doctest: +skip
    [1, 2, 'a', 'b', 'c', 3]
    """
    shuffled_len = len(xs) + len(ys)
    shuffled = [None] * shuffled_len
    indices = range(shuffled_len)
    xs_indices = sorted(r.sample(indices, len(xs)))
    ys_indices = [i for i in indices if i not in xs_indices]

    for (x, i) in zip(xs, xs_indices):
        shuffled[i] = x

    for (y, i) in zip(ys, ys_indices):
        shuffled[i] = y

    return shuffled

def shuffles(ls, r):
    """Shuffle a list of lists."""
    return reduce(lambda xs, ys: shuffle(xs, ys, r), ls, [])

def object():
    """Random object (e.g. A, B, X, Y, Z)."""
    return st.one_of([st.just(X), st.just(Y), st.just(Z)])

def read_or_write_type():
    """READ or WRITE."""
    return st.one_of([st.just(READ), st.just(WRITE)])

def commit_or_abort_type():
    """COMMIT or ABORT."""
    return st.one_of([st.just(COMMIT), st.just(ABORT)])

def read_or_write(i):
    """Random read or write on random object by transaction i."""
    return st.tuples(read_or_write_type(), object()).map(lambda (t, o): Action(t, i, o))

def commit_or_abort(i):
    """Random commit or abort transaction i."""
    return commit_or_abort_type().map(lambda t: Action(t, i, None))

def number_of_txns():
    """Random number of transactions >=2."""
    return st.integers(min_value=2, max_value=3)

def transaction(i):
    """Random transaction by transaction i."""
    rws = st.lists(elements=read_or_write(i), min_size=1, max_size=3)
    ca  = commit_or_abort(i)
    return st.tuples(rws, ca).map(lambda (rws, ca): rws + [ca])

def schedule():
    """Random schedule of transactions."""
    return \
        number_of_txns().flatmap(lambda n:
        st.tuples(*[transaction(i) for i in range(1, n+1)]).flatmap(lambda ts:
        st.randoms().map(lambda r:
        shuffles(ts, r)
        )))

def main():
    # abbreviations
    vs  = serial.view_serializable
    cs  = serial.conflict_serializable
    rec = serial.recoverable
    aca = serial.aca
    sct = serial.strict

    # boolean logic predicate combinators
    def neg(p): return lambda s: not p(s)
    def all_of(ps): return lambda s: all([p(s) for p in ps])

    def characterize(sched):
        return [vs(sched), cs(sched), rec(sched), aca(sched), sct(sched)]

    def short_bool(b):
        return "T" if b else "F"

    def check_bool(b):
        return "$\\checkmark$" if b else ""

    def show(sched):
        s = " ".join(short_bool(b) for b in characterize(sched))
        print s, sched
        return sched

    def find(r, p):
        minimized = True
        if minimized:
            return hyp.find(r, p)
        else:
            while True:
                s = r.example()
                if p(s):
                    return s

    schedules = []
    schedules.append(show(find(schedule(), all_of([sct, cs]))))
    # for some odd reason, this schedule takes a really long time to find
    # schedules.append(show(find(schedule(), all_of([sct, neg(cs), vs]))))
    schedules.append(show([r(2,X),w(3,X),commit(3),r(1,X),w(2,X),commit(2),w(1,X),commit(1)]))
    schedules.append(show(find(schedule(), all_of([sct, neg(vs)]))))
    print ""
    schedules.append(show(find(schedule(), all_of([neg(sct), aca, cs]))))
    schedules.append(show(find(schedule(), all_of([neg(sct), aca, neg(cs), vs]))))
    schedules.append(show(find(schedule(), all_of([neg(sct), aca, neg(vs)]))))
    print ""
    schedules.append(show(find(schedule(), all_of([neg(aca), rec, cs]))))
    schedules.append(show(find(schedule(), all_of([neg(aca), rec, neg(cs), vs]))))
    schedules.append(show(find(schedule(), all_of([neg(aca), rec, neg(vs)]))))
    print ""
    schedules.append(show(find(schedule(), all_of([neg(rec), cs]))))
    schedules.append(show(find(schedule(), all_of([neg(rec), neg(cs), vs]))))
    schedules.append(show(find(schedule(), all_of([neg(rec), neg(vs)]))))

    random.shuffle(schedules)

    with open("short.tex", "w") as f:
        for (i, s) in enumerate(schedules, 1):
            f.write("\\item " + ", ".join(a.tex() for a in s) + "\n")

    with open("short-sol.tex", "w") as f:
        for (i, s) in enumerate(schedules, 1):
            checks = " & ".join(check_bool(b) for b in characterize(s))
            f.write("{} & {} \\\\\\hline\n".format(i, checks))

    with open("tables.tex", "w") as f:
        for s in schedules:
            f.write(serial.tex(s) + "\n")

    for (i, s) in enumerate(schedules, 1):
        serial.draw(serial.conflict_graph(s))
        plt.savefig("conflict-graph-{}.pdf".format(i))
        plt.close()

if __name__ == "__main__":
    main()
