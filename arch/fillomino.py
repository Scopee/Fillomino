from itertools import product
from typing import Iterator, Callable, List, Any, Tuple, Union


def string_reader(string: str) -> Iterator[str]:
    for line in string.split('\n'):
        for x in line.split():
            yield x


def file_reader(file: str) -> Iterator[str]:
    with open(file, 'r') as f:
        for line in f:
            for x in line.split():
                yield x


def get_from_string(file: str, reader: Callable[[str], Iterator[str]]) -> (
        int, int, List[Tuple[int, int]]):
    r = reader(file)

    rows = int(next(r))
    cols = int(next(r))

    table = []
    for (i, j) in product(range(rows), range(cols)):
        try:
            v = next(r)
            if v.isdigit():
                table.append((i, j, int(v)))
        except StopIteration:
            return rows, cols, None

    return rows, cols, table


class Fillomino:
    def __init__(self, cols: int, rows: int,
                 matrix: List[List[Union[str, int]]], table=False):
        self.rows, self.cols = cols, rows
        if table:
            self.table = matrix
        else:
            self.table = []
            for i, j in product(range(self.rows), range(self.cols)):
                if not isinstance(matrix[i][j], str):
                    self.table.append((i, j, matrix[i][j]))
        self.err = False if self.table else True

    def __eq__(self, other: Any) -> bool:
        if self.rows != other.rows:
            return False
        if self.cols != other.cols:
            return False
        for i in range(len(self.table)):
            if self.table[i] != other.table[i]:
                return False
        return True

    def __hash__(self) -> int:
        return self.rows + self.cols

    def __str__(self) -> str:
        s = ""
        for row in self.as_array():
            s += " ".join(map(str, row))
            s += "\n"
        return s[:-1]

    def as_array(self):
        res = []
        for i in range(self.rows):
            res.append([])
            for j in range(self.cols):
                res[i].append("-")
        for (i, j, k) in self.table:
            res[i][j] = str(k)
        return res
