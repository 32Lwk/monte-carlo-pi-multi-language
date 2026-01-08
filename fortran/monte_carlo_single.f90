program monte_carlo_single
    use xoshiro256_module
    implicit none
    
    real(8), parameter :: PI_THEORETICAL = 3.141592653589793238462643383279502884197d0
    integer(8), parameter :: iterations = 100000000_8
    type(xoshiro256_type) :: rng
    integer(8) :: i, inside_circle
    real(8) :: x, y, pi_estimate, error
    real(8) :: start_time, end_time, elapsed_ms
    
    call cpu_time(start_time)
    
    call xoshiro256_init(rng, 12345_8)
    inside_circle = 0
    
    do i = 1, iterations
        x = xoshiro256_next_double(rng)
        y = xoshiro256_next_double(rng)
        
        if (x * x + y * y <= 1.0d0) then
            inside_circle = inside_circle + 1
        end if
    end do
    
    pi_estimate = 4.0d0 * real(inside_circle, 8) / real(iterations, 8)
    error = abs(pi_estimate - PI_THEORETICAL)
    
    call cpu_time(end_time)
    elapsed_ms = (end_time - start_time) * 1000.0d0
    
    write(*, '(a)') '{'
    write(*, '(a)') '  "language": "Fortran",'
    write(*, '(a)') '  "variant": "standard",'
    write(*, '(a)') '  "version": "F2008",'
    write(*, '(a)') '  "mode": "single",'
    write(*, '(a,i0,a)') '  "iterations": ', iterations, ','
    write(*, '(a,f0.15,a)') '  "pi_estimate": ', pi_estimate, ','
    write(*, '(a,f0.15,a)') '  "error": ', error, ','
    write(*, '(a,f0.2,a)') '  "time_ms": ', elapsed_ms, ','
    write(*, '(a)') '  "memory_mb": 0.0,'
    write(*, '(a)') '  "cache_misses": 0,'
    write(*, '(a)') '  "lines_of_code": 0,'
    write(*, '(a)') '  "compiler_flags": "-O3 -march=native -flto",'
    write(*, '(a)') '  "cpu_model": "N/A",'
    write(*, '(a)') '  "cpu_cores": 1,'
    write(*, '(a)') '  "thread_count": 1,'
    write(*, '(a)') '  "os": "N/A",'
    write(*, '(a)') '  "os_version": "N/A",'
    write(*, '(a)') '  "compiler": "GCC/GFortran",'
    write(*, '(a)') '  "simd_detected": false,'
    write(*, '(a)') '  "simd_instructions": []'
    write(*, '(a)') '}'
    
end program monte_carlo_single

