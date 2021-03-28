import random
from copy import deepcopy
from timeit import default_timer
from typing import List


class Bucket:
    def __init__(self, number, count):
        self.number = number
        self.count = count

    def is_complete(self) -> bool:
        return self.number == self.count


def fix_previous(previous: List[int], count_empty: int) -> List[int]:
    for i in range(3):
        if count_empty == i and i in previous:
            previous.remove(i)
    return previous


class Generator:
    def __init__(self, rows: int, cols: int, range_values: (int, int)):
        self.rows = rows
        self.cols = cols
        self.range_values = range_values
        self.solution = self.generate_solution()
        self.puzzle = self.generate_puzzle()

    def generate_empty_puzzle(self) -> List[List]:
        puzzle = []
        for i in range(self.rows):
            puzzle.append([])
            for j in range(self.cols):
                puzzle[i].append(0)
        return puzzle

    def generate_solution(self) -> List[List[int]]:
        puzzle = self.generate_empty_puzzle()
        is_reversed = False
        rnd_cell = random.randint(*self.range_values)
        while rnd_cell > self.rows * self.cols:
            rnd_cell = random.randint(*self.range_values)
        bucket = Bucket(rnd_cell, 0)
        previous = list()
        count_empty = self.rows * self.cols

        if self.cols <= self.rows:
            previous_len = self.rows // 2 + 1
        else:
            previous_len = self.cols // 2 + 1

        for i in range(self.rows):
            rng = (0, self.cols, 1) if not is_reversed else (
                self.cols - 1, -1, -1)
            is_reversed = not is_reversed
            for j in range(*rng):
                if len(previous) >= previous_len:
                    previous.remove(previous[0])
                puzzle[i][j] = self.fill_cell(
                    bucket,
                    previous,
                    count_empty
                )
                count_empty -= 1
        return puzzle

    def fill_cell(self, bucket: Bucket, previous: List[int],
                  count_empty: int) -> int:
        if bucket.is_complete():
            result = self.fill_new_bucket(bucket, previous, count_empty)
            while not result:
                result = self.fill_new_bucket(bucket, previous, count_empty)
            return result
        else:
            bucket.count += 1
            return bucket.number

    def fill_new_bucket(self, bucket: Bucket, previous: List[int],
                        count_empty: int, ranges=None) -> int:
        previous.append(bucket.number)
        if not ranges:
            ranges = self.range_values
        new_cell = random.randint(*ranges)
        t = default_timer()
        while new_cell == previous[-1]:
            new_cell = random.randint(*ranges)
        while (new_cell in previous) or (count_empty < new_cell):
            if default_timer() - t < 0.005:
                # previous = fix_previous(previous, count_empty)
                new_cell = random.randint(*ranges)
                if count_empty <= ranges[1] and new_cell >= count_empty:
                    new_cell = count_empty
            else:
                break
        cell = new_cell
        bucket.number = cell
        bucket.count = 1
        return cell

    def generate_puzzle(self) -> List[List[int]]:
        puzzle = deepcopy(self.solution)
        del_percent = 25 / 100
        prev = 0
        is_reversed = False
        prev_skip = True

        for i in range(self.rows):
            rng = (0, self.cols, 1) if not is_reversed else (
                self.cols - 1, -1, -1)
            is_reversed = not is_reversed
            for j in range(*rng):
                if puzzle[i][j] != prev:
                    cell = puzzle[i][j]
                    deleted = del_percent * cell
                    count = cell
                    prev = cell
                    del_count = 0
                else:
                    count -= 1
                    if (count >= deleted) and not prev_skip:
                        prev_skip = True
                        continue
                    if del_count < deleted:
                        puzzle[i][j] = '-'
                        del_count += 1
        return puzzle

    def get_fillomino_string(self, puzzle: List[List[int]]) -> str:
        res = f"{self.rows}\n{self.cols}\n"
        for i in range(self.rows):
            row = map(str, puzzle[i])
            res += ' '.join(row)
            res += '\n'
        return res[:-1]
