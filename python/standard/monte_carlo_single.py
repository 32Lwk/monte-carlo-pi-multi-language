#!/usr/bin/env python3
"""
モンテカルロ法による円周率計算（Python Standard版 - シングルスレッド）

この実装は純正CPythonとrandomモジュールを使用します。
教育目的で、最も基本的な実装を示します。
"""

import sys
import json
import time
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from xoshiro256 import Xoshiro256

# 理論上の円周率
PI_THEORETICAL = 3.141592653589793238462643383279502884197


def calculate_pi(iterations: int) -> tuple[float, float]:
    """
    モンテカルロ法で円周率を計算
    
    Args:
        iterations: 試行回数
    
    Returns:
        (円周率の推定値, 誤差)
    """
    rng = Xoshiro256(12345)  # 固定シード
    inside_circle = 0
    
    for _ in range(iterations):
        # 0.0以上1.0未満の乱数を生成
        x = rng.next_double()
        y = rng.next_double()
        
        # 単位円内か判定（x^2 + y^2 <= 1）
        if x * x + y * y <= 1.0:
            inside_circle += 1
    
    # π ≈ 4 × (円内の点数) / (総試行回数)
    pi_estimate = 4.0 * inside_circle / iterations
    error = abs(pi_estimate - PI_THEORETICAL)
    
    return pi_estimate, error


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
        "variant": "standard",
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "mode": "single",
        "iterations": iterations,
        "pi_estimate": pi_estimate,
        "error": error,
        "time_ms": elapsed_ms,
        "memory_mb": 0.0,  # runner.pyで測定
        "cache_misses": 0,  # runner.pyで測定
        "lines_of_code": lines_of_code,
        "compiler_flags": "N/A (interpreted)",
        "cpu_model": "N/A",
        "cpu_cores": os.cpu_count() or 1,
        "thread_count": 1,
        "os": os.name,
        "os_version": "N/A",
        "compiler": "CPython",
        "simd_detected": False,
        "simd_instructions": []
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

