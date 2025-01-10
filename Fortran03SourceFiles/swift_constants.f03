module swift_constants

! swift_constants.f03
! adapted from the original swift include by Hal Levinson who
! was extremely excited by being able to declare implicit none!
! SWIFT.INC
! Include file for SWIFT
! Author:  Hal Levison

   implicit NONE    ! you got it baby

!...   Maximum array size
   integer, parameter :: NPLMAX = 202 ! max number of planets, including the Sun
   integer, parameter :: NTPMAX = 2000 ! max number of test particles

!...   Size of the test particle status flag
   integer, parameter :: NSTAT = 3

!...   convergence criteria for danby
   real(kind=8), parameter :: DANBYAC = 1.0d-14, DANBYB = 1.0d-13

!...    loop limits in the Laguerre attempts
   integer, parameter :: NLAG1 = 50, NLAG2 = 400

!...    A small number
   real(kind=8), parameter :: TINY = 4.D-15

!...    trig stuff
   real(kind=8), parameter :: PI = 3.141592653589793D0
   real(kind=8), parameter :: TWOPI = 2.0D0*PI
   real(kind=8), parameter :: PIBY2 = PI/2.0D0
   real(kind=8), parameter :: DEGRAD = 180.0D0/PI

end module swift_constants
