#!/usr/bin/env python3
"""
ベンチマーク実行スクリプト
全言語のプログラムを順次実行し、結果を収集します。
"""

import subprocess
import json
import os
import sys
import platform
import psutil
import time
import shutil
from pathlib import Path

# プロジェクトルート
ROOT_DIR = Path(__file__).parent.parent
BIN_DIR = ROOT_DIR / "bin"
BUILD_DIR = ROOT_DIR / "build"
RESULTS_DIR = ROOT_DIR / "results"

# 試行回数
ITERATIONS = 100_000_000
WARMUP_ITERATIONS = 1_000_000

# JIT言語のリスト
JIT_LANGUAGES = ["julia", "java", "javascript"]

# OS判定
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"


def get_cpu_info():
    """CPU情報を取得"""
    try:
        if IS_WINDOWS:
            return platform.processor()
        elif IS_LINUX:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        elif IS_MACOS:
            result = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
    except:
        pass
    return "N/A"


def get_compiler_version(compiler):
    """コンパイラのバージョンを取得"""
    try:
        result = subprocess.run([compiler, "--version"], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.split("\n")[0].strip()
    except:
        return "N/A"


def measure_memory_windows(process):
    """Windowsでのメモリ使用量を測定"""
    try:
        return process.memory_info().rss / 1024 / 1024  # MB
    except:
        return 0.0


def measure_memory_linux(command):
    """Linuxでのメモリ使用量を測定"""
    try:
        result = subprocess.run(["/usr/bin/time", "-v"] + command,
                              capture_output=True, text=True, timeout=600)
        for line in result.stderr.split("\n"):
            if "Maximum resident set size" in line:
                return float(line.split()[-1]) / 1024  # KB to MB
    except:
        pass
    return 0.0


def measure_cache_misses(command):
    """キャッシュミスを測定（Linuxのみ）"""
    if not IS_LINUX:
        return 0
    
    try:
        result = subprocess.run(["perf", "stat", "-e", "cache-misses"] + command,
                              capture_output=True, text=True, timeout=600)
        for line in result.stderr.split("\n"):
            if "cache-misses" in line:
                parts = line.split()
                if len(parts) > 0:
                    return int(parts[0].replace(",", ""))
    except:
        pass
    return 0


def run_python_standard(mode):
    """Python Standard版を実行"""
    script = ROOT_DIR / "python" / "standard" / f"monte_carlo_{mode}.py"
    print(f"    Running Python Standard ({mode})...", end="", flush=True)
    start_time = time.time()
    result = subprocess.run([sys.executable, str(script)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    else:
        print(f" Failed (return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def run_python_numpy(mode):
    """Python NumPy版を実行"""
    script = ROOT_DIR / "python" / "numpy" / f"monte_carlo_{mode}.py"
    print(f"    Running Python NumPy ({mode})...", end="", flush=True)
    start_time = time.time()
    result = subprocess.run([sys.executable, str(script)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    else:
        print(f" Failed (return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def run_python_numba(mode):
    """Python Numba版を実行"""
    script = ROOT_DIR / "python" / "numba" / f"monte_carlo_{mode}.py"
    print(f"    Running Python Numba ({mode})...", end="", flush=True)
    start_time = time.time()
    result = subprocess.run([sys.executable, str(script)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    else:
        print(f" Failed (return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def run_c(mode):
    """C言語版を実行"""
    binary = BIN_DIR / f"pi_c_{mode}{'.exe' if IS_WINDOWS else ''}"
    if not binary.exists():
        print(f"    C ({mode}): Binary not found, skipping")
        return None
    
    print(f"    Running C ({mode})...", end="", flush=True)
    start_time = time.time()
    command = [str(binary)]
    
    # メモリ測定
    memory_mb = 0.0
    cache_misses = 0
    
    if IS_WINDOWS:
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            memory_mb = measure_memory_windows(psutil.Process(process.pid))
            stdout, stderr = process.communicate(timeout=600)
            output = stdout.decode('utf-8')
            returncode = process.returncode
        except Exception as e:
            elapsed = time.time() - start_time
            print(f" Failed ({elapsed:.1f}s): {e}")
            return None
    else:
        memory_mb = measure_memory_linux(command)
        if IS_LINUX:
            cache_misses = measure_cache_misses(command)
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            elapsed = time.time() - start_time
            print(f" Failed ({elapsed:.1f}s, return code: {result.returncode})")
            return None
        output = result.stdout
        returncode = result.returncode
    
    elapsed = time.time() - start_time
    try:
        data = json.loads(output)
        data["memory_mb"] = memory_mb
        if IS_LINUX:
            data["cache_misses"] = cache_misses
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    except json.JSONDecodeError as e:
        print(f" Failed ({elapsed:.1f}s): JSON parse error: {e}")
        return None


def run_julia(mode):
    """Julia版を実行"""
    # Juliaがインストールされているか確認
    julia_cmd = shutil.which("julia")
    if not julia_cmd:
        print(f"    Julia ({mode}): julia not found, skipping")
        return None
    
    try:
        subprocess.run(["julia", "--version"], capture_output=True, timeout=5, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print(f"    Julia ({mode}): julia not found, skipping")
        return None
    
    script = ROOT_DIR / "julia" / f"monte_carlo_{mode}.jl"
    if not script.exists():
        print(f"    Julia ({mode}): Script not found, skipping")
        return None
    
    print(f"    Running Julia ({mode})...", end="", flush=True)
    start_time = time.time()
    
    # ウォームアップ実行
    print(" [warmup]", end="", flush=True)
    try:
        subprocess.run(["julia", str(script), str(WARMUP_ITERATIONS)],
                      capture_output=True, timeout=60, check=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        elapsed = time.time() - start_time
        print(f" Failed ({elapsed:.1f}s): warmup error")
        return None
    
    # 本番実行
    print(" [running]", end="", flush=True)
    try:
        result = subprocess.run(["julia", str(script), str(ITERATIONS)],
                              capture_output=True, text=True, timeout=600, check=True)
        elapsed = time.time() - start_time
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        elapsed = time.time() - start_time
        print(f" Failed ({elapsed:.1f}s): execution error")
        return None
    except json.JSONDecodeError as e:
        elapsed = time.time() - start_time
        print(f" Failed ({elapsed:.1f}s): JSON parse error")
        return None


def run_java(mode, gc_mode="default"):
    """Java版を実行"""
    # Javaがインストールされているか確認
    java_cmd = shutil.which("java")
    if not java_cmd:
        print(f"    Java ({mode}): java not found, skipping")
        return None
    
    try:
        subprocess.run(["java", "-version"], capture_output=True, timeout=5, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print(f"    Java ({mode}): java not found, skipping")
        return None
    
    class_name = f"MonteCarlo{mode.capitalize()}"
    classpath = str(BUILD_DIR)
    
    # クラスファイルが存在するか確認
    class_file = BUILD_DIR / f"{class_name}.class"
    if not class_file.exists():
        print(f"    Java ({mode}): Class file not found (run 'build.ps1 java' first), skipping")
        return None
    
    gc_suffix = f" ({gc_mode})" if mode == "parallel" else ""
    print(f"    Running Java ({mode}{gc_suffix})...", end="", flush=True)
    start_time = time.time()
    
    # ウォームアップ実行（JIT言語）
    if mode == "parallel":
        print(" [warmup]", end="", flush=True)
        warmup_args = []
        if gc_mode == "pure":
            warmup_args = ["--pure"]
        try:
            subprocess.run(["java", "-cp", classpath, class_name] + warmup_args,
                          capture_output=True, timeout=60, check=True)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass  # ウォームアップ失敗でも続行
    
    args = []
    if mode == "parallel" and gc_mode == "pure":
        args = ["--pure"]
    
    print(" [running]", end="", flush=True)
    try:
        result = subprocess.run(["java", "-cp", classpath, class_name] + args,
                              capture_output=True, text=True, timeout=600, check=True)
        elapsed = time.time() - start_time
        data = json.loads(result.stdout)
        if mode == "parallel":
            data["gc_mode"] = gc_mode
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f" Failed ({elapsed:.1f}s, return code: {e.returncode})")
        if e.stderr:
            stderr_str = e.stderr.decode('utf-8', errors='ignore') if isinstance(e.stderr, bytes) else e.stderr
            print(f"      Error: {stderr_str[:200]}")
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        elapsed = time.time() - start_time
        print(f" Failed ({elapsed:.1f}s): {type(e).__name__}")
        return None


def run_javascript(mode):
    """JavaScript版を実行"""
    script = ROOT_DIR / "javascript" / f"monte_carlo_{mode}.js"
    print(f"    Running JavaScript ({mode})...", end="", flush=True)
    start_time = time.time()
    
    # ウォームアップ実行（JIT言語）
    print(" [warmup]", end="", flush=True)
    subprocess.run(["node", str(script)],
                  capture_output=True, timeout=60)
    
    print(" [running]", end="", flush=True)
    result = subprocess.run(["node", str(script)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
            return data
        except json.JSONDecodeError as e:
            print(f" Failed ({elapsed:.1f}s): JSON parse error: {e}")
            return None
    else:
        print(f" Failed ({elapsed:.1f}s, return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def run_go(mode):
    """Go版を実行"""
    binary = BIN_DIR / f"pi_go_{mode}{'.exe' if IS_WINDOWS else ''}"
    if not binary.exists():
        print(f"    Go ({mode}): Binary not found, skipping")
        return None
    
    print(f"    Running Go ({mode})...", end="", flush=True)
    start_time = time.time()
    result = subprocess.run([str(binary)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    else:
        print(f" Failed ({elapsed:.1f}s, return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def run_rust(mode):
    """Rust版を実行"""
    binary = BIN_DIR / f"pi_rust_{mode}{'.exe' if IS_WINDOWS else ''}"
    if not binary.exists():
        print(f"    Rust ({mode}): Binary not found, skipping")
        return None
    
    print(f"    Running Rust ({mode})...", end="", flush=True)
    start_time = time.time()
    result = subprocess.run([str(binary)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    else:
        print(f" Failed ({elapsed:.1f}s, return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def run_cpp(mode):
    """C++版を実行"""
    binary = BIN_DIR / f"pi_cpp_{mode}{'.exe' if IS_WINDOWS else ''}"
    if not binary.exists():
        print(f"    C++ ({mode}): Binary not found, skipping")
        return None
    
    print(f"    Running C++ ({mode})...", end="", flush=True)
    start_time = time.time()
    result = subprocess.run([str(binary)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    else:
        print(f" Failed ({elapsed:.1f}s, return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def run_fortran(mode):
    """Fortran版を実行"""
    binary = BIN_DIR / f"pi_fortran_{mode}{'.exe' if IS_WINDOWS else ''}"
    if not binary.exists():
        print(f"    Fortran ({mode}): Binary not found, skipping")
        return None
    
    print(f"    Running Fortran ({mode})...", end="", flush=True)
    start_time = time.time()
    result = subprocess.run([str(binary)],
                          capture_output=True, text=True, timeout=600)
    elapsed = time.time() - start_time
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f" Done ({elapsed:.1f}s, {data.get('time_ms', 0):.2f}ms)")
        return data
    else:
        print(f" Failed ({elapsed:.1f}s, return code: {result.returncode})")
        if result.stderr:
            print(f"      Error: {result.stderr[:200]}")
    return None


def main():
    """メイン関数"""
    RESULTS_DIR.mkdir(exist_ok=True)
    
    results = []
    
    # 環境情報を収集
    cpu_model = get_cpu_info()
    cpu_cores = os.cpu_count() or 1
    
    print("Running benchmarks...")
    print(f"CPU: {cpu_model}, Cores: {cpu_cores}")
    print(f"Iterations: {ITERATIONS:,}")
    print("")
    
    # Python実装
    print("Python Standard:")
    for mode in ["single", "parallel"]:
        result = run_python_standard(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("Python NumPy:")
    for mode in ["single", "parallel"]:
        result = run_python_numpy(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("Python Numba:")
    for mode in ["single", "parallel"]:
        result = run_python_numba(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    # コンパイル言語
    print("C:")
    for mode in ["single", "parallel"]:
        result = run_c(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("C++:")
    for mode in ["single", "parallel"]:
        result = run_cpp(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("Rust:")
    for mode in ["single", "parallel"]:
        result = run_rust(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("Go:")
    for mode in ["single", "parallel"]:
        result = run_go(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("Java:")
    for mode in ["single", "parallel"]:
        if mode == "parallel":
            for gc_mode in ["default", "pure"]:
                result = run_java(mode, gc_mode)
                if result:
                    result["cpu_model"] = cpu_model
                    results.append(result)
        else:
            result = run_java(mode)
            if result:
                result["cpu_model"] = cpu_model
                results.append(result)
    
    print("Julia:")
    for mode in ["single", "parallel"]:
        result = run_julia(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("JavaScript:")
    for mode in ["single", "parallel"]:
        result = run_javascript(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    print("Fortran:")
    for mode in ["single", "parallel"]:
        result = run_fortran(mode)
        if result:
            result["cpu_model"] = cpu_model
            results.append(result)
    
    # 結果を保存
    output_file = RESULTS_DIR / "results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    print(f"Total results: {len(results)}")


if __name__ == "__main__":
    main()

