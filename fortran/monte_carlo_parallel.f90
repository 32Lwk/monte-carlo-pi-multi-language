program monte_carlo_parallel
    use xoshiro256_module
    use omp_lib
    implicit none
    
    real(8), parameter :: PI_THEORETICAL = 3.141592653589793238462643383279502884197d0
    integer(8), parameter :: SEED_MULTIPLIER = z'9E3779B97F4A7C15'  ! 16進数リテラル
    integer(8), parameter :: iterations = 100000000_8
    integer(8), parameter :: base_seed = 12345_8
    integer :: num_threads, thread_id
    integer(8) :: iterations_per_thread, i, inside_circle, total_inside
    real(8) :: x, y, pi_estimate, error
    real(8) :: start_time, end_time, elapsed_ms
    type(xoshiro256_type) :: rng
    integer(8), allocatable :: results(:)
    
    num_threads = omp_get_max_threads()
    iterations_per_thread = iterations / num_threads
    allocate(results(num_threads))
    
    call cpu_time(start_time)
    
    !$omp parallel private(thread_id, rng, i, x, y, inside_circle) shared(results, iterations_per_thread, base_seed)
        thread_id = omp_get_thread_num()
        
        ! 推奨方式: シードの加算幅を大きくする
        call xoshiro256_init(rng, base_seed + (thread_id * SEED_MULTIPLIER))
        inside_circle = 0
        
        do i = 1, iterations_per_thread
            x = xoshiro256_next_double(rng)
            y = xoshiro256_next_double(rng)
            
            if (x * x + y * y <= 1.0d0) then
                inside_circle = inside_circle + 1
            end if
        end do
        
        results(thread_id + 1) = inside_circle
    !$omp end parallel
    
    total_inside = sum(results)
    pi_estimate = 4.0d0 * real(total_inside, 8) / real(iterations, 8)
    error = abs(pi_estimate - PI_THEORETICAL)
    
    call cpu_time(end_time)
    elapsed_ms = (end_time - start_time) * 1000.0d0
    
    write(*, '(a)') '{'
    write(*, '(a)') '  "language": "Fortran",'
    write(*, '(a)') '  "variant": "standard",'
    write(*, '(a)') '  "version": "F2008",'
    write(*, '(a)') '  "mode": "parallel",'
    write(*, '(a,i0,a)') '  "iterations": ', iterations, ','
    write(*, '(a,f0.15,a)') '  "pi_estimate": ', pi_estimate, ','
    write(*, '(a,f0.15,a)') '  "error": ', error, ','
    write(*, '(a,f0.2,a)') '  "time_ms": ', elapsed_ms, ','
    write(*, '(a)') '  "memory_mb": 0.0,'
    write(*, '(a)') '  "cache_misses": 0,'
    write(*, '(a)') '  "lines_of_code": 0,'
    write(*, '(a)') '  "compiler_flags": "-O3 -march=native -flto -fopenmp",'
    write(*, '(a)') '  "cpu_model": "N/A",'
    write(*, '(a,i0,a)') '  "cpu_cores": ', num_threads, ','
    write(*, '(a,i0,a)') '  "thread_count": ', num_threads, ','
    write(*, '(a)') '  "os": "N/A",'
    write(*, '(a)') '  "os_version": "N/A",'
    write(*, '(a)') '  "compiler": "GCC/GFortran",'
    write(*, '(a)') '  "simd_detected": false,'
    write(*, '(a)') '  "simd_instructions": []'
    write(*, '(a)') '}'
    
    deallocate(results)
    
end program monte_carlo_parallel

