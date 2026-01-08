import java.util.concurrent.*;

public class MonteCarloParallel {
    private static final double PI_THEORETICAL = 3.141592653589793238462643383279502884197;
    private static final long SEED_MULTIPLIER = 0x9E3779B97F4A7C15L;

    public static double[] calculatePi(long iterations, int numThreads, boolean pureMode) {
        // 純粋モード: GCを事前実行
        if (pureMode) {
            System.gc();
            try {
                Thread.sleep(100);  // GC完了を待つ
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        long iterationsPerThread = iterations / numThreads;
        long baseSeed = 12345L;

        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        List<Future<Long>> futures = new ArrayList<>();

        for (int i = 0; i < numThreads; i++) {
            final int threadId = i;
            futures.add(executor.submit(() -> {
                long threadSeed = baseSeed + (threadId * SEED_MULTIPLIER);
                Xoshiro256 rng = new Xoshiro256(threadSeed);

                long insideCircle = 0;
                for (long j = 0; j < iterationsPerThread; j++) {
                    double x = rng.nextDouble();
                    double y = rng.nextDouble();

                    if (x * x + y * y <= 1.0) {
                        insideCircle++;
                    }
                }

                return insideCircle;
            }));
        }

        long totalInside = 0;
        for (Future<Long> future : futures) {
            try {
                totalInside += future.get();
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        }

        executor.shutdown();

        double piEstimate = 4.0 * totalInside / iterations;
        double error = Math.abs(piEstimate - PI_THEORETICAL);

        return new double[]{piEstimate, error};
    }

    public static void main(String[] args) {
        long iterations = 100_000_000L;
        int numThreads = Runtime.getRuntime().availableProcessors();
        boolean pureMode = args.length > 0 && args[0].equals("--pure");

        long start = System.nanoTime();
        double[] result = calculatePi(iterations, numThreads, pureMode);
        long end = System.nanoTime();

        double elapsedMs = (end - start) / 1_000_000.0;

        System.out.println("{");
        System.out.println("  \"language\": \"Java\",");
        System.out.println("  \"variant\": \"standard\",");
        System.out.println("  \"version\": \"" + System.getProperty("java.version") + "\",");
        System.out.println("  \"mode\": \"parallel\",");
        System.out.println("  \"gc_mode\": \"" + (pureMode ? "pure" : "default") + "\",");
        System.out.println("  \"iterations\": " + iterations + ",");
        System.out.printf("  \"pi_estimate\": %.15f,\n", result[0]);
        System.out.printf("  \"error\": %.15f,\n", result[1]);
        System.out.printf("  \"time_ms\": %.2f,\n", elapsedMs);
        System.out.println("  \"memory_mb\": 0.0,");
        System.out.println("  \"cache_misses\": 0,");
        System.out.println("  \"lines_of_code\": 0,");
        System.out.println("  \"compiler_flags\": \"javac\",");
        System.out.println("  \"cpu_model\": \"N/A\",");
        System.out.println("  \"cpu_cores\": " + numThreads + ",");
        System.out.println("  \"thread_count\": " + numThreads + ",");
        System.out.println("  \"os\": \"" + System.getProperty("os.name") + "\",");
        System.out.println("  \"os_version\": \"N/A\",");
        System.out.println("  \"compiler\": \"javac\",");
        System.out.println("  \"simd_detected\": false,");
        System.out.println("  \"simd_instructions\": []");
        System.out.println("}");
    }
}

