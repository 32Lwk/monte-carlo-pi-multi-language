#!/usr/bin/env python3
"""
モンテカルロ法による円周率計算（Python Standard版 - 並列化）

この実装は純正CPythonとthreadingモジュールを使用します。
注意: PythonのGIL（Global Interpreter Lock）により、真の並列化は制限されます。
これは教育目的で、GILの影響を示すための実装です。
"""

import sys
import json
import time
import os
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from xoshiro256 import Xoshiro256

# 理論上の円周率
PI_THEORETICAL = 3.141592653589793238462643383279502884197

# シードの加算幅を大きくする（推奨方式）
SEED_MULTIPLIER = 0x9E3779B97F4A7C15  # 黄金比の逆数（64ビット）


def calculate_pi_thread(iterations_per_thread: int, thread_id: int, 
                        base_seed: int, results: list) -> None:
    """
    スレッドごとの円周率計算
    
    Args:
        iterations_per_thread: スレッドあたりの試行回数
        thread_id: スレッドID
        base_seed: ベースシード
        results: 結果を格納するリスト
    """
    # 推奨方式: シードの加算幅を大きくする
    thread_seed = base_seed + (thread_id * SEED_MULTIPLIER)
    rng = Xoshiro256(thread_seed)  # スレッドごとに独立したインスタンス
    
    inside_circle = 0
    
    for _ in range(iterations_per_thread):
        # 0.0以上1.0未満の乱数を生成
        x = rng.next_double()
        y = rng.next_double()
        
        # 単位円内か判定（x^2 + y^2 <= 1）
        if x * x + y * y <= 1.0:
            inside_circle += 1
    
    results[thread_id] = inside_circle


def calculate_pi(iterations: int, num_threads: int) -> tuple[float, float]:
    """
    モンテカルロ法で円周率を計算（並列化版）
    
    Args:
        iterations: 総試行回数
        num_threads: スレッド数
    
    Returns:
        (円周率の推定値, 誤差)
    """
    iterations_per_thread = iterations // num_threads
    base_seed = 12345
    
    # 各スレッドの結果を格納
    results = [0] * num_threads
    threads = []
    
    # スレッドを起動
    for thread_id in range(num_threads):
        thread = threading.Thread(
            target=calculate_pi_thread,
            args=(iterations_per_thread, thread_id, base_seed, results)
        )
        threads.append(thread)
        thread.start()
    
    # すべてのスレッドの完了を待つ
    for thread in threads:
        thread.join()
    
    # 結果を集計
    total_inside = sum(results)
    
    # π ≈ 4 × (円内の点数) / (総試行回数)
    pi_estimate = 4.0 * total_inside / iterations
    error = abs(pi_estimate - PI_THEORETICAL)
    
    return pi_estimate, error


def main():
    """メイン関数"""
    iterations = 100_000_000
    num_threads = os.cpu_count() or 1
    
    # 実行時間の測定
    start_time = time.perf_counter()
    pi_estimate, error = calculate_pi(iterations, num_threads)
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
        "cpu_cores": os.cpu_count() or 1,
        "thread_count": num_threads,
        "os": os.name,
        "os_version": "N/A",
        "compiler": "CPython",
        "simd_detected": False,
        "simd_instructions": []
    }
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

