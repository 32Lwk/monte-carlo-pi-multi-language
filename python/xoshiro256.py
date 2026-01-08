"""
Xoshiro256** - 高速・軽量・高品質な乱数生成器

アルゴリズムの背景:
- Mersenne Twister (MT19937) は状態空間が大きく（約2.5KB）、
  キャッシュ効率が悪く、SIMD化の妨げになる
- Xoshiro256** は軽量（256ビット = 32バイト）、高速、高品質
- 純粋な演算性能（コンパイラの最適化能力）を比較できる

ビット演算の解説:
- << (左シフト): ビットを左に移動、右側は0で埋める
- >> (右シフト): ビットを右に移動
- ^ (XOR): 排他的論理和、異なるビットで1、同じビットで0
- | (OR): 論理和、どちらかが1なら1
- & (AND): 論理積、両方が1なら1

各言語での実装の違い:
- Python: 整数は自動的に多倍長整数になるため、64ビット演算に注意
- C/C++: uint64_t型を使用、restrictキーワードで最適化
- Rust: u64型、所有権システムで安全性を確保
"""


def rotl(x: int, k: int) -> int:
    """
    左ローテーション（ビットを左に回転）
    
    Args:
        x: ローテートする値
        k: ローテートするビット数
    
    Returns:
        ローテートされた値
    """
    return ((x << k) | (x >> (64 - k))) & 0xFFFFFFFFFFFFFFFF


class Xoshiro256:
    """
    Xoshiro256** 乱数生成器
    
    状態: 4つの64ビット整数（合計256ビット）
    出力: 64ビット整数
    """
    
    def __init__(self, seed: int):
        """
        シードから初期状態を生成
        
        Args:
            seed: 初期シード値
        """
        # シードを4つの状態に分散（SplitMix64アルゴリズムの簡易版）
        self.state = [0] * 4
        s = seed & 0xFFFFFFFFFFFFFFFF  # 64ビットに制限
        
        # SplitMix64風の初期化
        for i in range(4):
            s = (s ^ (s >> 30)) & 0xFFFFFFFFFFFFFFFF
            s = (s * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
            s = (s ^ (s >> 27)) & 0xFFFFFFFFFFFFFFFF
            s = (s * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
            s = (s ^ (s >> 31)) & 0xFFFFFFFFFFFFFFFF
            self.state[i] = s
    
    def next(self) -> int:
        """
        次の乱数を生成（Xoshiro256**アルゴリズム）
        
        Returns:
            64ビットの乱数
        """
        # 結果 = rotl(state[1] * 5, 7) * 9
        result = rotl((self.state[1] * 5) & 0xFFFFFFFFFFFFFFFF, 7)
        result = (result * 9) & 0xFFFFFFFFFFFFFFFF
        
        # 状態の更新
        t = (self.state[1] << 17) & 0xFFFFFFFFFFFFFFFF
        
        # XOR演算で状態を混合
        self.state[2] ^= self.state[0]
        self.state[3] ^= self.state[1]
        self.state[1] ^= self.state[2]
        self.state[0] ^= self.state[3]
        
        self.state[2] ^= t
        
        # 状態[3] = rotl(state[1], 45)
        self.state[3] = rotl(self.state[1], 45)
        
        return result
    
    def next_double(self) -> float:
        """
        0.0以上1.0未満の浮動小数点数を生成
        
        Returns:
            乱数（0.0 <= x < 1.0）
        """
        # 64ビット整数を53ビット精度の浮動小数点数に変換
        # IEEE 754倍精度浮動小数点数の仮数部は52ビット + 1ビットの暗黙の1
        return (self.next() >> 11) * (1.0 / (1 << 53))
