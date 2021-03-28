from itertools import product
from typing import List, Generator, Callable, Tuple, Union

import z3

from arch.fillomino import Fillomino, Iterator


class FillominoSolver:
    def __init__(self, problem: Fillomino):
        self._solver = z3.Solver()
        self._vars = {}
        self._puzzle = problem
        self._count = 0
        self.is_empty = False
        self.solved = False

    def solve(self) -> None:
        if self._puzzle.rows == 0 or self._puzzle.cols == 0:
            self.is_empty = True
            return
        if not self._puzzle.table:
            return
        for (x, y) in self._all_coordinates(self._puzzle.cols):
            v = self._create_z3_variable('e_{}_{}'.format(x, y))
            self._solver.add(z3.Or(v == 0, v == 1))

        for (x, y) in self._all_coordinates(self._puzzle.cols):
            self._solver.add(self._vars[f'e_{x}_{y}']
                             + self._vars[f'e_{y}_{x}'] <= 1)

        self._apply_functions_to_pairs(self._puzzle.cols, self._puzzle.cols,
                                       lambda li, x, y:
                                       li.append(self._vars[f'e_{y}_{x}']),
                                       lambda li, x:
                                       self._solver.add(sum(li) <= 1))

        self._apply_function_to_all_cells(
            lambda x: self._create_z3_variable('n_{}'.format(x)))

        for (i, j, k) in self._puzzle.table:
            x = i * self._puzzle.cols + j
            self._solver.add(self._vars[f'n_{x}'] == k)

        self._apply_function_to_all_cells(
            lambda x: self._create_z3_variable('s_{}'.format(x)))

        self._calculate_size_of_children()

        self._check_size_to_number()

        for (x, y) in self._all_coordinates(self._puzzle.cols):
            self._solver.add(z3.Implies(self._vars[f'e_{x}_{y}'] == 1,
                                        self._vars[f'n_{x}'] == self._vars[
                                            f'n_{y}']))

        self._apply_function_to_all_cells(
            lambda x: self._create_z3_variable('r_{}'.format(x)))

        self._apply_functions_to_pairs(self._puzzle.cols, self._puzzle.cols,
                                       lambda li, x, y: li.append(
                                           self._vars[f'e_{y}_{x}']),
                                       lambda li, x: self._solver.add(
                                           z3.Implies(sum(li) == 0, self._vars[
                                               f'r_{x}'] == x)))

        for (x, y) in self._all_coordinates(self._puzzle.cols):
            self._solver.add(
                z3.Implies(self._vars[f'n_{x}'] == self._vars[f'n_{y}'],
                           self._vars[f'r_{x}'] == self._vars[f'r_{y}']))

        res = self._solver.check()
        if res == z3.sat:
            self.solved = True

    def get_next_model(self) -> Union[Iterator[Fillomino], None]:
        res = []
        models = set()
        while self._solver.check() == z3.sat:
            try:
                model = self._solver.model()
            except z3.z3types.Z3Exception:
                return None
            res.append(model)
            solved = self.get_result(model)
            if solved not in models:
                yield solved
            models.add(solved)
            block = []
            for expr in model:
                if expr.arity() > 0:
                    raise z3.Z3Exception(
                        "uninterpreted functions are not supported")
                c = expr()
                if z3.is_array(
                        c) or c.sort().kind() == z3.Z3_UNINTERPRETED_SORT:
                    raise z3.Z3Exception(
                        "arrays and uninterpreted sorts are not supported")
                block.append(c != model[expr])
            self._solver.add(z3.Or(block))
        return None

    def get_result(self, m: z3.ModelRef) -> Fillomino:
        res = None
        if self.solved:
            res = []
            for i in range(0, self._puzzle.rows * self._puzzle.cols,
                           self._puzzle.cols):
                r = []
                for j in range(self._puzzle.cols):
                    r.append(m[self._vars[f'n_{i + j}']])
                res.append(r)
        return Fillomino(self._puzzle.rows, self._puzzle.cols, res)

    def _all_coordinates(self, cols: int) -> Generator[
            Tuple[int, int], None, None]:
        for (i, j) in product(range(self._puzzle.rows),
                              range(self._puzzle.cols)):
            x = i * cols + j
            for (k, l) in self._get_neighbours(i, j):
                y = k * cols + l
                yield x, y

    def _apply_functions_to_pairs(self, rows: int, cols: int,
                                  inner_fun: Callable[[List, int, int], None],
                                  outer_fun=lambda li, x: None) -> None:
        li = []
        for (i, j) in product(range(self._puzzle.rows),
                              range(self._puzzle.cols)):
            x = i * rows + j
            for (k, l) in self._get_neighbours(i, j):
                y = k * cols + l
                inner_fun(li, x, y)
            outer_fun(li, x)
            li.clear()

    def _apply_function_to_all_cells(self, fun: Callable[[int], None]) -> None:
        for (i, j) in product(range(self._puzzle.rows),
                              range(self._puzzle.cols)):
            x = i * self._puzzle.cols + j
            fun(x)

    def _calculate_size_of_children(self) -> None:
        li = []
        for (i, j) in product(range(self._puzzle.rows),
                              range(self._puzzle.cols)):
            x = i * self._puzzle.cols + j
            for (k, l) in self._get_neighbours(i, j):
                y = k * self._puzzle.cols + l
                li.append(self._vars[f'e_{x}_{y}'])
                li.append(self._vars[f's_{y}'])

            a = 0
            for k in range(0, len(li), 2):
                a += z3.If(li[k] == 1, li[k + 1], 0)
            self._solver.add(self._vars[f's_{x}'] == (1 + a))
            li.clear()

    def _check_size_to_number(self) -> None:
        li = []
        for (i, j) in product(range(self._puzzle.rows),
                              range(self._puzzle.cols)):
            x = i * self._puzzle.cols + j
            for (k, l) in self._get_neighbours(i, j):
                y = k * self._puzzle.cols + l
                li.append(self._vars[f'e_{y}_{x}'])
            s = self._vars['s_{}'.format(x)]
            n = self._vars['n_{}'.format(x)]
            self._solver.add(z3.Implies(sum(li) == 0, s == n))
            li.clear()

    def _create_z3_variable(self, name: str) -> z3.Int:
        t = z3.Int(name)
        self._vars[name] = t
        return t

    def _get_neighbours(self, i: int, j: int) -> List[Tuple[int, int]]:
        neighbours = []
        if i - 1 >= 0:
            neighbours.append((i - 1, j))
        if i + 1 < self._puzzle.rows:
            neighbours.append((i + 1, j))
        if j - 1 >= 0:
            neighbours.append((i, j - 1))
        if j + 1 < self._puzzle.cols:
            neighbours.append((i, j + 1))
        return neighbours
