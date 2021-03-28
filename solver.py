#!/usr/bin/env python3
import argparse
import sys

from arch.fillomino import Fillomino, get_from_string, file_reader
from arch.fillomino_solver import FillominoSolver
from arch.views.MainWindow import MainWindow


def main():
    parser = argparse.ArgumentParser(description="Fillomino solver")
    parser.add_argument('-f', '--file', type=str, default="",
                        help="Path to file with puzzle")
    parser.add_argument('-g', '--gui', action='store_true',
                        help='Open with GUI')

    args = parser.parse_args()
    file = args.file
    if file:
        write_to_console(file)

    if args.gui:
        app = MainWindow(file)
        sys.exit(app.exec_())


def write_to_console(file):
    problem = Fillomino(*get_from_string(file, file_reader),
                        True)
    solver = FillominoSolver(problem)
    solver.solve()
    try:
        it = solver.get_next_model()
        n = next(it)
        print("Solution:")
        print(str(n))
    except StopIteration:
        print("No solutions")


if __name__ == '__main__':
    main()
