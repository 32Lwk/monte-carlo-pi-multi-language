#include "xoshiro256.hpp"

Xoshiro256::Xoshiro256(uint64_t seed) {
    /**
     * シードを4つの状態に分散（SplitMix64アルゴリズムの簡易版）
     */
    uint64_t s = seed;
    
    // SplitMix64風の初期化
    for (int i = 0; i < 4; i++) {
        s ^= s >> 30;
        s *= 0xBF58476D1CE4E5B9ULL;
        s ^= s >> 27;
        s *= 0x94D049BB133111EBULL;
        s ^= s >> 31;
        state[i] = s;
    }
}

uint64_t Xoshiro256::next() {
    /**
     * 次の乱数を生成（Xoshiro256**アルゴリズム）
     */
    // 結果 = rotl(state[1] * 5, 7) * 9
    uint64_t result = rotl(state[1] * 5, 7) * 9;
    
    // 状態の更新
    uint64_t t = state[1] << 17;
    
    // XOR演算で状態を混合
    state[2] ^= state[0];
    state[3] ^= state[1];
    state[1] ^= state[2];
    state[0] ^= state[3];
    
    state[2] ^= t;
    
    // 状態[3] = rotl(state[1], 45)
    state[3] = rotl(state[1], 45);
    
    return result;
}

double Xoshiro256::next_double() {
    /**
     * 0.0以上1.0未満の浮動小数点数を生成
     */
    // 64ビット整数を53ビット精度の浮動小数点数に変換
    // IEEE 754倍精度浮動小数点数の仮数部は52ビット + 1ビットの暗黙の1
    return (next() >> 11) * (1.0 / (1ULL << 53));
}

