#!/usr/bin/env python3
"""Генерация случайной квадратной матрицы в формат, понятный matmul.

Использование: python3 gen_matrix.py N out.txt [seed]
"""
import sys

import numpy as np


def write_matrix(path, m):
    with open(path, "w") as f:
        f.write(f"{m.shape[0]}\n")
        np.savetxt(f, m, fmt="%.17g")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    n = int(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else None
    rng = np.random.default_rng(seed)
    write_matrix(sys.argv[2], rng.uniform(-10.0, 10.0, size=(n, n)))
