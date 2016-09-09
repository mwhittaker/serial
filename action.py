"""
Schedules are made up of actions. For example the schedule `R_1(X), W_2(X),
Commit_1, Abort_2` consists of four actions:

    1. Transaction 1 reads object X
    2. Transaction 2 writes object X
    3. Transaction 1 commits
    3. Transaction 2 aborts

This file contains a representation of read, write, commit, and abort actions.
"""

import string

# Useful abbreviations for constructing actions. Instead of writing r(1, "A"),
# if you import these abbreviations, you can instead write r(1, A).
A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z = string.ascii_uppercase

# Enumeration of action types
READ   = 1
WRITE  = 2
COMMIT = 3
ABORT  = 4

class Action(object):
    def __init__(self, op, i, obj=None):
        self.op  = op  # operation:      READ, WRITE, COMMIT, or ABORT
        self.i   = i   # transaction id: 1, 2, 3, ...
        self.obj = obj # object:         A, B, C, ...

    def __eq__(self, other):
        return self.op == other.op and self.i == other.i and self.obj == other.obj

    def __hash__(self):
        return hash((self.op, self.i, self.obj))

    def __str__(self):
        if self.op == READ:
            return "R_{}({})".format(self.i, self.obj)
        elif self.op == WRITE:
            return "W_{}({})".format(self.i, self.obj)
        elif self.op == COMMIT:
            return "Commit_{}".format(self.i)
        elif self.op == ABORT:
            return "Abort_{}".format(self.i)
        else:
            raise ValueError("invalid action type {}".format(self.op))

    def __repr__(self):
        return str(self)

    def tex(self):
        if self.op == READ:
            return "$R_{{{}}}({})$".format(self.i, self.obj)
        elif self.op == WRITE:
            return "$W_{{{}}}({})$".format(self.i, self.obj)
        elif self.op == COMMIT:
            return "$\\text{{Commit}}_{{{}}}$".format(self.i)
        elif self.op == ABORT:
            return "$\\text{{Abort}}_{{{}}}$".format(self.i)
        else:
            raise ValueError("invalid action type {}".format(self.op))

def r(t, obj):
    """
    Constructs a read action.

    >>> r(1, "A")
    R_1(A)
    """
    return Action(READ, t, obj)

def w(t, obj):
    """
    Constructs a write action.

    >>> w(1, "A")
    W_1(A)
    """
    return Action(WRITE, t, obj)

def commit(t):
    """
    Constructs a commit action.

    >>> commit(1)
    Commit_1
    """
    return Action(COMMIT, t)

def abort(t):
    """
    Constructs an abort action.

    >>> abort(1)
    Abort_1
    """
    return Action(ABORT, t)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
