"""
This module contains functions to check whether a schedule is:

    1. view-serializable
    2. conflict-serializable
    3. recoverable
    4. avoids cascading aborts
    5. strict

It also contains some nice functions to tabularize schedules into tex and draw
a conflict graph using matplotlib.
"""

from action import *
from collections import defaultdict
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

################################################################################
# helper functions
################################################################################
def flatten(ls):
    """
    >>> flatten([[], [1], [2,3], [4]])
    [1, 2, 3, 4]
    """
    return [x for l in ls for x in l]

def graphs_eq(g1, g2):
    """
    Returns if two networkx graphs are 100% identical.

    >>> G1 = nx.DiGraph()
    >>> G1.add_nodes_from([1, 2, 3])
    >>> G1.add_edges_from([(1, 2), (2, 3), (3, 1)])
    >>> G2 = nx.DiGraph()
    >>> G2.add_nodes_from([3, 2, 1])
    >>> G2.add_edges_from([(3, 1), (2, 3), (1, 2)])
    >>> G3 = nx.DiGraph()
    >>> G3.add_nodes_from([1, 2, 3, 4])
    >>> G3.add_edges_from([(1, 2), (2, 3), (3, 1)])
    >>> G4 = nx.DiGraph()
    >>> G4.add_nodes_from([1, 2, 3])
    >>> G4.add_edges_from([(1, 2), (2, 3), (3, 1), (1, 4)])
    >>> graphs_eq(G1, G2)
    True
    >>> graphs_eq(G2, G1)
    True
    >>> graphs_eq(G1, G3)
    False
    >>> graphs_eq(G1, G4)
    False
    """
    return (set(g1.nodes()) == set(g2.nodes()) and
            set(g1.edges()) == set(g2.edges()))

def transaction_ids(schedule):
    """
    Return a list of the _unique_ transaction ids in the schedule in the order
    that they appear.

    >>> transaction_ids([r(1, "A"), r(2, "A"), w(1, "A"), r(3, "A")])
    [1, 2, 3]
    """
    js = []
    for a in schedule:
        if a.i not in js:
            js.append(a.i)
    return js

def transactions(schedule):
    """
    Partitions a schedule into the list of transactions that compose it.
    Transactions are returned in the order in which an operation of the
    transaction first appears.

    >>> transactions([
    ...     r(1, "A"),
    ...     w(2, "A"),
    ...     commit(2),
    ...     w(1, "A"),
    ...     commit(1),
    ...     w(3, "A"),
    ...     commit(3),
    ... ])
    [[R_1(A), W_1(A), Commit_1], [W_2(A), Commit_2], [W_3(A), Commit_3]]
    >>> transactions([
    ...     w(2, "A"),
    ...     r(1, "A"),
    ...     commit(2),
    ...     w(1, "A"),
    ...     commit(1),
    ...     w(3, "A"),
    ...     commit(3),
    ... ])
    [[W_2(A), Commit_2], [R_1(A), W_1(A), Commit_1], [W_3(A), Commit_3]]
    """
    js = transaction_ids(schedule)
    partitions = [[] for _ in range(len(js))]
    index = {js: i for (i, js) in enumerate(js)}
    for a in schedule:
        partitions[index[a.i]].append(a)
    return partitions

def drop_aborts(schedule):
    """
    Remove all transactions that abort.
    >>> drop_aborts([r(1, "A"), r(2, "A"), r(3, "A"), abort(1), commit(2), abort(3)])
    [R_2(A), Commit_2]
    """
    aborteds = {a.i for a in schedule if a.op == ABORT}
    return [a for a in schedule if a.i not in aborteds]

def add_commits(schedule):
    """
    Add a commit for every transaction that doesn't end in a commit or abort.
    Commits are added in the order of the first action of the transaction.

    >>> add_commits([r(1, "A"), r(2, "A"), r(3, "A"), r(4, "A"), commit(2), abort(4)])
    [R_1(A), R_2(A), R_3(A), R_4(A), Commit_2, Abort_4, Commit_1, Commit_3]
    """
    ends = {a.i for a in schedule if a.op == COMMIT or a.op == ABORT}
    no_ends = [i for i in transaction_ids(schedule) if i not in ends]
    return schedule + [commit(i) for i in no_ends]

def first_read(schedule):
    """
    Returns a mapping from each object to the transaction ids that initially
    read it. If an object is never read, it is not included in the return.

    >>> first_read([w(1, "A"), w(2, "B")])
    {}
    >>> first_read([r(1, "A"), r(2, "B"), r(2, "A")])
    {'A': [1, 2], 'B': [2]}
    """
    fr = defaultdict(list)
    written = set()
    for a in schedule:
        if a.op == READ and a.obj not in written:
            fr[a.obj].append(a.i)
        elif a.op == WRITE:
            written.add(a.obj)
    return dict(fr)

