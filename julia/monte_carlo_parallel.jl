include("xoshiro256.jl")
using Base.Threads

const PI_THEORETICAL = 3.141592653589793238462643383279502884197
const SEED_MULTIPLIER = 0x9E3779B97F4A7C15

function calculate_pi(iterations::Int64, num_threads::Int)
    iterations_per_thread = iterations ÷ num_threads
    base_seed = UInt64(12345)
    
    results = zeros(Int64, num_threads)
    
    @threads for thread_id in 1:num_threads
        # 推奨方式: シードの加算幅を大きくする
        thread_seed = base_seed + (UInt64(thread_id - 1) * SEED_MULTIPLIER)
        rng = Xoshiro256(thread_seed)
        
        inside_circle = 0
        
        for i in 1:iterations_per_thread
            x = next_double(rng)
            y = next_double(rng)
            
            if x * x + y * y <= 1.0
                inside_circle += 1
            end
        end
        
        results[thread_id] = inside_circle
    end
    
    total_inside = sum(results)
    pi_estimate = 4.0 * total_inside / iterations
    error = abs(pi_estimate - PI_THEORETICAL)
    
    return pi_estimate, error
end

function main()
    iterations = parse(Int64, length(ARGS) > 0 ? ARGS[1] : "100000000")
    num_threads = Threads.nthreads()
    
    start = time()
    pi_estimate, error = calculate_pi(iterations, num_threads)
    elapsed = time() - start
    
    elapsed_ms = elapsed * 1000.0
    
    println("{")
    println("  \"language\": \"Julia\",")
    println("  \"variant\": \"standard\",")
    println("  \"version\": \"$(VERSION)\",")
    println("  \"mode\": \"parallel\",")
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
    println("  \"thread_count\": $num_threads,")
    println("  \"os\": \"$(Sys.KERNEL)\",")
    println("  \"os_version\": \"N/A\",")
    println("  \"compiler\": \"julia\",")
    println("  \"simd_detected\": false,")
    println("  \"simd_instructions\": []")
    println("}")
end

main()

