#!/usr/bin/env python3
"""
モンテカルロ法による円周率計算（Python NumPy版 - 並列化）

この実装はNumPyとmultiprocessingを使用します。
multiprocessingはGILを回避するため、真の並列化が可能です。
"""

import sys
import json
import time
import os
import numpy as np
from multiprocessing import Pool, cpu_count
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from xoshiro256 import Xoshiro256

# 理論上の円周率
PI_THEORETICAL = 3.141592653589793238462643383279502884197

# シードの加算幅を大きくする（推奨方式）
SEED_MULTIPLIER = 0x9E3779B97F4A7C15  # 黄金比の逆数（64ビット）


def calculate_pi_worker(args: tuple) -> int:
    """
    ワーカープロセスでの円周率計算
    
    Args:
        args: (iterations_per_worker, worker_id, base_seed)のタプル
    
    Returns:
        円内の点の数
    """
    iterations_per_worker, worker_id, base_seed = args
    
    # 推奨方式: シードの加算幅を大きくする
    thread_seed = base_seed + (worker_id * SEED_MULTIPLIER)
    rng = Xoshiro256(thread_seed)  # ワーカーごとに独立したインスタンス
    
    # バッチサイズ
    batch_size = min(1_000_000, iterations_per_worker)
    inside_circle = 0
    
    for _ in range(0, iterations_per_worker, batch_size):
        current_batch = min(batch_size, iterations_per_worker - inside_circle)
        
        # ランダムな点を生成
        x = np.array([rng.next_double() for _ in range(current_batch)])
        y = np.array([rng.next_double() for _ in range(current_batch)])
        
        # 単位円内か判定（ベクトル化）
        distances_squared = x * x + y * y
        inside = np.sum(distances_squared <= 1.0)
        
        inside_circle += inside
    
    return inside_circle


def calculate_pi(iterations: int, num_workers: int) -> tuple[float, float]:
    """
    モンテカルロ法で円周率を計算（並列化版）
    
    Args:
        iterations: 総試行回数
        num_workers: ワーカー数
    
    Returns:
        (円周率の推定値, 誤差)
    """
    iterations_per_worker = iterations // num_workers
    base_seed = 12345
    
    # ワーカーに渡す引数を準備
    args_list = [
        (iterations_per_worker, worker_id, base_seed)
        for worker_id in range(num_workers)
    ]
    
    # 並列実行
    with Pool(processes=num_workers) as pool:
        results = pool.map(calculate_pi_worker, args_list)
    
    # 結果を集計
    total_inside = sum(results)
    
    # π ≈ 4 × (円内の点数) / (総試行回数)
    pi_estimate = 4.0 * total_inside / iterations
    error = abs(pi_estimate - PI_THEORETICAL)
    
    return pi_estimate, error


def main():
    """メイン関数"""
    iterations = 100_000_000
    num_workers = cpu_count() or 1
    
    # 実行時間の測定
    start_time = time.perf_counter()
    pi_estimate, error = calculate_pi(iterations, num_workers)
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
        "variant": "numpy",
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "mode": "parallel",
        "iterations": iterations,
        "pi_estimate": pi_estimate,
        "error": error,
        "time_ms": elapsed_ms,
        "memory_mb": 0.0,  # runner.pyで測定
        "cache_misses": 0,  # runner.pyで測定
        "lines_of_code": lines_of_code,
        "compiler_flags": "N/A (interpreted)",
        "cpu_model": "N/A",
        "cpu_cores": cpu_count() or 1,
        "thread_count": num_workers,
        "os": os.name,
        "os_version": "N/A",
        "compiler": "CPython + NumPy",
        "simd_detected": False,
        "simd_instructions": []
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

