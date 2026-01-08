#include <iostream>
#include <iomanip>
#include <cmath>
#include <ctime>
#include <thread>
#include <vector>
#include <algorithm>
#include "xoshiro256.hpp"

// 理論上の円周率
const double PI_THEORETICAL = 3.141592653589793238462643383279502884197;

// シードの加算幅を大きくする（推奨方式）
const uint64_t SEED_MULTIPLIER = 0x9E3779B97F4A7C15ULL;  // 黄金比の逆数（64ビット）

/**
 * スレッドごとの計算用構造体
 */
struct ThreadData {
    uint64_t iterations_per_thread;
    int thread_id;
    uint64_t base_seed;
    uint64_t inside_circle;
};

/**
 * スレッドごとの円周率計算
 * 
 * @param data ThreadDataへのポインタ
 */
void calculate_pi_thread(ThreadData *data) {
    // 推奨方式: シードの加算幅を大きくする
    uint64_t thread_seed = data->base_seed + (data->thread_id * SEED_MULTIPLIER);
    Xoshiro256 rng(thread_seed);  // スレッドごとに独立したインスタンス
    
    uint64_t inside_circle = 0;
    
    for (uint64_t i = 0; i < data->iterations_per_thread; i++) {
        // 0.0以上1.0未満の乱数を生成
        double x = rng.next_double();
        double y = rng.next_double();
        
        // 単位円内か判定（x^2 + y^2 <= 1）
        if (x * x + y * y <= 1.0) {
            inside_circle++;
        }
    }
    
    data->inside_circle = inside_circle;
}

/**
 * モンテカルロ法で円周率を計算（並列化版）
 * 
 * @param iterations 総試行回数
 * @param num_threads スレッド数
 * @param pi_estimate 円周率の推定値（出力）
 * @param error 誤差（出力）
 */
void calculate_pi(uint64_t iterations, int num_threads, 
                 double &pi_estimate, double &error) {
    uint64_t iterations_per_thread = iterations / num_threads;
    uint64_t base_seed = 12345;
    
    // スレッドとデータを準備
    std::vector<std::thread> threads;
    std::vector<ThreadData> thread_data(num_threads);
    
    // スレッドを起動
    for (int i = 0; i < num_threads; i++) {
        thread_data[i].iterations_per_thread = iterations_per_thread;
        thread_data[i].thread_id = i;
        thread_data[i].base_seed = base_seed;
        thread_data[i].inside_circle = 0;
        
        threads.emplace_back(calculate_pi_thread, &thread_data[i]);
    }
    
    // すべてのスレッドの完了を待つ
    for (auto &thread : threads) {
        thread.join();
    }
    
    // 結果を集計
    uint64_t total_inside = 0;
    for (const auto &data : thread_data) {
        total_inside += data.inside_circle;
    }
    
    // π ≈ 4 × (円内の点数) / (総試行回数)
    pi_estimate = 4.0 * total_inside / iterations;
    error = std::abs(pi_estimate - PI_THEORETICAL);
}

int main() {
    const uint64_t iterations = 100000000ULL;
    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 1;
    
    // 実行時間の測定
    std::clock_t start = std::clock();
    double pi_estimate, error;
    calculate_pi(iterations, num_threads, pi_estimate, error);
    std::clock_t end = std::clock();
    
    double elapsed_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    
    // 結果をJSON形式で出力
    std::cout << std::fixed << std::setprecision(15);
    std::cout << "{\n";
    std::cout << "  \"language\": \"C++\",\n";
    std::cout << "  \"variant\": \"standard\",\n";
    std::cout << "  \"version\": \"C++17\",\n";
    std::cout << "  \"mode\": \"parallel\",\n";
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
    std::cout << "  \"cpu_cores\": " << num_threads << ",\n";
    std::cout << "  \"thread_count\": " << num_threads << ",\n";
    std::cout << "  \"os\": \"N/A\",\n";
    std::cout << "  \"os_version\": \"N/A\",\n";
    std::cout << "  \"compiler\": \"GCC/Clang\",\n";
    std::cout << "  \"simd_detected\": false,\n";
    std::cout << "  \"simd_instructions\": []\n";
    std::cout << "}\n";
    
    return 0;
}

