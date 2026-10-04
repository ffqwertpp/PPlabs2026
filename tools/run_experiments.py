#!/usr/bin/env python3
"""Серия экспериментов: генерация -> умножение (C++) -> верификация (NumPy) -> таблица.

Для каждого размера N и каждого алгоритма программа запускается --repeats раз,
в таблицу попадает медиана времени. Ускорение считается относительно naive.
Каждый результат автоматически проверяется tools/verify.py.

Использование (из корня проекта):
    python tools/run_experiments.py
    python tools/run_experiments.py --sizes 128 256 512 --repeats 5
    python tools/run_experiments.py --exe build/Release/matmul.exe   # Visual Studio

Результаты: report/lab1/results.csv и report/lab1/results.md
Код возврата: 0 — все проверки пройдены, 1 — есть расхождения.
"""
import argparse
import csv
import statistics
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import write_matrix  # noqa: E402

ALGOS = ["naive", "ikj", "blocked"]


def find_exe(user_path):
    if user_path:
        return Path(user_path)
    for cand in ("build/matmul", "build/matmul.exe",
                 "build/Release/matmul.exe", "build/Debug/matmul.exe"):
        if (ROOT / cand).exists():
            return ROOT / cand
    sys.exit("Не найден исполняемый файл matmul. Соберите проект:\n"
             "  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release\n"
             "  cmake --build build --config Release\n"
             "или укажите путь через --exe")


def read_header(path):
    info = {}
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                break
            key, val = line[1:].split(":", 1)
            info[key.strip()] = val.strip()
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", type=int, nargs="+",
                    default=[64, 128, 256, 512, 1024])
    ap.add_argument("--algos", nargs="+", default=ALGOS, choices=ALGOS)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--exe", default=None)
    args = ap.parse_args()

    exe = find_exe(args.exe)
    data = ROOT / "data"
    out_dir = ROOT / "report" / "lab1"
    data.mkdir(exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows, all_ok = [], True
    for n in args.sizes:
        a, b = data / f"A_{n}.txt", data / f"B_{n}.txt"
        rng = np.random.default_rng(n)
        write_matrix(a, rng.uniform(-10, 10, (n, n)))
        write_matrix(b, rng.uniform(-10, 10, (n, n)))
        naive_time = None
        for algo in args.algos:
            c = data / f"C_{n}_{algo}.txt"
            times = []
            for _ in range(args.repeats):
                subprocess.check_call([str(exe), str(a), str(b), str(c), algo],
                                      stdout=subprocess.DEVNULL)
                times.append(float(read_header(c)["time_seconds"]))
            t = statistics.median(times)
            if algo == "naive":
                naive_time = t
            v = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "verify.py"),
                 str(a), str(b), str(c)], capture_output=True, text=True)
            ok = v.returncode == 0
            all_ok &= ok
            print(v.stdout.strip(), f"[{algo}]")
            h = read_header(c)
            rows.append({
                "N": n,
                "algorithm": algo,
                "threads": 1,
                "time_s": round(t, 6),
                "speedup_vs_naive": (round(naive_time / t, 2)
                                     if naive_time and t > 0 else ""),
                "GFLOPS": round(float(h["operations_flop"]) / t / 1e9, 3),
                "memory_MB": round(float(h["memory_MB (A+B+C)"]), 2),
                "verified": "OK" if ok else "FAIL",
            })

    with open(out_dir / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    cols = list(rows[0].keys())
    with open(out_dir / "results.md", "w", encoding="utf-8") as f:
        f.write(f"Медиана по {args.repeats} запускам.\n\n")
        f.write("| " + " | ".join(cols) + " |\n")
        f.write("|" + "|".join("---" for _ in cols) + "|\n")
        for r in rows:
            f.write("| " + " | ".join(str(r[c]) for c in cols) + " |\n")

    print("\n" + "\t".join(cols))
    for r in rows:
        print("\t".join(str(r[c]) for c in cols))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
