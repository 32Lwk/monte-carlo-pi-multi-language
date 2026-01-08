include("xoshiro256.jl")

const PI_THEORETICAL = 3.141592653589793238462643383279502884197

function calculate_pi(iterations::Int64)
    rng = Xoshiro256(UInt64(12345))
    inside_circle = 0
    
    for i in 1:iterations
        x = next_double(rng)
        y = next_double(rng)
        
        if x * x + y * y <= 1.0
            inside_circle += 1
        end
    end
    
    pi_estimate = 4.0 * inside_circle / iterations
    error = abs(pi_estimate - PI_THEORETICAL)
    
    return pi_estimate, error
end

function main()
    iterations = 100_000_000
    
    start = time()
    pi_estimate, error = calculate_pi(iterations)
    elapsed = time() - start
    
    elapsed_ms = elapsed * 1000.0
    
    println("{")
    println("  \"language\": \"Julia\",")
    println("  \"variant\": \"standard\",")
    println("  \"version\": \"$(VERSION)\",")
    println("  \"mode\": \"single\",")
    println("  \"iterations\": $iterations,")
    println("  \"pi_estimate\": $pi_estimate,")
    println("  \"error\": $error,")
    println("  \"time_ms\": $elapsed_ms,")
    println("  \"memory_mb\": 0.0,")
    println("  \"cache_misses\": 0,")
    println("  \"lines_of_code\": 0,")
    println("  \"compiler_flags\": \"N/A (JIT compiled)\",")
    println("  \"cpu_model\": \"N/A\",")
    println("  \"cpu_cores\": $(Sys.CPU_THREADS),")
    println("  \"thread_count\": 1,")
    println("  \"os\": \"$(Sys.KERNEL)\",")
    println("  \"os_version\": \"N/A\",")
    println("  \"compiler\": \"julia\",")
    println("  \"simd_detected\": false,")
    println("  \"simd_instructions\": []")
    println("}")
end

main()

