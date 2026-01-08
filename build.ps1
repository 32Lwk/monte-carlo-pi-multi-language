# PowerShell Build Script for Monte Carlo Pi Benchmark
# Windows環境用ビルドスクリプト

param(
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"

# 設定
$EXT = ".exe"
$BIN_DIR = "bin"
$BUILD_DIR = "build"

# コンパイラフラグ
$CFLAGS = "-O3 -march=native -flto -std=c99"
$CXXFLAGS = "-O3 -march=native -flto -std=c++17"
$FFLAGS = "-O3 -march=native -flto -fopenmp"
$RUSTFLAGS = "-C target-cpu=native"

# ディレクトリ作成
function New-DirectoryIfNotExists {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

# C言語ビルド
function Build-C {
    Write-Host "Building C..." -ForegroundColor Green
    New-DirectoryIfNotExists $BIN_DIR
    
    $CC = Get-Command gcc -ErrorAction SilentlyContinue
    if (-not $CC) {
        Write-Host "Warning: gcc not found. Skipping C build." -ForegroundColor Yellow
        return
    }
    
    & gcc $CFLAGS.Split(' ') -o "$BIN_DIR/pi_c_single$EXT" c/monte_carlo_single.c c/xoshiro256.c -lm
    if ($LASTEXITCODE -ne 0) { throw "C single build failed" }
    
    & gcc $CFLAGS.Split(' ') -o "$BIN_DIR/pi_c_parallel$EXT" c/monte_carlo_parallel.c c/xoshiro256.c -lm -lpthread
    if ($LASTEXITCODE -ne 0) { throw "C parallel build failed" }
    
    Write-Host "C build complete!" -ForegroundColor Green
}

# C++ビルド
function Build-Cpp {
    Write-Host "Building C++..." -ForegroundColor Green
    New-DirectoryIfNotExists $BIN_DIR
    
    $CXX = Get-Command g++ -ErrorAction SilentlyContinue
    if (-not $CXX) {
        Write-Host "Warning: g++ not found. Skipping C++ build." -ForegroundColor Yellow
        return
    }
    
    & g++ $CXXFLAGS.Split(' ') -o "$BIN_DIR/pi_cpp_single$EXT" cpp/monte_carlo_single.cpp cpp/xoshiro256.cpp
    if ($LASTEXITCODE -ne 0) { throw "C++ single build failed" }
    
    & g++ $CXXFLAGS.Split(' ') -o "$BIN_DIR/pi_cpp_parallel$EXT" cpp/monte_carlo_parallel.cpp cpp/xoshiro256.cpp -pthread
    if ($LASTEXITCODE -ne 0) { throw "C++ parallel build failed" }
    
    Write-Host "C++ build complete!" -ForegroundColor Green
}

# Rustビルド
function Build-Rust {
    Write-Host "Building Rust..." -ForegroundColor Green
    New-DirectoryIfNotExists $BIN_DIR
    
    $CARGO = Get-Command cargo -ErrorAction SilentlyContinue
    if (-not $CARGO) {
        Write-Host "Warning: cargo not found. Skipping Rust build." -ForegroundColor Yellow
        return
    }
    
    $env:RUSTFLAGS = $RUSTFLAGS
    Push-Location rust
    & cargo build --release --manifest-path Cargo.toml
    if ($LASTEXITCODE -ne 0) { 
        Pop-Location
        throw "Rust build failed" 
    }
    Pop-Location
    
    Copy-Item "rust/target/release/monte_carlo_single$EXT" "$BIN_DIR/pi_rust_single$EXT" -ErrorAction SilentlyContinue
    Copy-Item "rust/target/release/monte_carlo_parallel$EXT" "$BIN_DIR/pi_rust_parallel$EXT" -ErrorAction SilentlyContinue
    
    Write-Host "Rust build complete!" -ForegroundColor Green
}

# Goビルド
function Build-Go {
    Write-Host "Building Go..." -ForegroundColor Green
    New-DirectoryIfNotExists $BIN_DIR
    
    $GO = Get-Command go -ErrorAction SilentlyContinue
    if (-not $GO) {
        Write-Host "Warning: go not found. Skipping Go build." -ForegroundColor Yellow
        return
    }
    
    Push-Location go
    & go build -ldflags="-s -w" -o "../$BIN_DIR/pi_go_single$EXT" monte_carlo_single.go xoshiro256.go
    if ($LASTEXITCODE -ne 0) { 
        Pop-Location
        throw "Go single build failed" 
    }
    
    & go build -ldflags="-s -w" -o "../$BIN_DIR/pi_go_parallel$EXT" monte_carlo_parallel.go xoshiro256.go
    if ($LASTEXITCODE -ne 0) { 
        Pop-Location
        throw "Go parallel build failed" 
    }
    Pop-Location
    
    Write-Host "Go build complete!" -ForegroundColor Green
}

# Javaビルド
function Build-Java {
    Write-Host "Building Java..." -ForegroundColor Green
    New-DirectoryIfNotExists $BUILD_DIR
    
    $JAVAC = Get-Command javac -ErrorAction SilentlyContinue
    if (-not $JAVAC) {
        Write-Host "Warning: javac not found. Skipping Java build." -ForegroundColor Yellow
        return
    }
    
    & javac -d $BUILD_DIR java/*.java
    if ($LASTEXITCODE -ne 0) { throw "Java build failed" }
    
    Write-Host "Java build complete!" -ForegroundColor Green
}

# Fortranビルド
function Build-Fortran {
    Write-Host "Building Fortran..." -ForegroundColor Green
    New-DirectoryIfNotExists $BIN_DIR
    
    $FC = Get-Command gfortran -ErrorAction SilentlyContinue
    if (-not $FC) {
        Write-Host "Warning: gfortran not found. Skipping Fortran build." -ForegroundColor Yellow
        return
    }
    
    # モジュールを先にコンパイル（.modファイルを生成）
    & gfortran $FFLAGS.Split(' ') -c fortran/xoshiro256.f90 -J fortran
    if ($LASTEXITCODE -ne 0) { throw "Fortran module build failed" }
    
    # メインプログラムをコンパイル
    & gfortran $FFLAGS.Split(' ') -o "$BIN_DIR/pi_fortran_single$EXT" -J fortran fortran/xoshiro256.f90 fortran/monte_carlo_single.f90
    if ($LASTEXITCODE -ne 0) { throw "Fortran single build failed" }
    
    & gfortran $FFLAGS.Split(' ') -o "$BIN_DIR/pi_fortran_parallel$EXT" -J fortran fortran/xoshiro256.f90 fortran/monte_carlo_parallel.f90
    if ($LASTEXITCODE -ne 0) { throw "Fortran parallel build failed" }
    
    Write-Host "Fortran build complete!" -ForegroundColor Green
}

# メイン処理
Write-Host "=== Monte Carlo Pi Benchmark Build Script ===" -ForegroundColor Cyan
Write-Host ""

switch ($Target) {
    "all" {
        Write-Host "Building all languages..." -ForegroundColor Cyan
        Write-Host "Python: No build required (interpreted)" -ForegroundColor Gray
        Build-C
        Build-Cpp
        Build-Rust
        Build-Go
        Build-Java
        Build-Fortran
        Write-Host ""
        Write-Host "Build complete!" -ForegroundColor Green
    }
    "c" { Build-C }
    "cpp" { Build-Cpp }
    "rust" { Build-Rust }
    "go" { Build-Go }
    "java" { Build-Java }
    "fortran" { Build-Fortran }
    "clean" {
        Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
        if (Test-Path $BIN_DIR) { Remove-Item -Recurse -Force $BIN_DIR }
        if (Test-Path $BUILD_DIR) { Remove-Item -Recurse -Force $BUILD_DIR }
        if (Test-Path "rust/target") {
            Push-Location rust
            & cargo clean
            Pop-Location
        }
        Write-Host "Clean complete!" -ForegroundColor Green
    }
    default {
        Write-Host "Unknown target: $Target" -ForegroundColor Red
        Write-Host "Usage: .\build.ps1 [all|c|cpp|rust|go|java|fortran|clean]" -ForegroundColor Yellow
        exit 1
    }
}
