#!/usr/bin/env python3
"""
モンテカルロ法による円周率計算（Python Numba版 - シングルスレッド）

この実装はNumba JITコンパイルを使用します。
NumbaはPythonコードを機械語にコンパイルし、C並の速度を実現します。
"""

import sys
import json
import time
import os
from numba import njit
# Numba版はxoshiro256.pyを直接使用せず、Numba用の実装を使用

# 理論上の円周率
PI_THEORETICAL = 3.141592653589793238462643383279502884197


@njit
def rotl(x: int, k: int) -> int:
    """左ローテーション（Numba用）"""
    return ((x << k) | (x >> (64 - k))) & 0xFFFFFFFFFFFFFFFF


@njit
def xoshiro_next(state: list) -> int:
    """
    Xoshiro256**のnext関数（Numba用）
    
    Args:
        state: 4要素のリスト（状態）
    
    Returns:
        64ビットの乱数
    """
    result = rotl((state[1] * 5) & 0xFFFFFFFFFFFFFFFF, 7)
    result = (result * 9) & 0xFFFFFFFFFFFFFFFF
    
    t = (state[1] << 17) & 0xFFFFFFFFFFFFFFFF
    
    state[2] ^= state[0]
    state[3] ^= state[1]
    state[1] ^= state[2]
    state[0] ^= state[3]
    
    state[2] ^= t
    state[3] = rotl(state[1], 45)
    
    return result


@njit
def xoshiro_next_double(state: list) -> float:
    """
    0.0以上1.0未満の浮動小数点数を生成（Numba用）
    
    Args:
        state: 4要素のリスト（状態）
    
    Returns:
        乱数（0.0 <= x < 1.0）
    """
    return (xoshiro_next(state) >> 11) * (1.0 / (1 << 53))


@njit
def calculate_pi_numba(iterations: int, seed: int) -> tuple[float, float]:
    """
    モンテカルロ法で円周率を計算（Numba JIT版）
    
    Args:
        iterations: 試行回数
        seed: シード値
    
    Returns:
        (円周率の推定値, 誤差)
    """
    # 状態の初期化（SplitMix64風）
    state = [0] * 4
    s = seed & 0xFFFFFFFFFFFFFFFF
    
    for i in range(4):
        s = (s ^ (s >> 30)) & 0xFFFFFFFFFFFFFFFF
        s = (s * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        s = (s ^ (s >> 27)) & 0xFFFFFFFFFFFFFFFF
        s = (s * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        s = (s ^ (s >> 31)) & 0xFFFFFFFFFFFFFFFF
        state[i] = s
    
    inside_circle = 0
    
    for _ in range(iterations):
        x = xoshiro_next_double(state)
        y = xoshiro_next_double(state)
        
        if x * x + y * y <= 1.0:
            inside_circle += 1
    
    pi_estimate = 4.0 * inside_circle / iterations
    error = abs(pi_estimate - PI_THEORETICAL)
    
    return pi_estimate, error


def calculate_pi(iterations: int) -> tuple[float, float]:
    """
    モンテカルロ法で円周率を計算（ラッパー関数）
    
    Args:
        iterations: 試行回数
    
    Returns:
        (円周率の推定値, 誤差)
    """
    return calculate_pi_numba(iterations, 12345)


def main():
    """メイン関数"""
    iterations = 100_000_000
    
    # 実行時間の測定
    start_time = time.perf_counter()
    pi_estimate, error = calculate_pi(iterations)
    end_time = time.perf_counter()
    
    elapsed_ms = (end_time - start_time) * 1000
    
    # コード行数のカウント（コメント・空行除く）
    script_path = os.path.abspath(__file__)
    with open(script_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    lines_of_code = len(lines)
    
    # 結果をJSON形式で出力
    result = {
        "language": "Python",
        "variant": "numba",
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "mode": "single",
        "iterations": iterations,
        "pi_estimate": pi_estimate,
        "error": error,
        "time_ms": elapsed_ms,
        "memory_mb": 0.0,  # runner.pyで測定
        "cache_misses": 0,  # runner.pyで測定
        "lines_of_code": lines_of_code,
        "compiler_flags": "N/A (JIT compiled)",
        "cpu_model": "N/A",
        "cpu_cores": os.cpu_count() or 1,
        "thread_count": 1,
        "os": os.name,
        "os_version": "N/A",
        "compiler": "CPython + Numba",
        "simd_detected": False,
        "simd_instructions": []
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

