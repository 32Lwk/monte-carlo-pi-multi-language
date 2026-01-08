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
 * Javaでの実装の違い:
 * - long型（64ビット）を使用、JVMの最適化を活用
 */
public class Xoshiro256 {
    private long[] state;  // 4つの64ビット整数（合計256ビット）

    /**
     * 左ローテーション（ビットを左に回転）
     */
    private static long rotl(long x, int k) {
        return (x << k) | (x >>> (64 - k));
    }

    /**
     * シードから初期状態を生成
     */
    public Xoshiro256(long seed) {
        state = new long[4];
        long s = seed;

        // SplitMix64風の初期化
        for (int i = 0; i < 4; i++) {
            s ^= s >>> 30;
            s *= 0xBF58476D1CE4E5B9L;
            s ^= s >>> 27;
            s *= 0x94D049BB133111EBL;
            s ^= s >>> 31;
            state[i] = s;
        }
    }

    /**
     * 次の乱数を生成（Xoshiro256**アルゴリズム）
     */
    public long next() {
        // 結果 = rotl(state[1] * 5, 7) * 9
        long result = rotl(state[1] * 5, 7) * 9;

        // 状態の更新
        long t = state[1] << 17;

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

    /**
     * 0.0以上1.0未満の浮動小数点数を生成
     */
    public double nextDouble() {
        // 64ビット整数を53ビット精度の浮動小数点数に変換
        return (next() >>> 11) * (1.0 / (1L << 53));
    }
}

