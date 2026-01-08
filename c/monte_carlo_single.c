#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include "xoshiro256.h"

// 理論上の円周率
#define PI_THEORETICAL 3.141592653589793238462643383279502884197

/**
 * モンテカルロ法で円周率を計算
 * 
 * @param iterations 試行回数
 * @param pi_estimate 円周率の推定値（出力）
 * @param error 誤差（出力）
 */
void calculate_pi(uint64_t iterations, double *pi_estimate, double *error) {
    xoshiro256_t rng;
    xoshiro256_init(&rng, 12345);  // 固定シード
    
    uint64_t inside_circle = 0;
    
    for (uint64_t i = 0; i < iterations; i++) {
        // 0.0以上1.0未満の乱数を生成
        double x = xoshiro256_next_double(&rng);
        double y = xoshiro256_next_double(&rng);
        
        // 単位円内か判定（x^2 + y^2 <= 1）
        if (x * x + y * y <= 1.0) {
            inside_circle++;
        }
    }
    
    // π ≈ 4 × (円内の点数) / (総試行回数)
    *pi_estimate = 4.0 * inside_circle / iterations;
    *error = fabs(*pi_estimate - PI_THEORETICAL);
}

int main(void) {
    const uint64_t iterations = 100000000ULL;
    
    // 実行時間の測定
    clock_t start = clock();
    double pi_estimate, error;
    calculate_pi(iterations, &pi_estimate, &error);
    clock_t end = clock();
    
    double elapsed_ms = ((double)(end - start) / CLOCKS_PER_SEC) * 1000.0;
    
    // 結果をJSON形式で出力
    printf("{\n");
    printf("  \"language\": \"C\",\n");
    printf("  \"variant\": \"standard\",\n");
    printf("  \"version\": \"C99\",\n");
    printf("  \"mode\": \"single\",\n");
    printf("  \"iterations\": %llu,\n", iterations);
    printf("  \"pi_estimate\": %.15f,\n", pi_estimate);
    printf("  \"error\": %.15f,\n", error);
    printf("  \"time_ms\": %.2f,\n", elapsed_ms);
    printf("  \"memory_mb\": 0.0,\n");  // runner.pyで測定
    printf("  \"cache_misses\": 0,\n");  // runner.pyで測定
    printf("  \"lines_of_code\": 0,\n");  // runner.pyで計算
    printf("  \"compiler_flags\": \"-O3 -march=native -flto\",\n");
    printf("  \"cpu_model\": \"N/A\",\n");
    printf("  \"cpu_cores\": %d,\n", 1);
    printf("  \"thread_count\": 1,\n");
    printf("  \"os\": \"N/A\",\n");
    printf("  \"os_version\": \"N/A\",\n");
    printf("  \"compiler\": \"GCC/Clang\",\n");
    printf("  \"simd_detected\": false,\n");
    printf("  \"simd_instructions\": []\n");
    printf("}\n");
    
    return 0;
}

