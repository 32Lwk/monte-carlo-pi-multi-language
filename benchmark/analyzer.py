#!/usr/bin/env python3
"""
結果を分析・集計するスクリプト
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
RESULTS_DIR = ROOT_DIR / "results"

def analyze_results():
    """結果を分析"""
    results_file = RESULTS_DIR / "results.json"
    
    if not results_file.exists():
        print("No results file found. Run runner.py first.")
        return
    
    with open(results_file, "r") as f:
        results = json.load(f)
    
    # 言語ごとにグループ化
    grouped = {}
    for result in results:
        lang = result.get("language", "Unknown")
        variant = result.get("variant", "standard")
        mode = result.get("mode", "single")
        
        key = f"{lang}_{variant}_{mode}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(result)
    
    # ランキング生成
    rankings = {
        "time": sorted(results, key=lambda x: x.get("time_ms", float("inf"))),
        "error": sorted(results, key=lambda x: x.get("error", float("inf"))),
        "memory": sorted(results, key=lambda x: x.get("memory_mb", float("inf"))),
    }
    
    # 統計情報
    stats = {
        "total_results": len(results),
        "languages": len(set(r.get("language") for r in results)),
        "fastest": rankings["time"][0] if rankings["time"] else None,
        "most_accurate": rankings["error"][0] if rankings["error"] else None,
        "most_efficient_memory": rankings["memory"][0] if rankings["memory"] else None,
    }
    
    # 結果を保存
    analysis_file = RESULTS_DIR / "analysis.json"
    with open(analysis_file, "w") as f:
        json.dump({
            "grouped": grouped,
            "rankings": rankings,
            "stats": stats
        }, f, indent=2)
    
    print(f"Analysis saved to {analysis_file}")


if __name__ == "__main__":
    analyze_results()

