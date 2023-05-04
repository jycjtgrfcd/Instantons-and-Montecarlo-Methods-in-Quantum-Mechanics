import numpy as np
import format_strings as fs
import random

#------------------------------------------------------------------------------
# Lattice calculation in quantum mechanics.
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Action m/2(\dot x)^2+k(x^2-f^2)^2, units 2m=k=1.
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# Calculate partition function from adiabatic switching.
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#   f       minimum of harmonic oxillator: (x^2-f^2)^2
#   n       number of lattice points in the euclidean time direction (n=800)
#   a       lattice spacing (a=0.05)
#   ih      ih=0: cold start, x_i=-f; ih=1: hot start, x_i=random
#   neq     number of equlibration sweeps before the first measurement (neq=100)
#   nmc     number of Monte Carlo sweeps (nmc=10^5)
#   dx      width of Gaussian distribution used for MonteCarlo update: x_i^(n)-->x_i^(n+1)
#   np      number of points on which the correlation functions are measured: 
#           <x_i x_(i+1)>,...,<x_i x_(i+np)> (np=20)
#   nmea    number of measurement of the correlation function given MonteCarlo configuration x_i
#           (nmea=5)
#   npri    number of MonteCarlo configurations between output of averaes to output file (npri=100)
#   nc      number of correlator measurements in a single configuration                                
#   kp      number of sweeps between writeout of complete configuration     
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#   Estimate average and error from xtot and x2tot
#------------------------------------------------------------------------------
#   Input:
#           n: number of measurements
#           xtot: sum of x_i
#           x2tot: sum of x**2
#   Output:
#           xav: average
#           xerr: error estimate
#------------------------------------------------------------------------------  
def disp(n, xtot, x2tot):
    if n < 1:
        raise ValueError("Number of measurements must be at least 1")
    xav = xtot / float(n)
    del2 = x2tot / float(n*n) - xav*xav / float(n)
    if del2 < 0:
        del2 = 0      
    xerr = np.sqrt(del2)  
    return xav, xerr

#------------------------------------------------------------------------------
#   Read input values from console
#------------------------------------------------------------------------------

while True:
    try:
        seed = int(input("Enter the random seed: ")) #change to int() if expecting int-point input
        break # Break out of the loop if input is numeric
    except ValueError:
        print("Invalid input. Please enter a number.")
while True:
    try:
        icold = bool(input("Insert 0 (for a cold start) or 1 (for a hot start): ")) #change to bool() if expecting bool-point input
        break # Break out of the loop if input is numeric
    except ValueError:
        print("Invalid input. Please enter a number.")
while True:
    try:
        nmc = int(input("Enter the number of MonteCarlo sweeps: ")) #change to int() if expecting int-point input
        break # Break out of the loop if input is numeric
    except ValueError:
        print("Invalid input. Please enter a number.")


#------------------------------------------------------------------------------
#   set the values
#------------------------------------------------------------------------------

f      = 1.4
n      = 800
a      = 0.05
neq    = 100
delx   = 0.5
kp     = 5
w      = 5.6
nalpha = 20

dalpha = 1.0/float(nalpha)
beta   = n*a

#------------------------------------------------------------------------------
# echo input parameters
#------------------------------------------------------------------------------
#open txt files

file16 = open('Data/qmswitch.dat', 'w')


# write on a txt file the values

file16.write('lattice qm switch 1.0\n')
file16.write('---------------------\n')
file16.write(fs.f101.format(f,n,a))
file16.write(fs.f102.format(nmc,neq))
file16.write(fs.f104.format(delx,icold))
file16.write(fs.f105.format(w, nalpha))

#------------------------------------------------------------------------------
#     initialize                                                             
#------------------------------------------------------------------------------
random.seed(seed)

stot_sum = 0.0
stot2_sum= 0.0
vav_sum = 0.0
vav2_sum= 0.0
valpha_sum = 0.0
valpha2_sum= 0.0
x_sum = 0
x2_sum = 0
x4_sum = 0
x8_sum = 0

