#!/usr/bin/env python3
import argparse

from arch.generator import Generator
from arch.fillomino import Fillomino, get_from_string, string_reader


def main():
    parser = argparse.ArgumentParser(description="Fillomino generator")
    parser.add_argument('cols', type=int, help="Number of columns")
    parser.add_argument('rows', type=int, help="Number of rows")
    parser.add_argument('-f', '--file',
                        type=str, help="File to write solution")
    args = parser.parse_args()
    if args.cols == 0 or args.rows == 0:
        print("Incorrect input!")
        exit(1)
    gen = Generator(args.cols, args.rows, (1, 9))
    puzzle = Fillomino(
        *get_from_string(gen.get_fillomino_string(gen.puzzle), string_reader),
        True)
    print(gen.get_fillomino_string(puzzle.as_array()))
    if args.file:
        with open(args.file, "w") as f:
            f.write(str(Fillomino(
                *get_from_string(gen.get_fillomino_string(gen.solution),
                                 string_reader),
                True)))


if __name__ == '__main__':
    main()
