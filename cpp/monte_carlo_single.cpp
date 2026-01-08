#include <iostream>
#include <iomanip>
#include <cmath>
#include <ctime>
#include "xoshiro256.hpp"

// 理論上の円周率
const double PI_THEORETICAL = 3.141592653589793238462643383279502884197;

/**
 * モンテカルロ法で円周率を計算
 * 
 * @param iterations 試行回数
 * @param pi_estimate 円周率の推定値（出力）
 * @param error 誤差（出力）
 */
void calculate_pi(uint64_t iterations, double &pi_estimate, double &error) {
    Xoshiro256 rng(12345);  // 固定シード
    
    uint64_t inside_circle = 0;
    
    for (uint64_t i = 0; i < iterations; i++) {
        // 0.0以上1.0未満の乱数を生成
        double x = rng.next_double();
        double y = rng.next_double();
        
        // 単位円内か判定（x^2 + y^2 <= 1）
        if (x * x + y * y <= 1.0) {
            inside_circle++;
        }
    }
    
    // π ≈ 4 × (円内の点数) / (総試行回数)
    pi_estimate = 4.0 * inside_circle / iterations;
    error = std::abs(pi_estimate - PI_THEORETICAL);
}

int main() {
    const uint64_t iterations = 100000000ULL;
    
    // 実行時間の測定
    std::clock_t start = std::clock();
    double pi_estimate, error;
    calculate_pi(iterations, pi_estimate, error);
    std::clock_t end = std::clock();
    
    double elapsed_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    
    // 結果をJSON形式で出力
    std::cout << std::fixed << std::setprecision(15);
    std::cout << "{\n";
    std::cout << "  \"language\": \"C++\",\n";
    std::cout << "  \"variant\": \"standard\",\n";
    std::cout << "  \"version\": \"C++17\",\n";
    std::cout << "  \"mode\": \"single\",\n";
    std::cout << "  \"iterations\": " << iterations << ",\n";
    std::cout << "  \"pi_estimate\": " << pi_estimate << ",\n";
    std::cout << "  \"error\": " << error << ",\n";
    std::cout << std::setprecision(2);
    std::cout << "  \"time_ms\": " << elapsed_ms << ",\n";
    std::cout << "  \"memory_mb\": 0.0,\n";  // runner.pyで測定
    std::cout << "  \"cache_misses\": 0,\n";  // runner.pyで測定
    std::cout << "  \"lines_of_code\": 0,\n";  // runner.pyで計算
    std::cout << "  \"compiler_flags\": \"-O3 -march=native -flto\",\n";
    std::cout << "  \"cpu_model\": \"N/A\",\n";
    std::cout << "  \"cpu_cores\": 1,\n";
    std::cout << "  \"thread_count\": 1,\n";
    std::cout << "  \"os\": \"N/A\",\n";
    std::cout << "  \"os_version\": \"N/A\",\n";
    std::cout << "  \"compiler\": \"GCC/Clang\",\n";
    std::cout << "  \"simd_detected\": false,\n";
    std::cout << "  \"simd_instructions\": []\n";
    std::cout << "}\n";
    
    return 0;
}

