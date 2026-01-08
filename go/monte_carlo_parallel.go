package main

import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"sync"
	"time"
)

const PI_THEORETICAL = 3.141592653589793238462643383279502884197
const SEED_MULTIPLIER = 0x9E3779B97F4A7C15

func calculatePi(iterations uint64, numGoroutines int) (float64, float64) {
	iterationsPerGoroutine := iterations / uint64(numGoroutines)
	baseSeed := uint64(12345)

	var wg sync.WaitGroup
	results := make([]uint64, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(threadID int) {
			defer wg.Done()

			threadSeed := baseSeed + (uint64(threadID) * SEED_MULTIPLIER)
			rng := NewXoshiro256(threadSeed)

			insideCircle := uint64(0)
			for j := uint64(0); j < iterationsPerGoroutine; j++ {
				x := rng.NextDouble()
				y := rng.NextDouble()

				if x*x+y*y <= 1.0 {
					insideCircle++
				}
			}

			results[threadID] = insideCircle
		}(i)
	}

	wg.Wait()

	totalInside := uint64(0)
	for _, count := range results {
		totalInside += count
	}

	piEstimate := 4.0 * float64(totalInside) / float64(iterations)
	error := piEstimate - PI_THEORETICAL
	if error < 0 {
		error = -error
	}

	return piEstimate, error
}

func main() {
	iterations := uint64(100000000)
	numGoroutines := runtime.NumCPU()

	start := time.Now()
	piEstimate, error := calculatePi(iterations, numGoroutines)
	elapsed := time.Since(start)

	elapsedMs := float64(elapsed.Nanoseconds()) / 1e6

	result := map[string]interface{}{
		"language":      "Go",
		"variant":       "standard",
		"version":       "1.21",
		"mode":          "parallel",
		"iterations":    iterations,
		"pi_estimate":   piEstimate,
		"error":         error,
		"time_ms":       elapsedMs,
		"memory_mb":     0.0,
		"cache_misses": 0,
		"lines_of_code": 0,
		"compiler_flags": "go build -ldflags=\"-s -w\"",
		"cpu_model":     "N/A",
		"cpu_cores":      numGoroutines,
		"thread_count":   numGoroutines,
		"os":            runtime.GOOS,
		"os_version":    "N/A",
		"compiler":      "go",
		"simd_detected": false,
		"simd_instructions": []string{},
	}

	jsonData, _ := json.MarshalIndent(result, "", "  ")
	fmt.Println(string(jsonData))
	os.Exit(0)
}

