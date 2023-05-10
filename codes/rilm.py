import format_strings as fs
import numpy as np
import random
from tqdm import tqdm
import functions as fn
import re
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#     random instanton calculation in quantum mechanics.                     
#------------------------------------------------------------------------------
#     action m/2(\dot x)^2+k(x^2-f^2)^2, units 2m=k=1.                       
#------------------------------------------------------------------------------
#     program follows units and conventions of txt file
#------------------------------------------------------------------------------
#   Imput:
#------------------------------------------------------------------------------
#   f       minimum of harmonic oxillator: (x^2-f^2)^2
#   n       number of lattice points in the euclidean time direction (n=800)
#   a       lattice spacing (a=0.05)
#   N_I+A   number of instantons(has to be even). The program displays the one 
#           and two-loop results for the parameters
#   nmc     number of Monte Carlo sweeps (nmc=10^5)
#   n_p      number of points on which the correlation functions are measured: 
#           <x_i x_(i+1)>,...,<x_i x_(i+np)> (np=20)
#   nmea    number of measurement of the correlation function given MonteCarlo 
#           configuration x_i(nmea=5)
#   npri    number of MonteCarlo configurations between output of averaes to 
#           output file (npri=100)
#   nc      number of correlator measurements in a single configuration                                
#   kp      number of sweeps between writeout of complete configuration     
#------------------------------------------------------------------------------
#   Output:
#------------------------------------------------------------------------------
#   Stot        average total action per configuration
#   Vav, Tav    average potential and kinetic energy
#   <x^n>       expectation value <x^n> (n=1,2,3,4)
#   Pi(tau)     euclidean correlation function Pi(tau)=<O(0)O(tau)>,
#               for O=x,x^2,x^3;results are given in the format: tau, Pi(tau),
#               DeltaPi(tau), dlog(Pi)/dtau, Delta[dlog(Pi)/dtau],where 
#               DeltaPi(tau) is the statistical error in Pi(tau)
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#   open files
#------------------------------------------------------------------------------
file16 = open('Data/rilm.dat',       'w')
file17 = open('Data/config.dat',     'w')
file18 = open('Data/trajectory.dat', 'w')
file19 = open('Data/qmdist.dat',     'w')
file20 = open('Data/rcor.dat',       'w')
file21 = open('Data/rcor2.dat',      'w')
file22 = open('Data/rcor3.dat',      'w') 
file30 = open('Data/zdist.dat',      'w')

#------------------------------------------------------------------------------
#   input parameters                                                                 
#------------------------------------------------------------------------------
# open the file for reading
with open('parameters.txt', 'r') as file:
    # read the contents of the file
    contents = file.read()
   
# search for the values of f and a using regular expressions
f      = re.search(r'f\s*=\s*(\d+\.\d+)', contents).group(1)
n      = re.search(r'n\s*=\s*(\d+)', contents).group(1)
a      = re.search(r'a\s*=\s*(\d+\.\d+)', contents).group(1)
icold  = re.search(r'icold\s*=\s*(\d+)', contents).group(1)
neq    = re.search(r'neq\s*=\s*(\d+)', contents).group(1)
nmc    = re.search(r'nmc\s*=\s*(\d+)', contents).group(1)
delx   = re.search(r'delx\s*=\s*(\d+\.\d+)', contents).group(1)
n_p    = re.search(r'n_p\s*=\s*(\d+)', contents).group(1)
kp     = re.search(r'kp\s*=\s*(\d+)', contents).group(1)


# convert the values to integers
f      = float(f)   #separation of wells f (f=1.4)
n      = int(n)     #grid size n<10000 (n=100)
a      = float(a)   #grid spacing a (dtau=0.05)
icold  = int(icold) #cold/hot start (0,1)
neq    = int(neq)   #equilibration sweeps
nmc    = int(nmc)   #monte carlo sweeps
delx   = float(delx)#update x (delx)
n_p    = int(n_p)   #number of points in correlator
kp     = int(kp)    #number of sweeps between cooling

nin = 10
nc = 5
pi  = np.pi

tmax  = n*a
s0    = 4.0/3.0*f**3
dens  = 8*np.sqrt(2.0/pi)*f**2.5*np.exp(-s0)
dens2 = 8*np.sqrt(2.0/pi)*f**2.5*np.exp(-s0-71.0/72.0/s0)
xnin  = dens*tmax 
xnin2 = dens2*tmax
nexp  = int(xnin+0.5)
nexp2 = int(xnin2+0.5)

