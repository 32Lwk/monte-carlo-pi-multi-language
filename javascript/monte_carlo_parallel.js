const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const Xoshiro256 = require('./xoshiro256.js');
const os = require('os');

const PI_THEORETICAL = 3.141592653589793238462643383279502884197;
const SEED_MULTIPLIER = 0x9E3779B97F4A7C15n;

if (isMainThread) {
    function calculatePi(iterations, numWorkers) {
        return new Promise((resolve, reject) => {
            const iterationsPerWorker = Math.floor(iterations / numWorkers);
            const baseSeed = 12345n;
            const workers = [];
            const results = [];
            let completed = 0;
            
            for (let i = 0; i < numWorkers; i++) {
                const worker = new Worker(__filename, {
                    workerData: {
                        iterationsPerWorker,
                        threadId: i,
                        baseSeed: baseSeed.toString()
                    }
                });
                
                worker.on('message', (insideCircle) => {
                    results[i] = insideCircle;
                    completed++;
                    
                    if (completed === numWorkers) {
                        const totalInside = results.reduce((a, b) => a + b, 0);
                        const piEstimate = 4.0 * totalInside / iterations;
                        const error = Math.abs(piEstimate - PI_THEORETICAL);
                        resolve({ piEstimate, error });
                    }
                });
                
                worker.on('error', reject);
                workers.push(worker);
            }
        });
    }
    
    async function main() {
        const iterations = 100000000;
        const numWorkers = os.cpus().length;
        
        const start = process.hrtime.bigint();
        const { piEstimate, error } = await calculatePi(iterations, numWorkers);
        const end = process.hrtime.bigint();
        
        const elapsedMs = Number(end - start) / 1e6;
        
        console.log(JSON.stringify({
            language: "JavaScript",
            variant: "standard",
            version: process.version,
            mode: "parallel",
            iterations: iterations,
            pi_estimate: piEstimate,
            error: error,
            time_ms: elapsedMs,
            memory_mb: 0.0,
            cache_misses: 0,
            lines_of_code: 0,
            compiler_flags: "N/A (interpreted)",
            cpu_model: "N/A",
            cpu_cores: numWorkers,
            thread_count: numWorkers,
            os: process.platform,
            os_version: "N/A",
            compiler: "Node.js",
            simd_detected: false,
            simd_instructions: []
        }, null, 2));
    }
    
    main().catch(console.error);
} else {
    // ワーカースレッド
    const { iterationsPerWorker, threadId, baseSeed } = workerData;
    const threadSeed = BigInt(baseSeed) + (BigInt(threadId) * SEED_MULTIPLIER);
    const rng = new Xoshiro256(threadSeed);
    
    let insideCircle = 0;
    
    for (let i = 0; i < iterationsPerWorker; i++) {
        const x = rng.nextDouble();
        const y = rng.nextDouble();
        
        if (x * x + y * y <= 1.0) {
            insideCircle++;
        }
    }
    
    parentPort.postMessage(insideCircle);
}

