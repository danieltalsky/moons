! mercury_constants.f03
!
! adapted from an original Fortran 77 include
! MERCURY.INC    (ErikSoft   4 March 2001)
! Original Author: John E. Chambers

module mercury_constants

   use iso_fortran_env
   implicit none

! Parameters that you may want to alter at some point:
!
! NMAX  = maximum number of bodies
! CMAX  = maximum number of close-encounter minima monitored simultaneously
! NMESS = maximum number of messages in message.in
! HUGE  = an implausibly large number
! NFILES = maximum number of files that can be open at the same time

   integer, parameter :: NMAX = 50000
   integer, parameter :: CMAX = 5000
   integer, parameter :: NMESS = 200
   integer, parameter :: NFILES = 50

   real(8), parameter :: HUGE = 9.9d29

! Constants:
!
! DR = conversion factor from degrees to radians
! K2 = Gaussian gravitational constant squared
! AU = astronomical unit in cm
! MSUN = mass of the Sun in g

   real(8), parameter :: PI = 3.141592653589793d0
   real(8), parameter :: TWOPI = PI*2.d0
   real(8), parameter :: PIBY2 = PI*0.5d0
   real(8), parameter :: DR = PI/180.d0
   real(8), parameter :: K2 = 2.959122082855911d-4
   real(8), parameter :: AU = 1.4959787e13
   real(8), parameter :: MSUN = 1.9891e33

end module mercury_constants
