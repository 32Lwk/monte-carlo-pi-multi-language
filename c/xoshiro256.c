#include "xoshiro256.h"

void xoshiro256_init(xoshiro256_t * restrict rng, uint64_t seed) {
    /**
     * シードを4つの状態に分散（SplitMix64アルゴリズムの簡易版）
     * restrictキーワードにより、コンパイラはこのメモリが他のポインタから
     * 書き換えられないと確信し、より積極的な最適化（SIMD化など）を行う
     */
    uint64_t s = seed;
    
    // SplitMix64風の初期化
    for (int i = 0; i < 4; i++) {
        s ^= s >> 30;
        s *= 0xBF58476D1CE4E5B9ULL;
        s ^= s >> 27;
        s *= 0x94D049BB133111EBULL;
        s ^= s >> 31;
        rng->state[i] = s;
    }
}

uint64_t xoshiro256_next(xoshiro256_t * restrict rng) {
    /**
     * 次の乱数を生成（Xoshiro256**アルゴリズム）
     * restrictキーワードにより、コンパイラはこのメモリが他のポインタから
     * 書き換えられないと確信し、より積極的な最適化（SIMD化など）を行う
     */
    // 結果 = rotl(state[1] * 5, 7) * 9
    uint64_t result = rotl(rng->state[1] * 5, 7) * 9;
    
    // 状態の更新
    uint64_t t = rng->state[1] << 17;
    
    // XOR演算で状態を混合
    rng->state[2] ^= rng->state[0];
    rng->state[3] ^= rng->state[1];
    rng->state[1] ^= rng->state[2];
    rng->state[0] ^= rng->state[3];
    
    rng->state[2] ^= t;
    
    // 状態[3] = rotl(state[1], 45)
    rng->state[3] = rotl(rng->state[1], 45);
    
    return result;
}

double xoshiro256_next_double(xoshiro256_t * restrict rng) {
    /**
     * 0.0以上1.0未満の浮動小数点数を生成
     * restrictキーワードにより、コンパイラはこのメモリが他のポインタから
     * 書き換えられないと確信し、より積極的な最適化（SIMD化など）を行う
     */
    // 64ビット整数を53ビット精度の浮動小数点数に変換
    // IEEE 754倍精度浮動小数点数の仮数部は52ビット + 1ビットの暗黙の1
    return (xoshiro256_next(rng) >> 11) * (1.0 / (1ULL << 53));
}

