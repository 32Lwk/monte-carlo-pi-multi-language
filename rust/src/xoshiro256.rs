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
 * Rustでの実装の違い:
 * - u64型、所有権システムで安全性を確保
 * - メモリ安全性とパフォーマンスを両立
 */

/// 左ローテーション（ビットを左に回転）
#[inline]
fn rotl(x: u64, k: u32) -> u64 {
    (x << k) | (x >> (64 - k))
}

/// Xoshiro256** 乱数生成器
pub struct Xoshiro256 {
    state: [u64; 4],  // 4つの64ビット整数（合計256ビット）
}

impl Xoshiro256 {
    /// シードから初期状態を生成
    pub fn new(seed: u64) -> Self {
        let mut state = [0u64; 4];
        let mut s = seed;
        
        // SplitMix64風の初期化
        for i in 0..4 {
            s ^= s >> 30;
            s = s.wrapping_mul(0xBF58476D1CE4E5B9);
            s ^= s >> 27;
            s = s.wrapping_mul(0x94D049BB133111EB);
            s ^= s >> 31;
            state[i] = s;
        }
        
        Xoshiro256 { state }
    }
    
    /// 次の乱数を生成（Xoshiro256**アルゴリズム）
    pub fn next(&mut self) -> u64 {
        // 結果 = rotl(state[1] * 5, 7) * 9
        let result = rotl(self.state[1].wrapping_mul(5), 7).wrapping_mul(9);
        
        // 状態の更新
        let t = self.state[1] << 17;
        
        // XOR演算で状態を混合
        self.state[2] ^= self.state[0];
        self.state[3] ^= self.state[1];
        self.state[1] ^= self.state[2];
        self.state[0] ^= self.state[3];
        
        self.state[2] ^= t;
        
        // 状態[3] = rotl(state[1], 45)
        self.state[3] = rotl(self.state[1], 45);
        
        result
    }
    
    /// 0.0以上1.0未満の浮動小数点数を生成
    pub fn next_double(&mut self) -> f64 {
        // 64ビット整数を53ビット精度の浮動小数点数に変換
        // IEEE 754倍精度浮動小数点数の仮数部は52ビット + 1ビットの暗黙の1
        (self.next() >> 11) as f64 * (1.0 / (1u64 << 53) as f64)
    }
}

