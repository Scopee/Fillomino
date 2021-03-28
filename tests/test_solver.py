import unittest
from arch.fillomino import Fillomino, get_from_string, string_reader
from arch.fillomino_solver import FillominoSolver


class TestSolver(unittest.TestCase):
    def test_solve_2x2(self):
        s = """2
2
4 -
- -
"""
        expected = [[4, 4], [4, 4]]

        self.assert_values(expected, s)

    def test_solve_5x5(self):
        s = """5
        5
        - 1 - - 5
4 - 4 5 5
5 5 7 - 1
1 5 7 - -
5 - 1 7 7"""
        expected = [[4, 1, 5, 5, 5], [4, 4, 4, 5, 5], [5, 5, 7, 7, 1],
                    [1, 5, 7, 7, 7], [5, 5, 1, 7, 7]]
        self.assert_values(expected, s)

    def test_empty(self):
        s = """0
0
"""
        problem = Fillomino(*get_from_string(s, string_reader), True)
        solver = FillominoSolver(problem)
        solver.solve()
        self.assertTrue(problem.err)

    def test_wrong_puzzle(self):
        s = """1
1
2"""
        problem = Fillomino(*get_from_string(s, string_reader), True)
        solver = FillominoSolver(problem)
        solver.solve()
        self.assertRaises(StopIteration, lambda x: next(x),
                          solver.get_next_model())

    def test_rectangular_puzzle(self):
        s = """1
3
1 - 2"""

        expected = [[1, 2, 2]]
        self.assert_values(expected, s)

    def assert_values(self, expected, initial):
        expected = Fillomino(len(expected), len(expected[0]), expected)
        problem = Fillomino(*get_from_string(initial, string_reader), True)
        solver = FillominoSolver(problem)
        solver.solve()
        self.assertEqual(expected, next(solver.get_next_model()))