def number(schedule):
    """
    Enumerates each action according to its appearance within its transaction.
    The enumeration begins at 0.

    >>> number([r(1, "A"), r(1, "B"), r(2, "A"), w(3, "A"), commit(2)])
    [(0, R_1(A)), (1, R_1(B)), (0, R_2(A)), (0, W_3(A)), (1, Commit_2)]
    """
    ns = {i: 0 for i in transaction_ids(schedule)}
    s = []
    for a in schedule:
        s.append((ns[a.i], a))
        ns[a.i] += 1
    return s

def view_graph(schedule):
    """
    First, the schedule is numbered using the number function. Then, an edge is
    added from each read of an object to the most recent write to the same
    object.

    >>> view_graph([w(1, "A"), r(2, "A"), r(1, "A")]) #doctest: +SKIP
    +------------+     +------------+
    | (0, W_1(A) |<----| (0, R_2(A) |
    +------------+     +------------+
           ^
           |
    +------------+
    | (1, R_1(A) |
    +------------+
    """
    G = nx.DiGraph()
    last_written = {}
    for (i, a) in number(schedule):
        if a.op == WRITE:
            last_written[a.obj] = (i, a)
        elif a.op == READ:
            if a.obj in last_written:
                G.add_edge((i, a), last_written[a.obj])
        else: # a.op == COMMIT or a.op == ABORT
            pass
    return G

def last_written(schedule):
    """
    Returns a mapping from each object to the transaction id that last writes
    it. If an object is never written, it is not included in the return.

    >>> last_written([r(1, "A"), r(2, "B")])
    {}
    >>> last_written([w(1, "A"), w(2, "B"), w(2, "A")])
    {'A': 2, 'B': 2}
    """
    lw = {}
    for a in schedule:
        if a.op == WRITE:
            lw[a.obj] = a.i
    return lw

def view_equivalent(s1, s2):
    """
    Two schedules s1 and s2 are view equivalent if

        1. If Ti reads the initial value of object A in s1, it must also read
           the initial value of A in s2.
        2. If Ti reads a value of A written by Tj in s1, it must also read the
           value of A written by Tj in s2.
        3. For each data object A, the transaction (if any) that performs the
           final write on A in s1 must also perform the final write on A in s2.
    """
    assert set(transaction_ids(s1)) == set(transaction_ids(s2))

    # condition 1
    if not (first_read(s1) == first_read(s2)):
        return False

    # condition 2
    if not graphs_eq(view_graph(s1), view_graph(s2)):
        return False

    # condition 3
    if not (last_written(s1) == last_written(s2)):
        return False

    return True

################################################################################
# predicates
################################################################################
def view_serializable(schedule):
    """
    A schedule is view serializable if it is view equivalent to a some serial
    schedule over the same transactions. Aborted transactions are ignored.
    """
    schedule = drop_aborts(schedule)

    # conflict serializability implies view serializability
    if conflict_serializable(schedule):
        return True

    # if a schedule is not conflict serializable but doesn't have blind writes,
    # then it isn't view serializabile
    partitions = transactions(schedule)
    blind_write = False
    for t in partitions:
        objects_read = set()
        for a in t:
            if a.op == WRITE and a.obj not in objects_read:
                blind_write = True
            elif a.op == READ:
                objects_read.add(a.obj)
            else: # a.op == COMMIT or a.op == ABORT
                pass
    if not blind_write:
        return False

    # brute force check over all serializations to see if the schedule is view
    # equivalent to any serial schedule over the same set of transactions
    for s in itertools.permutations(transactions(schedule)):
        s = flatten(list(s))
        if view_equivalent(s, schedule):
            return True
    return False

def conflict_serializable(schedule):
    """
    A schedule is conflict serializable if its conflict graph is acyclic.
    Aborted transactions are ignored.
    """
    return len(list(nx.simple_cycles(conflict_graph(schedule)))) == 0

