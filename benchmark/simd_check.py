#!/usr/bin/env python3
"""
SIMD最適化の自動検証スクリプト
コンパイル済みバイナリに対してSIMD命令の有無を確認します。
"""

import subprocess
import json
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
BIN_DIR = ROOT_DIR / "bin"
RESULTS_DIR = ROOT_DIR / "results"

# SIMD命令のパターン
SIMD_PATTERNS = {
    "SSE": ["movdqa", "movdqu", "addps", "addpd", "mulps", "mulpd"],
    "SSE2": ["movdqa", "movdqu", "addpd", "mulpd"],
    "AVX": ["vmovaps", "vmovapd", "vaddps", "vaddpd", "vmulps", "vmulpd"],
    "AVX2": ["vpbroadcast", "vpmuludq", "vpsllvd"],
    "AVX-512": ["vpbroadcastd", "vpmuludq", "vpsllvd", "zmm"],
    "FMA": ["vfmadd", "vfnmadd"]
}


def check_simd(binary_path):
    """バイナリのSIMD命令を検出"""
    if not binary_path.exists():
        return False, []
    
    detected_instructions = []
    
    try:
        # objdumpまたはllvm-objdumpを使用
        for tool in ["objdump", "llvm-objdump"]:
            try:
                result = subprocess.run([tool, "-d", str(binary_path)],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    output = result.stdout.lower()
                    
                    # 各SIMD命令セットをチェック
                    for simd_set, patterns in SIMD_PATTERNS.items():
                        for pattern in patterns:
                            if pattern.lower() in output:
                                if simd_set not in detected_instructions:
                                    detected_instructions.append(simd_set)
                                break
                    
                    if detected_instructions:
                        return True, detected_instructions
            except:
                continue
    except:
        pass
    
    return False, []


def main():
    """メイン関数"""
    RESULTS_DIR.mkdir(exist_ok=True)
    
    results = {}
    
    # コンパイル言語のバイナリをチェック
    languages = ["c", "cpp", "rust", "fortran"]
    modes = ["single", "parallel"]
    
    for lang in languages:
        for mode in modes:
            binary_name = f"pi_{lang}_{mode}"
            if os.name == "nt":
                binary_name += ".exe"
            
            binary_path = BIN_DIR / binary_name
            simd_detected, instructions = check_simd(binary_path)
            
            key = f"{lang}_{mode}"
            results[key] = {
                "simd_detected": simd_detected,
                "simd_instructions": instructions
            }
    
    # 結果を保存
    output_file = RESULTS_DIR / "simd_check.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"SIMD check results saved to {output_file}")


if __name__ == "__main__":
    main()