x      = np.zeros(n)
va_av  = np.zeros(2 * nalpha + 1)
va_err = np.zeros(2 * nalpha + 1)
if icold==0:
    for i in range(n):
        x[i]= -f
else:
    for i in range(n):
        x[i] = 2.0 * random.random() * f - f

#------------------------------------------------------------------------------
#     periodic boundary conditions                                           
#------------------------------------------------------------------------------

x[0] = x[n-1]
x    = np.append(x, x[1])

#------------------------------------------------------------------------------
#     initial action                                                       
#------------------------------------------------------------------------------

stot= 0.0         
for i in range(n):
    xp = (x[i+1]-x[i])/a
    t  = 1.0/4.0*xp**2
    v0 = 1.0/4.0*w**2*x[i]**2
    v1 = (x[i]**2-f**2)**2
    v  = v0
    s  = a*(t+v)
    stot += s

#------------------------------------------------------------------------------
#     loop over coupling constant                                                       
#------------------------------------------------------------------------------

e0 = w/2.0
f0 = 1.0/beta*np.log(2.0*np.sinh(w/2.0*beta))
ei = e0

for ialpha in range(2 * nalpha + 1):
    if ialpha <= nalpha:
        alpha = ialpha * dalpha
    else:
        alpha = 2.0 - ialpha * dalpha
    
    nacc = 0
    nhit = 0    
    nconf= 0
    ncor = 0

#------------------------------------------------------------------------------
#    monte carlo sweeps                                                     
#------------------------------------------------------------------------------
    for i in range(nmc):
        nconf += 1
        if i == neq:
            nconf = 0
            stot_sum   = 0.0
            stot2_sum  = 0.0
            vav_sum    = 0.0
            vav2_sum   = 0.0 
            valpha_sum = 0.0
            valpha2_sum= 0.0
            x_sum  = 0.0
            x2_sum = 0.0 
            x4_sum = 0.0
            x8_sum = 0.0

#--------------------------------------------------------------------------
#   one sweep thorough configuration                                       
#--------------------------------------------------------------------------
    for j in range(1,n):
        nhit += 1
        
        xpm   = (x[j]-x[j-1])/a
        xpp   = (x[j+1]-x[j])/a
        t     = 1.0/4.0*(xpm**2+xpp**2)
        v0    = 1.0/4.0*w**2*x[j]**2
        v1    = (x[j]**2-f**2)**2
        v     = alpha*(v1-v0) + v0
        sold  = a*(t+v)
        
        xnew  = x[j] + delx*(2.0*random.random()-1.0)
        
        xpm   = (xnew-x[j-1])/a
        xpp   = (x[j+1]-xnew)/a
        t     = 1.0/4.0*(xpm**2+xpp**2)
        v0    = 1.0/4.0*w**2*xnew**2
        v1    = (xnew**2-f**2)**2
        v     = alpha*(v1-v0) + v0
        
        snew  = a*(t+v)
        dels  = snew-sold
        
        dels  = min(dels,70.0)
        dels  = max(dels,-70.0)
        if np.exp(-dels) > random.random():
            x[j]  = xnew
            nacc += 1
    x[n-1]= x[0]
    x     = np.append(x, x[1])

#--------------------------------------------------------------------------
#   calculate action and other things                                                  
#--------------------------------------------------------------------------
    stot = 0.0
    ttot = 0.0
    vtot = 0.0
    ptot = 0.0
    for j in range(n):
        xp = (x[j+1]-x[j])/a
        t  = 1.0/4.0*xp**2
        v0 = 1.0/4.0*w**2*x[j]**2
        v1 = (x[j]**2-f**2)**2
        v  = alpha*(v1-v0) + v0
        s  = a*(t+v)
        ttot += a*t
        vtot += a*v
        stot += s
        ptot += a*(v1-v0)
    
    if i % kp == 0:
        print("configuration:   ", i, "\n",
              "coupling:        ", alpha, "\n",
              "acceptance rate: ", float(nacc)/float(nhit), "\n",
              "action (T,V):    ", stot, ttot, vtot)

