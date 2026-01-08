package main

import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"time"
)

const PI_THEORETICAL = 3.141592653589793238462643383279502884197

func calculatePi(iterations uint64) (float64, float64) {
	rng := NewXoshiro256(12345)
	insideCircle := uint64(0)

	for i := uint64(0); i < iterations; i++ {
		x := rng.NextDouble()
		y := rng.NextDouble()

		if x*x+y*y <= 1.0 {
			insideCircle++
		}
	}

	piEstimate := 4.0 * float64(insideCircle) / float64(iterations)
	error := piEstimate - PI_THEORETICAL
	if error < 0 {
		error = -error
	}

	return piEstimate, error
}

func main() {
	iterations := uint64(100000000)

	start := time.Now()
	piEstimate, error := calculatePi(iterations)
	elapsed := time.Since(start)

	elapsedMs := float64(elapsed.Nanoseconds()) / 1e6

	result := map[string]interface{}{
		"language":      "Go",
		"variant":       "standard",
		"version":       "1.21",
		"mode":          "single",
		"iterations":    iterations,
		"pi_estimate":   piEstimate,
		"error":         error,
		"time_ms":       elapsedMs,
		"memory_mb":     0.0,
		"cache_misses": 0,
		"lines_of_code": 0,
		"compiler_flags": "go build -ldflags=\"-s -w\"",
		"cpu_model":     "N/A",
		"cpu_cores":      runtime.NumCPU(),
		"thread_count":  1,
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

