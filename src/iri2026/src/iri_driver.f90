program iri_driver
!! Command-line driver for the IRI-2026 International Reference Ionosphere.
!!
!! Updated to IRI-2026 by Xiangning Chu, Laboratory for Atmospheric and Space
!! Physics (LASP), University of Colorado Boulder, 2026.
!! Derived from the iri2020 driver by Michael Hirsch / space-physics
!! (https://github.com/space-physics/iri2020, MIT license).
!! The IRI model is developed by D. Bilitza and the COSPAR/URSI IRI Working
!! Group (https://irimodel.org).

use, intrinsic:: iso_fortran_env, only: stderr=>error_unit, stdout=>output_unit

implicit none

logical :: jf(50)
integer, parameter :: jmag = 0
integer :: iyyyy, mmdd, Nalt
real :: glat, glon, dhour
integer :: ymdhms(6)
real:: alt_km_range(3)


real :: oarr(100), outf(20,1000)
real :: tecbo, tecto
real, allocatable :: altkm(:)
character(1024) :: argv
integer :: i

!> jf switch description: comment block at the top of IRI_SUB in irisub.for
!> and https://irimodel.org/IRI-Switches-options.pdf
!> The "standard version" column of that table is the IRI-2026 recommended
!> set (also applied by iritest.for): jf(4,5,6,23,30,33,35,39,40,47)=.false.,
!> all others .true.  This driver keeps two wrapper choices from iri2020:
!> jf(22)=.false. (ion densities in m^-3) and jf(34)=.false. (messages off).

jf = .true.
!> jf(4) = .false. B0,B1: ABT-2009 (jf(31)) instead of Bil-2000 table  (IRI-2026 default)
!> jf(5) = .false. foF2: URSI coefficients instead of CCIR              (IRI-2026 default)
!> jf(6) = .false. Ni: RBV-2010 & TBT-2015 instead of DS-1995 & DY-1985 (IRI-2026 default)
jf(4:6) = .false.
!> jf(22) = .false. ion densities in m^-3 instead of percent            (wrapper choice, as iri2020)
!> jf(23) = .false. Te topside: TBPS-2026 instead of Bil-1985           (IRI-2026 default)
jf(22:23) = .false.
!> jf(30) = .false. with jf(29)=.true.: IRIcor2 topside                 (IRI-2026 default)
jf(30) = .false.
!> jf(33) = .false. auroral boundary model off                          (IRI-2026 default)
jf(33) = .false.
!> jf(34) = .false. messages off                                        (wrapper choice, as iri2020)
jf(34) = .false.
!> jf(35) = .false. foE storm model off                                 (IRI-2026 default)
jf(35) = .false.
!> jf(39) = .false. hmF2 from new models instead of M3000F2             (IRI-2026 default)
!> jf(40) = .false. hmF2: Shubin-COSMIC model instead of AMTB           (IRI-2026 default)
jf(39:40) = .false.
!> jf(47) = .false. CGM coordinate computation off                      (IRI-2026 default)
jf(47) = .false.
!> New in IRI-2026, left at their .true. defaults:
!> jf(38) IBP-2023 plasma bubble probability -> OARR(92)
!> jf(42) Te-TBPS with PF10.7 dependence
!> jf(45),jf(46) sporadic-E occurrence probability ESPROB -> OARR(91)
!> jf(48) Ti Truhlik-2021;  jf(49) Ozhogin plasmasphere;  jf(50) without plasmapause
!> jf(12) left .true. as in iri2020 (messages to KONSOL; irrelevant with jf(34)=.false.)

! --- command line input
if (command_argument_count() /= 11) then
  write(stderr,*) 'need input parameters: year month day hour minute second glat glon min_alt_km max_alt_km step_alt_km'
  stop 1
endif

do i=1,6
  call get_command_argument(i,argv)
  read(argv,*) ymdhms(i)
enddo

call get_command_argument(7, argv)
read(argv,*) glat

call get_command_argument(8, argv)
read(argv,*) glon

do i = 1,3
  call get_command_argument(8+i, argv)
  read(argv,*) alt_km_range(i)
enddo

! --- parse
Nalt = int((alt_km_range(2) - alt_km_range(1)) / alt_km_range(3)) + 1
allocate(altkm(Nalt))


altkm(1) = alt_km_range(1)
do i = 2,Nalt
  altkm(i) = altkm(i-1) + alt_km_range(3)
enddo

iyyyy = ymdhms(1)
mmdd = ymdhms(2) * 100 + ymdhms(3)
dhour = ymdhms(4) + ymdhms(5) / 60. + ymdhms(6) / 3600.

!> read the indices files once (ig_rz.dat on unit 12, apf107.dat on unit 13)
call read_ig_rz
call readapf107

!> dhour+25 selects Universal Time
call IRI_SUB(JF, JMAG, glat, glon, IYYYY, MMDD, DHOUR+25., &
     alt_km_range(1), alt_km_range(2), alt_km_range(3), &
     OUTF,OARR)

!> TEC from 0 km to the top of the requested altitude range, as in iri2020.
!> IRITEC(ALATI,ALONG,jmag,jf,iy,md,hour,hbeg,hend,hstep,oarr,tecbo,tecto) in iritec.for
call IRITEC(glat, glon, jmag, jf, iyyyy, mmdd, dhour+25., &
            0., alt_km_range(2), 0.1, &
            oarr, tecbo, tecto)

oarr(37) = tecbo + tecto
oarr(38) = tecto / oarr(37) * 100

!> altitude, then OUTF(1:11): Ne Tn Ti Te O+ H+ He+ O2+ NO+ Cluster N+
do i = 1,Nalt
  print '(F10.3, 11ES16.8)', altkm(i), outf(:11,i)
enddo

!> OARR(1:100); see the OARR table in irisub.for.  OARR(100) = foF2 (local patch).
print '(/,100ES16.8)', oarr

end program