x  =  np.zeros(n)
z  =  np.zeros(n)     
xcor_av    =  np.zeros(n_p)
xcor_er    =  np.zeros(n_p)
x2cor_av   =  np.zeros(n_p)
x2cor_er   =  np.zeros(n_p)
x3cor_av   =  np.zeros(n_p)
x3cor_er   =  np.zeros(n_p)
x2sub_av   =  np.zeros(n_p)
x2sub_er   =  np.zeros(n_p)      
#------------------------------------------------------------------------------
#     echo input parameters                                                  
#------------------------------------------------------------------------------
file16.write('qm rilm 1.0')   
file16.write('-----------')   
file16.write(fs.f101.format(f,n,a)) 
file16.write(fs.f102.format(nin,nmc)) 
file16.write(fs.f103.format(n_p,nc)) 
file16.write('\n')
file17.write(fs.f444.format(n, nmc/kp, n*a, f)) 

#------------------------------------------------------------------------------
#     parameters for histograms                                              
#------------------------------------------------------------------------------
      
nxhist = 50
xhist_min = -1.5*f
stxhist= 3.0*f/float(nxhist)
nzhist = 40
stzhist= 4.01/float(nzhist)

#------------------------------------------------------------------------------
#   Read input values from console
#------------------------------------------------------------------------------

#while True:
#   try:
#       seed = int(input("Enter the random seed: ")) #change to int() if expecting int-point input
#       break # Break out of the loop if input is numeric
#   except ValueError:
#       print("Invalid input. Please enter a number.")
seed = -1234
random.seed(seed)
#------------------------------------------------------------------------------
#     clear summation arrays                                                 
#------------------------------------------------------------------------------

stot_sum  = 0.0
stot2_sum = 0.0
vtot_sum  = 0.0
vtot2_sum = 0.0
ttot_sum  = 0.0
ttot2_sum = 0.0
tvir_sum  = 0.0
tvir2_sum = 0.0
x_sum     = 0.0
x2_sum    = 0.0
x4_sum    = 0.0
x8_sum    = 0.0

xcor_sum   = np.zeros(n_p)
xcor2_sum  = np.zeros(n_p)
x2cor_sum  = np.zeros(n_p)
x2cor2_sum = np.zeros(n_p)
x3cor_sum  = np.zeros(n_p)
x3cor2_sum = np.zeros(n_p)

ix = np.zeros(nxhist)
iz = np.zeros(nzhist)

nconf = 0
ncor  = 0

#------------------------------------------------------------------------------
#   loop over configurations                                                            
#------------------------------------------------------------------------------

for i in tqdm(range(nmc)):
    nconf = nconf+1
    fn.setup(nin,z,tmax, seed)
    #--------------------------------------------------------------------------
    #   new configuration                                                      
    #--------------------------------------------------------------------------
    for j in range(n):
        xx = a*j
        x[j] = fn.xsum(nin, z, f, xx)
        x[n-1]= x[0]
        x     = np.append(x, x[1])
    #--------------------------------------------------------------------------
    #   distribution of instantons                                             
    #--------------------------------------------------------------------------
    for ii in range(1, nin, 2):
        if ii == 1:
            zm = z[nin-1] - tmax
        else:
            zm = z[ii-2]
        z0 = z[ii-1]
        zp = z[ii]
        zia = min([abs(zp-z0), abs(z0-zm)])
        fn.histogramarray(zia, 0.0, stzhist, nzhist, iz)
    #--------------------------------------------------------------------------
    #   correlation function                                                   
    #--------------------------------------------------------------------------
    for ic in range(nc):
        ncor += 1
        ip0 = int((n-n_p)*random.random())
        x0 = x[ip0]
        for ip in range(n_p):
            x1 = x[ip0+ip]
            xcor = x0*x1
            x2cor = xcor**2
            x3cor = xcor**3
            xcor_sum[ip] += xcor
            xcor2_sum[ip] += xcor**2
            x2cor_sum[ip] += x2cor
            x2cor2_sum[ip] += x2cor**2
            x3cor_sum[ip] += x3cor
            x3cor2_sum[ip] += x3cor**2
#------------------------------------------------------------------------------
#   averages                                                               
#------------------------------------------------------------------------------

stot_av,stot_err = fn.disp(  nconf, stot_sum, stot2_sum)
vtot_av,vtot_err = fn.disp(  nconf, vtot_sum, vtot2_sum)
ttot_av,ttot_err = fn.disp(  nconf, ttot_sum, ttot2_sum)
tvir_av,tvir_err = fn.disp(  nconf, tvir_sum, tvir2_sum)
x_av,x_err       = fn.disp(nconf*n,    x_sum, x2_sum)
x2_av,x2_err     = fn.disp(nconf*n,   x2_sum, x4_sum)
x4_av,x4_err     = fn.disp(nconf*n,   x4_sum, x8_sum)
 
for ip in range(n_p):
    xcor_av[ip],  xcor_er[ip]  = fn.disp(ncor, xcor_sum[ip], xcor2_sum[ip])
    x2cor_av[ip], x2cor_er[ip] = fn.disp(ncor, x2cor_sum[ip], x2cor2_sum[ip])
    x3cor_av[ip], x3cor_er[ip] = fn.disp(ncor, x3cor_sum[ip], x3cor2_sum[ip])