def recoverable(schedule):
    """
    A schedule is recoverable if all the transactions whose changes it read
    commit and the schedule commits after them.
    """
    schedule = add_commits(schedule)

    written_by = defaultdict(list) # object -> ids
    read_from  = defaultdict(set)  # id -> ids
    committed  = set()             # ids
    for a in schedule:
        if a.op == WRITE:
            written_by[a.obj].append(a.i)
        elif a.op == READ:
            if a.obj in written_by and  \
                   len(written_by[a.obj]) > 0 and \
                   written_by[a.obj][-1] != a.i:
               read_from[a.i].add(written_by[a.obj][-1])
        elif a.op == COMMIT:
            if not all(i in committed for i in read_from[a.i]):
                return False
            committed.add(a.i)
        elif a.op == ABORT:
            for (o, ids) in written_by.iteritems():
                written_by[o] = [i for i in ids if i != a.i]

    return True

def aca(schedule):
    """A schedule avoids cascading aborts if it only reads commited changes."""
    schedule = add_commits(schedule)

    last_write = defaultdict(list) # object -> ids
    committed  = set()             # ids
    for a in schedule:
        if a.op == WRITE:
            last_write[a.obj].append(a.i)
        elif a.op == READ:
            if a.obj in last_write and \
                    len(last_write[a.obj]) > 0 and \
                    last_write[a.obj][-1] not in committed \
                    and last_write[a.obj][-1] != a.i:
                return False
        elif a.op == COMMIT:
            committed.add(a.i)
        elif a.op == ABORT:
            for (o, ids) in last_write.iteritems():
                last_write[o] = [i for i in ids if i != a.i]

    return True

def strict(schedule):
    """
    A schedule is strict if never reads or writes to an uncommited changed
    variable.
    """
    schedule = add_commits(schedule)

    last_write = defaultdict(list) # object -> id
    committed  = set()             # ids
    for a in schedule:
        if a.op == WRITE or a.op == READ:
            if a.obj in last_write and \
                    len(last_write[a.obj]) > 0 and \
                    last_write[a.obj][-1] not in committed and \
                    last_write[a.obj][-1] != a.i:
                return False
            if a.op == WRITE:
                last_write[a.obj].append(a.i)
        elif a.op == COMMIT:
            committed.add(a.i)
        elif a.op == ABORT:
            for (o, ids) in last_write.iteritems():
                last_write[o] = [i for i in ids if i != a.i]

    return True

################################################################################
# misc
################################################################################
def tex(schedule):
    """
    Return a texed tabular representation of a schedule.

    >>> tex([r(1,"A"), r(1,"B"), r(2,"B"), r(3,"B"), r(1,"A"), r(2,"B")]) #doctest: +SKIP
    +--------+--------+--------+
    | T_1    | T_2    | T_3    |
    +--------+--------+--------+
    | R_1(A) |        |        |
    | R_1(B) |        |        |
    |        | R_2(B) |        |
    |        |        | R_3(B) |
    | R_1(A) |        |        |
    |        | R_2(B) |        |
    +--------+--------+--------+
    """
    transactions = sorted(transaction_ids(schedule))
    s = r"\begin{tabular}{" + ("|" + "|".join("c" for _ in transactions) + "|" )+ "}\n"
    s += r"\hline" + "\n"
    s += "&".join("$T_{}$".format(t) for t in transactions) + r"\\\hline" + "\n"
    for a in schedule:
        index = transactions.index(a.i)
        s += ("&" * index) + a.tex() + ("&" * (len(transactions) - 1 - index))
        s += r"\\\hline" + "\n"
    s += r"\end{tabular}" + "\n"
    return s

def conflict_graph(schedule):
    """
    A graph with an edge from a to b for each pair of actions (a, b) from
    different transactions on the same object where at least one of the actions
    is a write and a precedes b.
    """
    schedule = drop_aborts(schedule)
    G = nx.DiGraph()
    G.add_nodes_from(transaction_ids(schedule))

    for (i, a) in enumerate(schedule):
        for b in schedule[i+1:]:
            same_obj = a.obj == b.obj
            diff_txn = a.i != b.i
            conflict = a.op == WRITE or b.op == WRITE
            if same_obj and diff_txn and conflict:
                G.add_edge(a.i, b.i)
    return G

def draw(G):
    """Prettily draw a networkx graph G."""
    plt.figure()
    color_range = np.linspace(0, 1, len(G.nodes()))
    labels = {n: "$T_{{{}}}$".format(n) for n in G}
    pos = nx.spectral_layout(G)
    kwargs = {
        "alpha": 1.0,
        "cmap": plt.get_cmap("Dark2"), # http://bit.ly/1ItQDgE
        "font_color": "w",
        "font_size": 40,
        "labels": labels,
        "node_color": color_range,
        "node_size": 10000,
        "pos": pos,                    # http://bit.ly/1DAnT4y
        "width": 4.0,
        "with_labels": True,
    }
    nx.draw(G, **kwargs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
