# 🎲 モンテカルロ法による円周率計算の多言語ベンチマーク

[![Languages](https://img.shields.io/badge/languages-9-blue)](https://github.com/32Lwk/monte-carlo-pi-multi-language)
[![License](https://img.shields.io/badge/license-educational-green)](LICENSE)

複数のプログラミング言語（**Python 3バリエーション, C, Rust, C++, JavaScript, Fortran, Julia, Go, Java**）でモンテカルロ法による円周率計算を実装し、実行時間、誤差、コード行数、メモリ使用量、キャッシュミス率を比較するベンチマークシステムです。

🎓 **このプロジェクトは、様々なプログラミング言語の特性や書き方を理解するための学習教材として設計されています。**

## 📋 目次

- [プロジェクト概要](#-プロジェクト概要)
- [主な特徴](#-主な特徴)
- [クイックスタート](#-クイックスタート)
- [セットアップ](#-セットアップ)
- [ビルド方法](#-ビルド方法)
- [実行方法](#-実行方法)
- [測定指標](#-測定指標)
- [実装の詳細](#-実装の詳細)
- [各言語の特性](#-各言語の特性と実装の違い)
- [プロジェクト構造](#-プロジェクト構造)

## 🎯 プロジェクト概要

このプロジェクトは、以下の目的で作成されました：

1. **プログラミング言語の学習**: 同じアルゴリズムを複数の言語で実装することで、各言語の特性、書き方、イディオムを学習
2. **パフォーマンス比較**: Xoshiro256**を統一実装し、純粋な演算性能を比較
3. **並列化の理解**: 各言語の並列化手法（threading, goroutine, Rayon等）を実装・比較
4. **最適化技術の学習**: SIMD最適化、JITコンパイル、ベクトル化などの最適化技術を実践

### 対応言語

| 言語 | 実装バリエーション | 並列化 |
|------|-------------------|--------|
| Python | Standard, NumPy, Numba | threading, multiprocessing, Numba parallel |
| C | ネイティブ | pthread |
| C++ | ネイティブ | std::thread |
| Rust | ネイティブ | Rayon |
| Go | ネイティブ | goroutine |
| Java | JVM | ExecutorService |
| Julia | JIT | @threads |
| JavaScript | Node.js | worker_threads |
| Fortran | ネイティブ | OpenMP |

## ✨ 主な特徴

- **🎲 Xoshiro256**の統一実装**: 各言語で同じアルゴリズムを実装し、純粋な演算性能を比較
- **🐍 Python 3バリエーション**: Standard, NumPy, Numbaの3種類を実装し、最適化手法の違いを比較
- **⚡ 並列化対応**: 各言語でシングルスレッド版と並列化版の両方を実装
- **🚀 ネイティブ最適化**: コンパイル言語は`-march=native -flto`で最適化
- **🔍 SIMD最適化の自動検証**: コンパイル済みバイナリに対してSIMD命令の有無を確認
- **📊 包括的な測定**: 実行時間、誤差、メモリ使用量、キャッシュミス率を測定

## 🚀 クイックスタート

```bash
# 1. リポジトリをクローン
git clone https://github.com/32Lwk/monte-carlo-pi-multi-language.git
cd monte-carlo-pi-multi-language

# 2. Python依存関係をインストール
pip install psutil numpy numba

# 3. ビルド（Linux/macOS）
make build

# Windowsの場合は
.\build.ps1

# 4. ベンチマーク実行
python benchmark/runner.py

# 5. 結果を確認
python benchmark/visualizer.py
# ブラウザで results/report.html を開く
```

## 🔧 セットアップ

### 必要な環境

| 言語/ツール | バージョン | 用途 |
|------------|-----------|------|
| **Python** | 3.8以上 | ベンチマーク実行・集計スクリプト |
| **C/C++** | GCC/Clang | C, C++, Fortranのコンパイル |
| **Rust** | rustc 1.70以上 | Rust実装のビルド |
| **Go** | 1.21以上 | Go実装のビルド |
| **Java** | JDK 11以上 | Java実装のコンパイル・実行 |
| **Julia** | 1.8以上 | Julia実装の実行 |
| **Node.js** | 18以上 | JavaScript実装の実行 |
| **Fortran** | GFortran | Fortran実装のコンパイル（GCCに含まれる） |

### 依存関係のインストール

```bash
# Python依存関係
pip install psutil numpy numba

# Rust依存関係（自動的にインストールされます）
cd rust && cargo build --release && cd ..
```

**注意**: すべての言語が必須ではありません。利用可能な言語だけをビルドして実行できます。

## 🏗️ ビルド方法

### Linux/macOS環境

```bash
# 全言語をビルド
make build

# 個別にビルド
make build-c      # C言語
make build-cpp    # C++
make build-rust   # Rust
make build-go     # Go
make build-java   # Java
make build-fortran # Fortran

# クリーンアップ
make clean
```

### Windows環境（PowerShell）

Windowsでは`make`コマンドが使えないため、PowerShellスクリプトを使用します：

```powershell
# 全言語をビルド
.\build.ps1

# または個別にビルド
.\build.ps1 c        # C言語
.\build.ps1 cpp      # C++
.\build.ps1 rust     # Rust
.\build.ps1 go       # Go
.\build.ps1 java     # Java
.\build.ps1 fortran  # Fortran

# クリーンアップ
.\build.ps1 clean
```

**注意**: Windowsでビルドするには、以下のツールが必要です：
- **MinGW/MSYS2** (C, C++, Fortran用のgcc/g++/gfortran)
- **Rust** (cargo)
- **Go** (goコマンド)
- **Java** (javac)

MinGW/MSYS2がインストールされていない場合、C/C++/Fortranのビルドはスキップされます。

## ▶️ 実行方法

### Linux/macOS環境

```bash
# 全言語を実行してベンチマーク
make run

# または直接実行
python benchmark/runner.py

# 結果を分析
python benchmark/analyzer.py

# HTMLレポートを生成
python benchmark/visualizer.py

# SIMD最適化を検証
make simd-check
```

### Windows環境（PowerShell）

```powershell
# 全言語を実行してベンチマーク
python benchmark/runner.py

# 結果を分析
python benchmark/analyzer.py

# HTMLレポートを生成
python benchmark/visualizer.py

# SIMD最適化を検証（Linuxのみ、Windowsではスキップされます）
python benchmark/simd_check.py
```

## 📊 測定指標

1. **⏱️ Time (ms)**: 実行時間（ミリ秒）
2. **📐 Error**: 理論上の円周率（3.141592653589793...）との誤差
3. **📝 Lines of Code**: コード行数（コメント・空行除く）
4. **💾 Memory Usage (MB)**: メモリ消費量
5. **🎯 Cache Misses**: キャッシュミス率（Linuxのみ）

結果は`results/results.json`に保存され、`results/report.html`で可視化されます。

## 🔬 実装の詳細

### Xoshiro256**の統一実装

各言語でXoshiro256**を実装し、純粋な演算性能を比較します。Mersenne Twisterと比較して、以下の特徴があります：

- **状態空間が小さい**: 32バイト（MTは2500バイト）
- **キャッシュ効率が良い**: 小さい状態空間により、キャッシュミスが少ない
- **SIMD化しやすい**: 4つの64ビット整数で構成され、ベクトル化が容易

### Python 3バリエーション

| バリエーション | 説明 | 用途 |
|--------------|------|------|
| **Standard** | 純正CPython + `random`モジュール | 教育目的、基本的な実装 |
| **NumPy** | NumPyを使ったベクトル化実装 | 高速なベクトル演算 |
| **Numba** | JITコンパイルを使った実装 | C並の速度を実現 |

### 並列化の実装

各言語の特性に応じた並列化を実装：

| 言語 | 並列化手法 | 特徴 |
|------|-----------|------|
| **Python Standard** | threading | GILの影響あり |
| **Python NumPy** | multiprocessing | GIL回避 |
| **Python Numba** | `@njit(nogil=True, parallel=True)` + `prange` | GIL解除、真の並列化 |
| **C/C++** | pthread / std::thread | システムスレッド |
| **Rust** | Rayon | データ並列処理 |
| **Go** | goroutine | 軽量スレッド |
| **Java** | ExecutorService | スレッドプール |
| **Julia** | @threads | 並列化マクロ |
| **JavaScript** | worker_threads | ワーカースレッド |
| **Fortran** | OpenMP | 並列化ディレクティブ |

### 最適化フラグ

- **GCC/Clang (C, C++, Fortran)**: `-O3 -march=native -flto`
- **Rust**: `RUSTFLAGS="-C target-cpu=native"`
- **Go**: `-ldflags="-s -w"`

### 重要な注意事項

- **Python Numba並列化**: `@njit(nogil=True, parallel=True)`を必須とする（GIL解除なしでは並列化されない）
- **C/C++の最適化**: ポインタ引数に`restrict`キーワードを使用し、コンパイラの自動ベクトル化を促進
- **JIT言語のウォームアップ**: Julia, Java, JavaScript等で、計測前に小規模試行を実施
- **JavaのGC制御**: 2モード（GC込み、純粋）で計測し、結果を別エントリとして記録

## 💡 各言語の特性と実装の違い

### Python

- **Standard**: GILの影響で並列化が制限される。学習目的に最適。
- **NumPy**: ベクトル化により高速化、multiprocessingで真の並列化。
- **Numba**: JITコンパイルでC並の速度、`nogil=True`でGILを解除。

### C/C++

- **restrictキーワード**: コンパイラの自動ベクトル化を促進。
- **SIMD最適化**: `-march=native`によりAVX2/AVX-512を活用。

### Rust

- **所有権システム**: メモリ安全性とパフォーマンスを両立。
- **Rayon**: データ並列処理ライブラリ。

### Go

- **goroutine**: 軽量スレッドによる並行処理。
- **チャネル**: 安全なデータ共有。

### Java

- **JVM**: JITコンパイルによる最適化。
- **GC制御**: 2モードで計測（実用的 vs 純粋）。

### Julia

- **JITコンパイル**: 数値計算に特化した最適化。
- **@threads**: 並列化マクロ。

### JavaScript

- **worker_threads**: マルチスレッド処理。
- **SharedArrayBuffer**: メモリ共有（パフォーマンス向上）。

### Fortran

- **OpenMP**: 並列化ディレクティブ。
- **数値計算**: 伝統的な数値計算言語。

## 📁 プロジェクト構造

```
monte-carlo-pi-multi-language/
├── python/          # Python実装（3バリエーション）
│   ├── standard/    # 標準CPython実装
│   ├── numpy/       # NumPyベクトル化実装
│   └── numba/       # Numba JIT実装
├── c/              # C言語実装
├── rust/           # Rust実装
├── cpp/            # C++実装
├── javascript/     # JavaScript実装
├── fortran/        # Fortran実装
├── julia/          # Julia実装
├── go/             # Go実装
├── java/           # Java実装
├── benchmark/      # ベンチマーク実行・集計スクリプト
│   ├── runner.py   # 全言語を実行するPythonスクリプト
│   ├── analyzer.py # 結果を分析・集計するスクリプト
│   ├── visualizer.py # 結果を可視化するスクリプト
│   └── simd_check.py # SIMD最適化の自動検証
├── results/        # 結果保存ディレクトリ
│   └── report.html # HTML形式の比較レポート
├── build.ps1       # Windows用ビルドスクリプト
├── Makefile        # Linux/macOS用ビルドスクリプト
└── README.md       # このファイル
```

## 📚 学習目的

このプロジェクトは、以下のスキルを学習・実践するために設計されています：

1. **複数言語の習得**: 同じアルゴリズムを複数の言語で実装することで、各言語の特性を理解
2. **パフォーマンス分析**: 実行時間、メモリ使用量、キャッシュ効率などの測定方法を学習
3. **並列プログラミング**: 各言語の並列化手法を実装し、その違いを理解
4. **最適化技術**: SIMD最適化、JITコンパイル、ベクトル化などの最適化手法を実践
5. **ベンチマーク設計**: 公平な比較のためのベンチマーク設計方法を学習

## 🤝 貢献

改善提案やバグ報告を歓迎します。IssueやPull Requestを送っていただけると助かります。

## 📄 ライセンス

このプロジェクトは教育目的で作成されています。

---

⭐ このプロジェクトが役に立ったら、スターを付けていただけると嬉しいです！