v_av  = vtot_av/tmax
v_err = vtot_err/tmax
t_av  = ttot_av/tmax
t_err = ttot_err/tmax
tv_av = tvir_av/tmax
tv_err= tvir_err/tmax
e_av  = v_av+tv_av
e_err = np.sqrt(v_err**2+tv_err**2)

#------------------------------------------------------------------------------
#     output                                                                 
#------------------------------------------------------------------------------

file16.write('\n')
file16.write(fs.f9901.format(           stot_av, stot_err)) 
file16.write(fs.f9902.format(stot_av/float(nin), stot_err/float(nin))) 
file16.write(fs.f9903.format(               s0)) 
file16.write(fs.f9904.format(  stot_av/(nin*s0), stot_err/(nin*s0))) 
file16.write(fs.f9905.format(              v_av, v_err)) 
file16.write(fs.f9906.format(              t_av, t_err)) 
file16.write(fs.f9907.format(             tv_av, tv_err)) 
file16.write(fs.f9908.format(              e_av, e_err)) 
file16.write(fs.f9909.format(              x_av, x_err)) 
file16.write(fs.f9910.format(              x2_av, x2_err)) 
file16.write(fs.f9911.format(             x4_av, x4_err)) 
file16.write('\n') 

#------------------------------------------------------------------------------
#     correlation function, log derivative                                   
#------------------------------------------------------------------------------

file16.write('# x correlation function\n') 
file20.write('# tau       x(tau)       dx(tau)     dlog\n')
for ip in range(1,n_p):
    dx = (xcor_av[ip-1] - xcor_av[ip]) / xcor_av[ip] / a 
    dxe2 = (xcor_er[ip] / xcor_av[ip])**2 + \
        (xcor_er[ip-1] * xcor_av[ip] / xcor_av[ip]**2)**2
    dxe = np.sqrt(dxe2) / a
    
    file16.write(fs.f555.format(ip*a, xcor_av[ip], xcor_er[ip], dx, dxe)) 
    file20.write(fs.f555.format(ip*a, xcor_av[ip], xcor_er[ip], dx, dxe))     

#------------------------------------------------------------------------------
#     subtracted x^2 correlation function, log derivative                    
#------------------------------------------------------------------------------

xx_sub = x2cor_av[n_p-1]
xx_er  = x2cor_er[n_p-1]
for ip in range(n_p):
    x2sub_av[ip] = x2cor_av[ip]-xx_sub
    x2sub_er[ip] = np.sqrt(x2cor_er[ip]**2+xx_er**2)

file16.write('# x2 correlation function\n') 
file21.write('# tau       x2(tau)      dx2(tau)     dlog\n')
             
for ip in range(n_p-1):
    dx  = (x2sub_av[ip]-x2sub_av[ip+1])/x2sub_av[ip]/a
    dxe2= (x2sub_er[ip+1]/x2sub_av[ip])**2
    +(x2sub_er[ip]*x2sub_av[ip+1]/x2sub_av[ip]**2)**2
    dxe = np.sqrt(dxe2)/a
    file16.write(fs.f555.format(ip*a, x2cor_av[ip], x2cor_er[ip], dx, dxe)) 
    file21.write(fs.f555.format(ip*a, x2cor_av[ip], x2cor_er[ip], dx, dxe)) 

#------------------------------------------------------------------------------
#     x^3 correlation function, log derivative                               
#------------------------------------------------------------------------------

file16.write('# x^3 correlation function\n') 
file22.write('# tau       x(tau)       dx(tau)     dlog\n')
 
for ip in range(n_p-1):
    dx  = (x3cor_av[ip]-x3cor_av[ip+1])/x3cor_av[ip]/a
    dxe2= (x3cor_er[ip+1]/x3cor_av[ip])**2
    +(x3cor_er[ip]*x3cor_av[ip+1]/x3cor_av[ip]**2)**2
    dxe = np.sqrt(dxe2)/a
    file16.write(fs.f555.format(ip*a, x3cor_av[ip], x3cor_er[ip], dx, dxe)) 
    file22.write(fs.f555.format(ip*a, x3cor_av[ip], x3cor_er[ip], dx, dxe)) 
 
#------------------------------------------------------------------------------
#   histograms                                                             
#------------------------------------------------------------------------------

file16.write('\n')
file16.write(' x distribution \n')
fn.plot_histogram(xhist_min, nxhist, ix)
file16.write('\n')
file16.write(' Z_IA distribution \n')
fn.plot_histogram(0.0, nzhist, iz)
for i in range(nzhist):
    xx = (i+0.5)*stzhist
    file30.write(fs.f222.format(xx,iz[i]) )

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
file16.close()
file17.close()
file18.close()
file19.close()
file20.close()
file21.close()
file22.close()
file30.close()


















