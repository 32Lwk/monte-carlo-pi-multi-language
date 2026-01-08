package main

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
 * Goでの実装の違い:
 * - uint64型を使用、goroutineで並行処理
 */

// Xoshiro256 乱数生成器
type Xoshiro256 struct {
	state [4]uint64 // 4つの64ビット整数（合計256ビット）
}

// rotl 左ローテーション（ビットを左に回転）
func rotl(x uint64, k uint) uint64 {
	return (x << k) | (x >> (64 - k))
}

// NewXoshiro256 シードから初期状態を生成
func NewXoshiro256(seed uint64) *Xoshiro256 {
	var state [4]uint64
	s := seed

	// SplitMix64風の初期化
	for i := 0; i < 4; i++ {
		s ^= s >> 30
		s *= 0xBF58476D1CE4E5B9
		s ^= s >> 27
		s *= 0x94D049BB133111EB
		s ^= s >> 31
		state[i] = s
	}

	return &Xoshiro256{state: state}
}

// Next 次の乱数を生成（Xoshiro256**アルゴリズム）
func (rng *Xoshiro256) Next() uint64 {
	// 結果 = rotl(state[1] * 5, 7) * 9
	result := rotl(rng.state[1]*5, 7) * 9

	// 状態の更新
	t := rng.state[1] << 17

	// XOR演算で状態を混合
	rng.state[2] ^= rng.state[0]
	rng.state[3] ^= rng.state[1]
	rng.state[1] ^= rng.state[2]
	rng.state[0] ^= rng.state[3]

	rng.state[2] ^= t

	// 状態[3] = rotl(state[1], 45)
	rng.state[3] = rotl(rng.state[1], 45)

	return result
}

// NextDouble 0.0以上1.0未満の浮動小数点数を生成
func (rng *Xoshiro256) NextDouble() float64 {
	// 64ビット整数を53ビット精度の浮動小数点数に変換
	// IEEE 754倍精度浮動小数点数の仮数部は52ビット + 1ビットの暗黙の1
	return float64(rng.Next()>>11) * (1.0 / (1 << 53))
}