#--------------------------------------------------------------------------
#   include in sample                                                     
#--------------------------------------------------------------------------
    stot_sum    += stot
    stot2_sum   += stot**2
    vav_sum     += vtot/beta
    vav2_sum    += vtot**2/beta
    valpha_sum  += ptot/beta
    valpha2_sum += ptot**2/beta
    
    for k in range(n):
        x_sum  += x[k]
        x2_sum += x[k]**2
        x4_sum += x[k]**4
        x8_sum += x[k]**8

#------------------------------------------------------------------------------
#   averages                                                               
#------------------------------------------------------------------------------
    
    stot_av, stot_err     = disp(nconf, stot_sum, stot2_sum)
    v_av, v_err           = disp(nconf, vav_sum, vav2_sum)
    valpha_av, valpha_err = disp(nconf, valpha_sum, valpha2_sum)
    x_av, x_err           = disp(nconf*n, x_sum, x2_sum)
    x2_av,x2_err          = disp(nconf*n, x2_sum, x4_sum)
    x4_av,x4_err          = disp(nconf*n, x4_sum, x8_sum)
    
    va_av[ialpha]  = valpha_av
    va_err[ialpha] = valpha_err
    
    if ialpha % (2 * nalpha) == 0:
        da = dalpha / 4.0
    else:
        da = dalpha / 2.0
    de = da * valpha_av
    ei = ei + de

#------------------------------------------------------------------------------
#   output                                                               
#------------------------------------------------------------------------------
    file16.write('\n')
    file16.write(fs.f800.format(alpha))
    file16.write(fs.f801.format(stot_av, stot_err))
    file16.write(fs.f806.format(x_av, x_err))
    file16.write(fs.f807.format(x2_av, x2_err))
    file16.write(fs.f808.format(x4_av, x4_err))
    file16.write(fs.f802.format(v_av, v_err))
    file16.write(fs.f809.format(valpha_av, valpha_err))
    file16.write(fs.f810.format(ei, de, e0))
    file16.write('\n')
    
#------------------------------------------------------------------------------
#   final estimate of integral over coupling                                                               
#------------------------------------------------------------------------------

eup_sum = 0.0
eup_err = 0.0
eup_hal = 0.0
edw_sum = 0.0
edw_err = 0.0
edw_hal = 0.0


for ia in range(nalpha+1):
    if ia % nalpha == 0:
        da = dalpha / 4.0
    else:
        da = dalpha / 2.0
    iap = ia + nalpha
    eup_sum += da * va_av[ia]
    eup_err += da * va_err[ia] ** 2
    edw_sum += da * va_av[iap]
    edw_err += da * va_err[iap] ** 2


for ia in range(0, nalpha+1, 2):
    if ia % nalpha == 0:
        da = dalpha / 2.0
    else:
        da = dalpha
    iap = ia + nalpha
    eup_hal += da * va_av[ia]
    edw_hal += da * va_av[iap]

#------------------------------------------------------------------------------
#   uncertainties                                                                         
#------------------------------------------------------------------------------

de     = eup_sum + edw_sum
ei     = e0 + de
de_err = np.sqrt(eup_err + edw_err)
de_hal = eup_hal + edw_hal
de_dif = abs(eup_sum - edw_sum)
de_dis = abs(de - de_hal)/2.0
de_tot = np.sqrt(de_err**2 + de_dif**2 + de_dis**2)

#------------------------------------------------------------------------------
#   output                                                                         
#------------------------------------------------------------------------------

file16.write("input parameters\n")   
file16.write("----------------\n")
file16.write(fs.f811.format(beta, f0, e0))
file16.write("final, initial energy\n")
file16.write(fs.f810.format(ei, de, e0))
file16.write(fs.f812.format(ei, de_tot))
file16.write(fs.f813.format(de_err, de_dif, de_dis))
    
file16.close()




















