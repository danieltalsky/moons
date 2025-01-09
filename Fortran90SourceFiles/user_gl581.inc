!%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!
!      USER.INC    (ErikSoft   4 March 2001)
!
!%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!
! Author: Avi Mandell
!
! Parameters that govern migration:
!
!   NMIG = # of migrating planets, in order in BIG file
!   TMAX = Time that migration ends, in days
!   MIGFACT = Ratio of  migration time to TMAX for each planet;
!       if two planets have MIGFACT in the same ratio as their distances,
!       they will migrate with the same inward velocity
!   TMIG0 = Init. mig time, as a fract. of total time
!   SWITCH = Time to switch to expon. mig fade-out, as a fract. of total time
!   GAMMA = Var. mig exponent
!   STOPDIST = Dist. to stop mig at, if reached
!
!   Gas Drag Formulas From Thommes03:
!   GASTIME = Time at which gas drag ceases, in days
!   RHOCONST = Gas density const, in g/cm^3
!   RHOEXP = Gas profile expon.
!   ZCONST = Vert. gas density scale height const., in AU
!   ZEXP = Vert. gas profile expon.
!   CDRAG = Drag constant
!   MEFF = Effective part. mass, in g
!   GCONST = Gravitational const. in AU,Sol.masses,days
!
      integer nmig
      real(kind=8) tmig0,tmax,migfact(1),switch,gamma,stopdist
!
      real(kind=8) gastime,rhoconst,rhoexp,zconst,zexp
      real(kind=8) cdrag,meff,gconst
!
      parameter (nmig = 0)
      parameter (tmax = 36525000.00)
      data migfact /1.00d0/
      parameter (tmig0 = 0.00d0)		!Stan.:0.67
      parameter (switch = 0.5d0)    		!Stan.:0.5
      parameter (gamma = 0.6d0)			!Stan.:0.6
      parameter (stopdist = 0.045d0)

      parameter (gastime = 0)
      parameter (rhoconst = 1.4d-9)            	!Stan.:1.4d-9
      parameter (rhoexp = (11.0/4.0))
      parameter (zconst = 0.0472d0)
      parameter (zexp = (5.0/4.0))
      parameter (cdrag = 1.0d0)
      parameter (meff = 1.26d16)		!1e-23 M_e
      parameter (gconst = 2.9601e-4)
