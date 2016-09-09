from action import *
import unittest

class ActionTest(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(r(1, A), r(1, A))
        self.assertEqual(w(1, A), w(1, A))
        self.assertEqual(commit(1), commit(1))
        self.assertEqual(abort(1), abort(1))

        self.assertNotEqual(r(2, A), r(1, A))
        self.assertNotEqual(w(2, A), w(1, A))
        self.assertNotEqual(commit(2), commit(1))
        self.assertNotEqual(abort(2), abort(1))

    def test_hash(self):
        self.assertEqual(hash(r(1, A)), hash(r(1, A)))
        self.assertEqual(hash(w(1, A)), hash(w(1, A)))
        self.assertEqual(hash(commit(1)), hash(commit(1)))
        self.assertEqual(hash(abort(1)), hash(abort(1)))

        self.assertNotEqual(hash(r(2, A)), hash(r(1, A)))
        self.assertNotEqual(hash(w(2, A)), hash(w(1, A)))
        self.assertNotEqual(hash(commit(2)), hash(commit(1)))
        self.assertNotEqual(hash(abort(2)), hash(abort(1)))

    def test_r(self):
        a = r(1, A)
        self.assertEqual(a.op, READ)
        self.assertEqual(a.i, 1)
        self.assertEqual(a.obj, A)

    def test_w(self):
        a = w(2, A)
        self.assertEqual(a.op, WRITE)
        self.assertEqual(a.i, 2)
        self.assertEqual(a.obj, A)

    def test_commit(self):
        a = commit(3)
        self.assertEqual(a.op, COMMIT)
        self.assertEqual(a.i, 3)
        self.assertIsNone(a.obj)

    def test_abort(self):
        a = abort(4)
        self.assertEqual(a.op, ABORT)
        self.assertEqual(a.i, 4)
        self.assertIsNone(a.obj)

if __name__ == "__main__":
    unittest.main()
