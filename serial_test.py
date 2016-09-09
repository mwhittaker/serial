from action import *
import matplotlib.pyplot as plt
import networkx as nx
import serial
import unittest

class SerialTest(unittest.TestCase):
    def setUp(self):
        self.schedule1 = [
            r(1, A),
            w(1, A),
                     r(2, B),
                     w(2, B),
            r(1, C),
            w(1, C),
        ]

        self.schedule2 = [
            r(1, A),
            w(1, A),
                       r(2, B),
                       w(2, B),
            r(1, C),
            w(1, C),
            commit(1),
                       commit(2),
        ]

        self.schedule3 = [
            r(1, A),
            w(1, A),
                      r(2, B),
                      w(2, B),
            r(1, C),
            w(1, C),
            abort(1),
                      abort(2),
        ]

        self.schedule4 = [
            r(1, A),
            w(1, A),
                       r(2, A),
                       w(2, A),
            r(1, B),
            w(1, B),
                       r(1, B),
                       w(1, B),
            commit(1),
                       commit(2),
        ]

        self.schedule5 = [
            r(1, A),
                       w(2, A),
                       commit(2),
            w(1, A),
            commit(1),
                                  w(3, A),
                                  commit(3)
        ]

        self.schedule6 = [
            w(1, A),
            r(1, A),
            commit(1),
        ]

        self.schedule7 = [
                      w(2, A),
                      abort(2),
            r(1, A),
            commit(1),
        ]

        # page 574
        self.exercise1 = [r(1,X), r(2,X), w(1,X), w(2,X)]
        self.exercise2 = [w(1,X), r(2,Y), r(1,Y), r(2,X)]
        self.exercise3 = [r(1,X), r(2,Y), w(3,X), r(2,X), r(1,Y)]
        self.exercise4 = [r(1,X), r(1,Y), w(1,X), r(2,Y), w(3,Y), w(1,X), r(2,Y)]
        self.exercise5 = [r(1,X), w(2,X), w(1,X), abort(2), commit(1)]
        self.exercise6 = [r(1,X), w(2,X), w(1,X), commit(2), commit(1)]
        self.exercise7 = [w(1,X), r(2,X), w(1,X), abort(2), commit(1)]
        self.exercise8 = [w(1,X), r(2,X), w(1,X), commit(2), commit(1)]
        self.exercise9 = [w(1,X), r(2,X), w(1,X), commit(2), abort(1)]
        self.exercise10 = [r(2,X), w(3,X), commit(3), w(1,Y), commit(1), r(2,Y), w(2,Z), commit(2)]
        self.exercise11 = [r(1,X), w(2,X), commit(2), w(1,X), commit(1), r(3,X), commit(3)]
        self.exercise12 = [r(1,X), w(2,X), w(1,X), r(3,X), commit(1), commit(2), commit(3)]

    def test_view_serializable(self):
        view_serializable = [
            self.schedule1,
            self.schedule2,
            self.schedule3,
            self.schedule4,
            self.schedule5,

            self.exercise2,
            self.exercise3,
            self.exercise5,
            self.exercise7,
            self.exercise9,
            self.exercise10,
        ]
        for s in view_serializable:
            self.assertTrue(serial.view_serializable(s), s)

        not_view_serializable = [
            self.exercise1,
            self.exercise4,
            self.exercise6,
            self.exercise8,
            self.exercise11,
            self.exercise12,
        ]
        for s in not_view_serializable:
            self.assertFalse(serial.view_serializable(s), s)

    def test_conflict_serializable(self):
        conflict_serializable = [
            self.schedule1,
            self.schedule2,
            self.schedule3,
            self.schedule4,

            self.exercise2,
            self.exercise3,
            self.exercise5,
            self.exercise7,
            self.exercise9,
            self.exercise10,
        ]
        for s in conflict_serializable:
            self.assertTrue(serial.conflict_serializable(s), s)

        not_conflict_serializable = [
            self.schedule5,

            self.exercise1,
            self.exercise4,
            self.exercise6,
            self.exercise8,
            self.exercise11,
            self.exercise12,
        ]
        for s in not_conflict_serializable:
            self.assertFalse(serial.conflict_serializable(s), s)

    def test_recoverable(self):
        recoverable = [
            self.schedule6,
            self.schedule7,

            self.exercise1,
            self.exercise2,
            self.exercise5,
            self.exercise6,
            self.exercise7,
            self.exercise10,
            self.exercise11,
            self.exercise12,
        ]
        for s in recoverable:
            self.assertTrue(serial.recoverable(s), s)

        not_recoverable = [
            self.exercise3,
            self.exercise4,
            self.exercise8,
            self.exercise9,
        ]
        for s in not_recoverable:
            self.assertFalse(serial.recoverable(s), s)

    def test_aca(self):
        aca = [
            self.schedule6,
            self.schedule7,

            self.exercise1,
            self.exercise5,
            self.exercise6,
            self.exercise10,
            self.exercise11,
        ]
        for s in aca:
            self.assertTrue(serial.aca(s), s)

        not_aca = [
            self.exercise2,
            self.exercise3,
            self.exercise4,
            self.exercise7,
            self.exercise8,
            self.exercise9,
            self.exercise12,
        ]
        for s in not_aca:
            self.assertFalse(serial.aca(s), s)

    def test_strict(self):
        strict = [
            self.schedule6,
            self.schedule7,

            self.exercise10,
            self.exercise11,
        ]
        for s in strict:
            self.assertTrue(serial.strict(s), s)

        not_strict = [
            self.exercise1,
            self.exercise2,
            self.exercise3,
            self.exercise4,
            self.exercise5,
            self.exercise6,
            self.exercise7,
            self.exercise8,
            self.exercise9,
            self.exercise12,
        ]
        for s in not_strict:
            self.assertFalse(serial.strict(s), s)

    def assertGraphsEq(self, G1, G2):
        self.assertTrue(serial.graphs_eq(G1, G2), msg="{} != {}".format(G1, G2))

    def test_conflict_graph(self):
        expected = nx.DiGraph()
        expected.add_nodes_from([1, 2])
        self.assertGraphsEq(expected, serial.conflict_graph(self.schedule1))
        self.assertGraphsEq(expected, serial.conflict_graph(self.schedule2))

        expected = nx.DiGraph()
        self.assertGraphsEq(expected, serial.conflict_graph(self.schedule3))

        expected = nx.DiGraph()
        expected.add_nodes_from([1, 2])
        expected.add_edges_from([(1, 2)])
        self.assertGraphsEq(expected, serial.conflict_graph(self.schedule4))

    def test_tex(self):
        exercises = [
            self.exercise1,
            self.exercise2,
            self.exercise3,
            self.exercise4,
            self.exercise5,
            self.exercise6,
            self.exercise7,
            self.exercise8,
            self.exercise9,
            self.exercise10,
            self.exercise11,
            self.exercise12,
        ]
        for (i, s) in enumerate(exercises, 1):
            with open("exercise{}.tex".format(i), "w") as f:
                f.write(serial.tex(s) + "\n")

    def test_draw(self):
        exercises = [
            self.exercise1,
            self.exercise2,
            self.exercise3,
            self.exercise4,
            self.exercise5,
            self.exercise6,
            self.exercise7,
            self.exercise8,
            self.exercise9,
            self.exercise10,
            self.exercise11,
            self.exercise12,
        ]
        for (i, s) in enumerate(exercises, 1):
            serial.draw(serial.conflict_graph(s))
            plt.savefig("exercise{}.pdf".format(i))
            plt.close()

if __name__ == "__main__":
    unittest.main()
