#=
Xoshiro256** - 高速・軽量・高品質な乱数生成器

アルゴリズムの背景:
- Mersenne Twister (MT19937) は状態空間が大きく（約2.5KB）、
  キャッシュ効率が悪く、SIMD化の妨げになる
- Xoshiro256** は軽量（256ビット = 32バイト）、高速、高品質
- 純粋な演算性能（コンパイラの最適化能力）を比較できる

ビット演算の解説:
- << (左シフト): ビットを左に移動、右側は0で埋める
- >> (右シフト): ビットを右に移動
- ⊻ (XOR): 排他的論理和、異なるビットで1、同じビットで0
- | (OR): 論理和、どちらかが1なら1
- & (AND): 論理積、両方が1なら1

Juliaでの実装の違い:
- UInt64型を使用、JITコンパイルで高速化
=#

# 左ローテーション（ビットを左に回転）
rotl(x::UInt64, k::Int) = (x << k) | (x >> (64 - k))

# Xoshiro256** 乱数生成器
mutable struct Xoshiro256
    state::Vector{UInt64}  # 4つの64ビット整数（合計256ビット）
end

# シードから初期状態を生成
function Xoshiro256(seed::UInt64)
    state = zeros(UInt64, 4)
    s = seed
    
    # SplitMix64風の初期化
    for i in 1:4
        s = s ⊻ (s >> 30)
        s = s * 0xBF58476D1CE4E5B9
        s = s ⊻ (s >> 27)
        s = s * 0x94D049BB133111EB
        s = s ⊻ (s >> 31)
        state[i] = s
    end
    
    Xoshiro256(state)
end

# 次の乱数を生成（Xoshiro256**アルゴリズム）
function next(rng::Xoshiro256)::UInt64
    # 結果 = rotl(state[2] * 5, 7) * 9
    result = rotl(rng.state[2] * UInt64(5), 7) * UInt64(9)
    
    # 状態の更新
    t = rng.state[2] << 17
    
    # XOR演算で状態を混合
    rng.state[3] ⊻= rng.state[1]
    rng.state[4] ⊻= rng.state[2]
    rng.state[2] ⊻= rng.state[3]
    rng.state[1] ⊻= rng.state[4]
    
    rng.state[3] ⊻= t
    
    # 状態[4] = rotl(state[2], 45)
    rng.state[4] = rotl(rng.state[2], 45)
    
    result
end

# 0.0以上1.0未満の浮動小数点数を生成
function next_double(rng::Xoshiro256)::Float64
    # 64ビット整数を53ビット精度の浮動小数点数に変換
    (next(rng) >> 11) * (1.0 / (1 << 53))
end

