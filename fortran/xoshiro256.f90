! Xoshiro256** - 高速・軽量・高品質な乱数生成器
!
! アルゴリズムの背景:
! - Mersenne Twister (MT19937) は状態空間が大きく（約2.5KB）、
!   キャッシュ効率が悪く、SIMD化の妨げになる
! - Xoshiro256** は軽量（256ビット = 32バイト）、高速、高品質
! - 純粋な演算性能（コンパイラの最適化能力）を比較できる
!
! ビット演算の解説:
! - ishft(x, k) (左シフト): ビットを左に移動
! - ishft(x, -k) (右シフト): ビットを右に移動
! - ieor (XOR): 排他的論理和
! - ior (OR): 論理和
! - iand (AND): 論理積
!
! Fortranでの実装の違い:
! - integer(8)型（64ビット整数）を使用、OpenMPで並列化

module xoshiro256_module
    implicit none
    
    ! 定数定義（モジュールレベル）
    ! 16進数リテラルを直接使用（Fortran 2008以降）
    integer(8), parameter :: MUL1 = z'BF58476D1CE4E5B9'  ! 16進数リテラル
    integer(8), parameter :: MUL2 = z'94D049BB133111EB'  ! 16進数リテラル
    integer(8), parameter :: SHIFT_53 = 9007199254740992_8  ! 2^53
    
    type :: xoshiro256_type
        integer(8) :: state(4)  ! 4つの64ビット整数（合計256ビット）
    end type xoshiro256_type
    
contains
    
    ! 左ローテーション（ビットを左に回転）
    function rotl(x, k) result(res)
        integer(8), intent(in) :: x
        integer, intent(in) :: k
        integer(8) :: res
        res = ior(ishft(x, k), ishft(x, -(64 - k)))
    end function rotl
    
    ! シードから初期状態を生成
    subroutine xoshiro256_init(rng, seed)
        type(xoshiro256_type), intent(out) :: rng
        integer(8), intent(in) :: seed
        integer(8) :: s
        integer :: i
        
        s = seed
        
        ! SplitMix64風の初期化
        do i = 1, 4
            s = ieor(s, ishft(s, -30))
            s = s * MUL1
            s = ieor(s, ishft(s, -27))
            s = s * MUL2
            s = ieor(s, ishft(s, -31))
            rng%state(i) = s
        end do
    end subroutine xoshiro256_init
    
    ! 次の乱数を生成（Xoshiro256**アルゴリズム）
    function xoshiro256_next(rng) result(res)
        type(xoshiro256_type), intent(inout) :: rng
        integer(8) :: res
        integer(8) :: t
        
        ! 結果 = rotl(state(2) * 5, 7) * 9
        res = rotl(rng%state(2) * 5_8, 7) * 9_8
        
        ! 状態の更新
        t = ishft(rng%state(2), 17)
        
        ! XOR演算で状態を混合
        rng%state(3) = ieor(rng%state(3), rng%state(1))
        rng%state(4) = ieor(rng%state(4), rng%state(2))
        rng%state(2) = ieor(rng%state(2), rng%state(3))
        rng%state(1) = ieor(rng%state(1), rng%state(4))
        
        rng%state(3) = ieor(rng%state(3), t)
        
        ! 状態(4) = rotl(state(2), 45)
        rng%state(4) = rotl(rng%state(2), 45)
    end function xoshiro256_next
    
    ! 0.0以上1.0未満の浮動小数点数を生成
    function xoshiro256_next_double(rng) result(res)
        type(xoshiro256_type), intent(inout) :: rng
        real(8) :: res
        integer(8) :: temp
        
        temp = xoshiro256_next(rng)
        res = real(ishft(temp, -11), 8) * (1.0d0 / real(SHIFT_53, 8))
    end function xoshiro256_next_double
    
end module xoshiro256_module

