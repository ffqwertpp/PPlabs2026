# Умножение квадратных матриц (C++) с автоматической верификацией

## Структура
```
src/matmul.cpp            программа: читает A и B, считает C = A*B, пишет результат и метрики
tools/generate.py         генератор случайных матриц
tools/verify.py           верификация через NumPy (A @ B)
tools/run_experiments.py  серия экспериментов: генерация -> запуск -> проверка -> таблица
data/                     сгенерированные матрицы (в git не попадают)
report/lab1/              results.csv и results.md с результатами замеров
CMakeLists.txt            сборка
```

## Сборка (Windows / Linux)
```
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```
Исполняемый файл: `build/matmul` (Linux/MinGW), `build/matmul.exe` или `build/Release/matmul.exe` (Visual Studio).

## Запуск вручную
```
python tools/generate.py 500 data/A.txt 1
python tools/generate.py 500 data/B.txt 2
build/matmul data/A.txt data/B.txt data/C.txt blocked     # naive | ikj | blocked
python tools/verify.py data/A.txt data/B.txt data/C.txt   # код возврата 0 = верно
```

## Серия экспериментов
```
python tools/run_experiments.py
python tools/run_experiments.py --sizes 128 256 512 --repeats 5
python tools/run_experiments.py --exe build/Release/matmul.exe
```
Для каждого N и алгоритма берётся медиана времени по `--repeats` запускам, считается ускорение относительно `naive`, каждый результат проверяется `verify.py`. Итог — `report/lab1/results.csv` и `results.md`. Колонка `threads` пока всегда 1 (потоки появятся в следующих лабораторных).

## Форматы файлов
Входной: первая строка — N, затем N строк по N чисел.
Выходной: строки-заголовок `# ...` (размер, алгоритм, время, FLOP, GFLOPS, память), затем матрица N×N. Заголовок с `#` читается `numpy.loadtxt` и Matlab (`readmatrix(..., 'CommentStyle', '#')`).

## Алгоритмы
- `naive` — классический i-j-k (много промахов кэша из-за обхода B по столбцам);
- `ikj` — перестановка циклов, последовательный доступ к памяти;
- `blocked` — блочное умножение, блок 64×64.

## Верификация
Критерий: `||C - C_ref||_F / ||C_ref||_F <= 1e-12`. Для double ошибка порядка 1e-16…1e-15 (разный порядок суммирования).
Matlab: `A=readmatrix('A.txt','NumHeaderLines',1); B=readmatrix('B.txt','NumHeaderLines',1); C=readmatrix('C.txt','CommentStyle','#'); norm(C-A*B,'fro')/norm(A*B,'fro')`
