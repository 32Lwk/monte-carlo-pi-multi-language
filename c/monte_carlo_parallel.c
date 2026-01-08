#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <pthread.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif
#include "xoshiro256.h"

// 理論上の円周率
#define PI_THEORETICAL 3.141592653589793238462643383279502884197

// シードの加算幅を大きくする（推奨方式）
#define SEED_MULTIPLIER 0x9E3779B97F4A7C15ULL  // 黄金比の逆数（64ビット）

/**
 * スレッドごとの計算用構造体
 */
typedef struct {
    uint64_t iterations_per_thread;
    int thread_id;
    uint64_t base_seed;
    uint64_t inside_circle;
} thread_data_t;

/**
 * スレッドごとの円周率計算
 * 
 * @param arg thread_data_tへのポインタ
 * @return NULL
 */
void *calculate_pi_thread(void *arg) {
    thread_data_t *data = (thread_data_t *)arg;
    
    // 推奨方式: シードの加算幅を大きくする
    uint64_t thread_seed = data->base_seed + (data->thread_id * SEED_MULTIPLIER);
    xoshiro256_t rng;
    xoshiro256_init(&rng, thread_seed);  // スレッドごとに独立したインスタンス
    
    uint64_t inside_circle = 0;
    
    for (uint64_t i = 0; i < data->iterations_per_thread; i++) {
        // 0.0以上1.0未満の乱数を生成
        double x = xoshiro256_next_double(&rng);
        double y = xoshiro256_next_double(&rng);
        
        // 単位円内か判定（x^2 + y^2 <= 1）
        if (x * x + y * y <= 1.0) {
            inside_circle++;
        }
    }
    
    data->inside_circle = inside_circle;
    return NULL;
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
                 double *pi_estimate, double *error) {
    uint64_t iterations_per_thread = iterations / num_threads;
    uint64_t base_seed = 12345;
    
    // スレッドとデータを準備
    pthread_t *threads = malloc(num_threads * sizeof(pthread_t));
    thread_data_t *thread_data = malloc(num_threads * sizeof(thread_data_t));
    
    // スレッドを起動
    for (int i = 0; i < num_threads; i++) {
        thread_data[i].iterations_per_thread = iterations_per_thread;
        thread_data[i].thread_id = i;
        thread_data[i].base_seed = base_seed;
        thread_data[i].inside_circle = 0;
        
        pthread_create(&threads[i], NULL, calculate_pi_thread, &thread_data[i]);
    }
    
    // すべてのスレッドの完了を待つ
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // 結果を集計
    uint64_t total_inside = 0;
    for (int i = 0; i < num_threads; i++) {
        total_inside += thread_data[i].inside_circle;
    }
    
    // π ≈ 4 × (円内の点数) / (総試行回数)
    *pi_estimate = 4.0 * total_inside / iterations;
    *error = fabs(*pi_estimate - PI_THEORETICAL);
    
    free(threads);
    free(thread_data);
}

int main(void) {
    const uint64_t iterations = 100000000ULL;
#ifdef _WIN32
    SYSTEM_INFO sysinfo;
    GetSystemInfo(&sysinfo);
    int num_threads = sysinfo.dwNumberOfProcessors;
#else
    int num_threads = sysconf(_SC_NPROCESSORS_ONLN);
#endif
    if (num_threads <= 0) num_threads = 1;
    
    // 実行時間の測定
    clock_t start = clock();
    double pi_estimate, error;
    calculate_pi(iterations, num_threads, &pi_estimate, &error);
    clock_t end = clock();
    
    double elapsed_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    
    // 結果をJSON形式で出力
    printf("{\n");
    printf("  \"language\": \"C\",\n");
    printf("  \"variant\": \"standard\",\n");
    printf("  \"version\": \"C99\",\n");
    printf("  \"mode\": \"parallel\",\n");
    printf("  \"iterations\": %llu,\n", iterations);
    printf("  \"pi_estimate\": %.15f,\n", pi_estimate);
    printf("  \"error\": %.15f,\n", error);
    printf("  \"time_ms\": %.2f,\n", elapsed_ms);
    printf("  \"memory_mb\": 0.0,\n");  // runner.pyで測定
    printf("  \"cache_misses\": 0,\n");  // runner.pyで測定
    printf("  \"lines_of_code\": 0,\n");  // runner.pyで計算
    printf("  \"compiler_flags\": \"-O3 -march=native -flto\",\n");
    printf("  \"cpu_model\": \"N/A\",\n");
    printf("  \"cpu_cores\": %d,\n", num_threads);
    printf("  \"thread_count\": %d,\n", num_threads);
    printf("  \"os\": \"N/A\",\n");
    printf("  \"os_version\": \"N/A\",\n");
    printf("  \"compiler\": \"GCC/Clang\",\n");
    printf("  \"simd_detected\": false,\n");
    printf("  \"simd_instructions\": []\n");
    printf("}\n");
    
    return 0;
}

