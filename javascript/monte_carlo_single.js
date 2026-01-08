const Xoshiro256 = require('./xoshiro256.js');

const PI_THEORETICAL = 3.141592653589793238462643383279502884197;

function calculatePi(iterations) {
    const rng = new Xoshiro256(12345);
    let insideCircle = 0;
    
    for (let i = 0; i < iterations; i++) {
        const x = rng.nextDouble();
        const y = rng.nextDouble();
        
        if (x * x + y * y <= 1.0) {
            insideCircle++;
        }
    }
    
    const piEstimate = 4.0 * insideCircle / iterations;
    const error = Math.abs(piEstimate - PI_THEORETICAL);
    
    return { piEstimate, error };
}

function main() {
    const iterations = 100000000;
    
    const start = process.hrtime.bigint();
    const { piEstimate, error } = calculatePi(iterations);
    const end = process.hrtime.bigint();
    
    const elapsedMs = Number(end - start) / 1e6;
    
    console.log(JSON.stringify({
        language: "JavaScript",
        variant: "standard",
        version: process.version,
        mode: "single",
        iterations: iterations,
        pi_estimate: piEstimate,
        error: error,
        time_ms: elapsedMs,
        memory_mb: 0.0,
        cache_misses: 0,
        lines_of_code: 0,
        compiler_flags: "N/A (interpreted)",
        cpu_model: "N/A",
        cpu_cores: require('os').cpus().length,
        thread_count: 1,
        os: process.platform,
        os_version: "N/A",
        compiler: "Node.js",
        simd_detected: false,
        simd_instructions: []
    }, null, 2));
}

main();

