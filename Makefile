# Makefile for Monte Carlo Pi Benchmark
# Windows/Linux対応

ifeq ($(OS),Windows_NT)
    EXT := .exe
    PYTHON := python
    JULIA := julia
    NODE := node
    JAVAC := javac
    JAVA := java
else
    EXT :=
    PYTHON := python3
    JULIA := julia
    NODE := node
    JAVAC := javac
    JAVA := java
endif

# コンパイラフラグ
CFLAGS := -O3 -march=native -flto -std=c99
CXXFLAGS := -O3 -march=native -flto -std=c++17
FFLAGS := -O3 -march=native -flto -fopenmp
RUSTFLAGS := -C target-cpu=native

# ビルドディレクトリ
BUILD_DIR := build
BIN_DIR := bin

.PHONY: all build clean run simd-check

all: build

build: $(BIN_DIR) $(BUILD_DIR)
	@echo "Building all languages..."
	@$(MAKE) build-python
	@$(MAKE) build-c
	@$(MAKE) build-cpp
	@$(MAKE) build-rust
	@$(MAKE) build-go
	@$(MAKE) build-java
	@$(MAKE) build-fortran
	@echo "Build complete!"

build-python:
	@echo "Python: No build required (interpreted)"

build-c: $(BIN_DIR)/pi_c_single$(EXT) $(BIN_DIR)/pi_c_parallel$(EXT)

$(BIN_DIR)/pi_c_single$(EXT): c/monte_carlo_single.c c/xoshiro256.c c/xoshiro256.h
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ c/monte_carlo_single.c c/xoshiro256.c -lm

$(BIN_DIR)/pi_c_parallel$(EXT): c/monte_carlo_parallel.c c/xoshiro256.c c/xoshiro256.h
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ c/monte_carlo_parallel.c c/xoshiro256.c -lm -lpthread

build-cpp: $(BIN_DIR)/pi_cpp_single$(EXT) $(BIN_DIR)/pi_cpp_parallel$(EXT)

$(BIN_DIR)/pi_cpp_single$(EXT): cpp/monte_carlo_single.cpp cpp/xoshiro256.cpp cpp/xoshiro256.hpp
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ cpp/monte_carlo_single.cpp cpp/xoshiro256.cpp

$(BIN_DIR)/pi_cpp_parallel$(EXT): cpp/monte_carlo_parallel.cpp cpp/xoshiro256.cpp cpp/xoshiro256.hpp
	@mkdir -p $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ cpp/monte_carlo_parallel.cpp cpp/xoshiro256.cpp -pthread

build-rust:
	@mkdir -p $(BIN_DIR)
	RUSTFLAGS="$(RUSTFLAGS)" cargo build --release --manifest-path rust/Cargo.toml
	@cp rust/target/release/monte_carlo_single$(EXT) $(BIN_DIR)/pi_rust_single$(EXT)
	@cp rust/target/release/monte_carlo_parallel$(EXT) $(BIN_DIR)/pi_rust_parallel$(EXT)

build-go:
	@mkdir -p $(BIN_DIR)
	cd go && go build -ldflags="-s -w" -o ../$(BIN_DIR)/pi_go_single$(EXT) monte_carlo_single.go xoshiro256.go
	cd go && go build -ldflags="-s -w" -o ../$(BIN_DIR)/pi_go_parallel$(EXT) monte_carlo_parallel.go xoshiro256.go

build-java:
	@mkdir -p $(BUILD_DIR)
	$(JAVAC) -d $(BUILD_DIR) java/*.java

build-fortran: $(BIN_DIR)/pi_fortran_single$(EXT) $(BIN_DIR)/pi_fortran_parallel$(EXT)

$(BIN_DIR)/pi_fortran_single$(EXT): fortran/monte_carlo_single.f90 fortran/xoshiro256.f90
	@mkdir -p $(BIN_DIR)
	$(FC) $(FFLAGS) -o $@ fortran/xoshiro256.f90 fortran/monte_carlo_single.f90

$(BIN_DIR)/pi_fortran_parallel$(EXT): fortran/monte_carlo_parallel.f90 fortran/xoshiro256.f90
	@mkdir -p $(BIN_DIR)
	$(FC) $(FFLAGS) -o $@ fortran/xoshiro256.f90 fortran/monte_carlo_parallel.f90

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

run:
	@$(PYTHON) benchmark/runner.py

simd-check:
	@$(PYTHON) benchmark/simd_check.py

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BIN_DIR) $(BUILD_DIR)
	@cd rust && cargo clean
	@echo "Clean complete!"

