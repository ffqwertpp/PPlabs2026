// Умножение двух квадратных матриц: C = A * B
//
// Использование:
//   ./matmul A.txt B.txt C.txt [naive|ikj|blocked]
//
// Формат входных файлов:
//   первая строка: N (размер матрицы)
//   далее N строк по N чисел (double), разделённых пробелами
//
// Формат выходного файла:
//   строки-заголовок, начинающиеся с '#' (размер, алгоритм, время, ...),
//   затем N строк по N чисел результирующей матрицы.
//   (комментарии '#' понимают numpy.loadtxt и Matlab/Octave)

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

using Matrix = std::vector<double>;  // хранение по строкам: a[i*n + j]

static bool read_matrix(const std::string& path, Matrix& m, size_t& n) {
    std::ifstream in(path);
    if (!in) {
        std::cerr << "Не удалось открыть файл: " << path << "\n";
        return false;
    }
    if (!(in >> n) || n == 0) {
        std::cerr << "Некорректный размер матрицы в файле " << path << "\n";
        return false;
    }
    m.assign(n * n, 0.0);
    for (size_t i = 0; i < n * n; ++i) {
        if (!(in >> m[i])) {
            std::cerr << "В файле " << path << " недостаточно данных: ожидалось "
                      << n * n << " чисел, прочитано " << i << "\n";
            return false;
        }
    }
    return true;
}

// Классический алгоритм i-j-k. Плохо использует кэш (обход B по столбцам).
static void mul_naive(const Matrix& A, const Matrix& B, Matrix& C, size_t n) {
    for (size_t i = 0; i < n; ++i)
        for (size_t j = 0; j < n; ++j) {
            double s = 0.0;
            for (size_t k = 0; k < n; ++k) s += A[i * n + k] * B[k * n + j];
            C[i * n + j] = s;
        }
}

// Перестановка циклов i-k-j: все обращения к памяти последовательные.
static void mul_ikj(const Matrix& A, const Matrix& B, Matrix& C, size_t n) {
    for (size_t i = 0; i < n; ++i)
        for (size_t k = 0; k < n; ++k) {
            const double a = A[i * n + k];
            for (size_t j = 0; j < n; ++j) C[i * n + j] += a * B[k * n + j];
        }
}

// Блочное умножение: блоки помещаются в кэш.
static void mul_blocked(const Matrix& A, const Matrix& B, Matrix& C, size_t n,
                        size_t bs = 64) {
    for (size_t ii = 0; ii < n; ii += bs)
        for (size_t kk = 0; kk < n; kk += bs)
            for (size_t jj = 0; jj < n; jj += bs) {
                const size_t i_end = std::min(ii + bs, n);
                const size_t k_end = std::min(kk + bs, n);
                const size_t j_end = std::min(jj + bs, n);
                for (size_t i = ii; i < i_end; ++i)
                    for (size_t k = kk; k < k_end; ++k) {
                        const double a = A[i * n + k];
                        for (size_t j = jj; j < j_end; ++j)
                            C[i * n + j] += a * B[k * n + j];
                    }
            }
}

int main(int argc, char** argv) {
    if (argc < 4) {
        std::cerr << "Использование: " << argv[0]
                  << " A.txt B.txt C.txt [naive|ikj|blocked]\n";
        return 1;
    }
    const std::string pathA = argv[1], pathB = argv[2], pathC = argv[3];
    const std::string algo = (argc >= 5) ? argv[4] : "blocked";
    if (algo != "naive" && algo != "ikj" && algo != "blocked") {
        std::cerr << "Неизвестный алгоритм: " << algo << "\n";
        return 1;
    }

    Matrix A, B;
    size_t nA = 0, nB = 0;
    if (!read_matrix(pathA, A, nA) || !read_matrix(pathB, B, nB)) return 1;
    if (nA != nB) {
        std::cerr << "Размеры матриц не совпадают: " << nA << " и " << nB << "\n";
        return 1;
    }
    const size_t n = nA;
    Matrix C(n * n, 0.0);

    // Замеряем только само умножение (без ввода-вывода)
    const auto t0 = std::chrono::steady_clock::now();
    if (algo == "naive") mul_naive(A, B, C, n);
    else if (algo == "ikj") mul_ikj(A, B, C, n);
    else mul_blocked(A, B, C, n);
    const auto t1 = std::chrono::steady_clock::now();

    const double sec = std::chrono::duration<double>(t1 - t0).count();
    const double flops = 2.0 * n * n * n;  // n^3 умножений + n^3 сложений
    const double gflops = sec > 0 ? flops / sec / 1e9 : 0.0;
    const double mem_mb = 3.0 * n * n * sizeof(double) / (1024.0 * 1024.0);

    std::ofstream out(pathC);
    if (!out) {
        std::cerr << "Не удалось создать файл: " << pathC << "\n";
        return 1;
    }
    out << std::setprecision(17);
    out << "# matrix_size_N: " << n << "\n";
    out << "# elements: " << n * n << "\n";
    out << "# algorithm: " << algo << "\n";
    out << "# time_seconds: " << sec << "\n";
    out << "# operations_flop: " << flops << "\n";
    out << "# performance_GFLOPS: " << gflops << "\n";
    out << "# memory_MB (A+B+C): " << mem_mb << "\n";
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) out << C[i * n + j] << (j + 1 < n ? " " : "");
        out << "\n";
    }

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "N=" << n << " algo=" << algo << " time=" << sec << " s"
              << " perf=" << std::setprecision(3) << gflops << " GFLOPS"
              << " mem=" << mem_mb << " MB\n";
    return 0;
}
