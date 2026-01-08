public class MonteCarloSingle {
    private static final double PI_THEORETICAL = 3.141592653589793238462643383279502884197;

    public static double[] calculatePi(long iterations) {
        Xoshiro256 rng = new Xoshiro256(12345);
        long insideCircle = 0;

        for (long i = 0; i < iterations; i++) {
            double x = rng.nextDouble();
            double y = rng.nextDouble();

            if (x * x + y * y <= 1.0) {
                insideCircle++;
            }
        }

        double piEstimate = 4.0 * insideCircle / iterations;
        double error = Math.abs(piEstimate - PI_THEORETICAL);

        return new double[]{piEstimate, error};
    }

    public static void main(String[] args) {
        long iterations = 100_000_000L;

        long start = System.nanoTime();
        double[] result = calculatePi(iterations);
        long end = System.nanoTime();

        double elapsedMs = (end - start) / 1_000_000.0;

        System.out.println("{");
        System.out.println("  \"language\": \"Java\",");
        System.out.println("  \"variant\": \"standard\",");
        System.out.println("  \"version\": \"" + System.getProperty("java.version") + "\",");
        System.out.println("  \"mode\": \"single\",");
        System.out.println("  \"iterations\": " + iterations + ",");
        System.out.printf("  \"pi_estimate\": %.15f,\n", result[0]);
        System.out.printf("  \"error\": %.15f,\n", result[1]);
        System.out.printf("  \"time_ms\": %.2f,\n", elapsedMs);
        System.out.println("  \"memory_mb\": 0.0,");
        System.out.println("  \"cache_misses\": 0,");
        System.out.println("  \"lines_of_code\": 0,");
        System.out.println("  \"compiler_flags\": \"javac\",");
        System.out.println("  \"cpu_model\": \"N/A\",");
        System.out.println("  \"cpu_cores\": " + Runtime.getRuntime().availableProcessors() + ",");
        System.out.println("  \"thread_count\": 1,");
        System.out.println("  \"os\": \"" + System.getProperty("os.name") + "\",");
        System.out.println("  \"os_version\": \"N/A\",");
        System.out.println("  \"compiler\": \"javac\",");
        System.out.println("  \"simd_detected\": false,");
        System.out.println("  \"simd_instructions\": []");
        System.out.println("}");
    }
}

