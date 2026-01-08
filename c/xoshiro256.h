#ifndef XOSHIRO256_H
#define XOSHIRO256_H

#include <stdint.h>

/**
 * Xoshiro256** - 高速・軽量・高品質な乱数生成器
 * 
 * アルゴリズムの背景:
 * - Mersenne Twister (MT19937) は状態空間が大きく（約2.5KB）、
 *   キャッシュ効率が悪く、SIMD化の妨げになる
 * - Xoshiro256** は軽量（256ビット = 32バイト）、高速、高品質
 * - 純粋な演算性能（コンパイラの最適化能力）を比較できる
 * 
 * ビット演算の解説:
 * - << (左シフト): ビットを左に移動、右側は0で埋める
 * - >> (右シフト): ビットを右に移動
 * - ^ (XOR): 排他的論理和、異なるビットで1、同じビットで0
 * - | (OR): 論理和、どちらかが1なら1
 * - & (AND): 論理積、両方が1なら1
 * 
 * C言語での実装の違い:
 * - uint64_t型を使用、restrictキーワードで最適化
 * - restrictキーワードにより、コンパイラは「このメモリは他のポインタから
 *   書き換えられない」と確信し、より積極的な最適化（SIMD化など）を行う
 */

/**
 * 左ローテーション（ビットを左に回転）
 * 
 * @param x ローテートする値
 * @param k ローテートするビット数
 * @return ローテートされた値
 */
static inline uint64_t rotl(uint64_t x, int k) {
    return (x << k) | (x >> (64 - k));
}

/**
 * Xoshiro256**の状態構造体
 */
typedef struct {
    uint64_t state[4];  // 4つの64ビット整数（合計256ビット）
} xoshiro256_t;

/**
 * シードから初期状態を生成
 * 
 * @param rng 乱数生成器の状態（restrictキーワードで最適化）
 * @param seed 初期シード値
 */
void xoshiro256_init(xoshiro256_t * restrict rng, uint64_t seed);

/**
 * 次の乱数を生成（Xoshiro256**アルゴリズム）
 * 
 * @param rng 乱数生成器の状態（restrictキーワードで最適化）
 * @return 64ビットの乱数
 */
uint64_t xoshiro256_next(xoshiro256_t * restrict rng);

/**
 * 0.0以上1.0未満の浮動小数点数を生成
 * 
 * @param rng 乱数生成器の状態（restrictキーワードで最適化）
 * @return 乱数（0.0 <= x < 1.0）
 */
double xoshiro256_next_double(xoshiro256_t * restrict rng);

#endif /* XOSHIRO256_H */

