#!/usr/bin/env python3
"""Автоматическая верификация результата matmul с помощью NumPy.

Использование: python3 verify.py A.txt B.txt C.txt [tol]

Эталон: C_ref = A @ B (NumPy/BLAS). Сравнение по относительной норме Фробениуса:
    ||C - C_ref||_F / ||C_ref||_F  <=  tol   (по умолчанию 1e-12)
Код возврата: 0 — верно, 1 — ошибка.
"""
import sys

import numpy as np


def load_input(path):
    with open(path) as f:
        n = int(f.readline())
        return np.loadtxt(f, ndmin=2).reshape(n, n)


def load_result(path):
    return np.loadtxt(path, comments="#", ndmin=2)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    tol = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-12
    A, B = load_input(sys.argv[1]), load_input(sys.argv[2])
    C = load_result(sys.argv[3])
    if C.shape != A.shape:
        print(f"FAIL: размер результата {C.shape}, ожидался {A.shape}")
        return 1
    ref = A @ B
    rel = np.linalg.norm(C - ref) / np.linalg.norm(ref)
    max_abs = np.max(np.abs(C - ref))
    ok = rel <= tol
    print(f"{'OK  ' if ok else 'FAIL'} N={A.shape[0]} rel_err={rel:.3e} "
          f"max_abs_err={max_abs:.3e} (tol={tol:g})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
