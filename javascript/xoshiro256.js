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
 * JavaScriptでの実装の違い:
 * - BigInt型を使用（64ビット整数の正確な処理）
 * - worker_threadsとSharedArrayBufferで並列化
 */

// 左ローテーション（ビットを左に回転）
function rotl(x, k) {
    // BigInt対応（常にBigIntとして処理）
    if (typeof x === 'bigint') {
        return (x << BigInt(k)) | (x >> BigInt(64 - k));
    }
    // 通常の数値の場合もBigIntに変換
    const bigX = BigInt(x);
    return (bigX << BigInt(k)) | (bigX >> BigInt(64 - k));
}

class Xoshiro256 {
    /**
     * シードから初期状態を生成
     */
    constructor(seed) {
        this.state = new BigUint64Array(4);
        let s = BigInt(seed);
        
        // SplitMix64風の初期化
        for (let i = 0; i < 4; i++) {
            s ^= s >> 30n;
            s *= 0xBF58476D1CE4E5B9n;
            s ^= s >> 27n;
            s *= 0x94D049BB133111EBn;
            s ^= s >> 31n;
            this.state[i] = s;
        }
    }
    
    /**
     * 次の乱数を生成（Xoshiro256**アルゴリズム）
     */
    next() {
        // 結果 = rotl(state[1] * 5, 7) * 9
        let result = rotl(this.state[1] * 5n, 7) * 9n;
        
        // 状態の更新
        let t = this.state[1] << 17n;
        
        // XOR演算で状態を混合
        this.state[2] ^= this.state[0];
        this.state[3] ^= this.state[1];
        this.state[1] ^= this.state[2];
        this.state[0] ^= this.state[3];
        
        this.state[2] ^= t;
        
        // 状態[3] = rotl(state[1], 45)
        this.state[3] = rotl(this.state[1], 45);
        
        return result;
    }
    
    /**
     * 0.0以上1.0未満の浮動小数点数を生成
     */
    nextDouble() {
        // 64ビット整数を53ビット精度の浮動小数点数に変換
        const value = this.next();
        const shifted = Number(value >> 11n);
        const divisor = Number(1n << 53n);
        return shifted * (1.0 / divisor);
    }
}

module.exports = Xoshiro256;

