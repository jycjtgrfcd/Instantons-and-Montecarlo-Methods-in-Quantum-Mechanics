# Definition of functions
import numpy as np
import matplotlib.pyplot as plt
import random

#------------------------------------------------------------------------------
#     function to include value a in histogram array hist(n)
#     def histogramarray(a, amin, st, m, hist)                
#------------------------------------------------------------------------------
#     a       value to be added to histogram array                        
#     amin    minimum value in histogram                                  
#     st      bin width                                                   
#     m       number of bins                                              
#     hist(n) histogram array                                             
#------------------------------------------------------------------------------
def histogramarray(a, amin, st, m, hist):
    j = (a - amin)/st + 1.000001
    if (j < 1):
        j = 1
    if (j > m):
        j = m
    hist[int(j)-1] += 1
    return

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
#   plot histogram
#       Input:  amin    minimum value in histogram
#               m       number of bins 
#               ist()   histogram array
#------------------------------------------------------------------------------

def plot_histogram(amin, m , ist):
    bins = np.linspace(amin, -amin, m+1)
    plt.hist(bins[:-1], bins, density=True ,weights=ist, histtype='step')
    plt.xlabel('x')
    plt.ylabel('P(x)')
    plt.show()

#------------------------------------------------------------------------------
#   Compute rescaled Hermite polynomials H_i(x)/2^i/sqrt(i!) for i = 0 to n.
#     Parameters:
#       n (int): The highest degree of Hermite polynomials to compute.
#       x (float): The value of x at which to evaluate the Hermite polynomials.
#       p (list): A list of length n+1 to store the computed values of Hermite polynomials.
#------------------------------------------------------------------------------

def hermite3(n, x, p):
    
    p[0] = 1.0
    p[1] = x

    for i in range(2, n + 1):
        p[i] = (x * p[i - 1] - np.sqrt(i - 1.0) * p[i - 2] / 2.0) / np.sqrt(float(i))

#------------------------------------------------------------------------------
#   Define harmonic oscillator wave function
#       Harmonic oscillator wave functions psi(i=0,..,n)=psi_i(x)
#       Parameters:
#           m (float): mass of the harmonic oscillator
#           w (float): frequency of harmonic oscillator
#           n (int): The highest index of the harmonic oscillator wave functions to compute.
#           x (float): The value of x at which to evaluate the harmonic oscillator wave functions.
#           psi (list): A list of length n+1 to store the computed values of the harmonic oscillator wave functions.
#------------------------------------------------------------------------------

def psiosc(m, w, n, x, psi):    

    h = np.zeros(n+1)  # array to store Hermite polynomials

    y = np.sqrt(m * w) * x
    hermite3(n, y, h)

    for i in range(n + 1):
        xnorm = (m * w / np.pi) ** 0.25 * 2.0 ** (i / 2.0)
        psi[i] = xnorm * h[i] * np.exp(-m * w / 2.0 * x ** 2)

    return psi

#------------------------------------------------------------------------------
#   discretized action for configuration x(n)                           
#------------------------------------------------------------------------------
def act(f, a, delx, n, x):
    stot = 0.0
    ttot = 0.0
    vtot = 0.0
    for j in range(n):
        xp = (x[j+1] - x[j]) / a
        t = 1.0 / 4.0 * xp**2
        v = (x[j]**2 - f**2)**2
        s = a * (t + v)
        ttot += a * t
        vtot += a * v
        stot += s
    return stot, ttot, vtot

#------------------------------------------------------------------------------
#     return number and location of (anti) instantons                    
#------------------------------------------------------------------------------
def inst(f, a, delx, n, x, xi, xa, z):
    ni = 0
    na = 0
    nin= 0
    ix = int(np.sign(x[0]))
    for i in range(1,n):
        tau = a * i
        ixp = int(np.sign(x[i]))
        if ixp > ix:
            xi[ni] = tau
            z[nin] = tau
            ni  += 1
            nin += 1         
        elif ixp < ix:
            xa[na] = tau
            z[nin] = tau
            na  += 1
            nin += 1            
        ix = ixp
    return ni, na

#------------------------------------------------------------------------------
#   log derivative                                                         
#------------------------------------------------------------------------------
def dl(xcor1,xcor2,a):      
    dl = (xcor1-xcor2)/(xcor1*a)
    return dl

#------------------------------------------------------------------------------
#     log derivative, error                                                  
#------------------------------------------------------------------------------
def dle(xcor1,xcor2,xcor1e,xcor2e,a):      
    dle2 = (xcor2e/xcor1)**2+(xcor1e*xcor2/xcor1**2)**2
    dle  = np.sqrt(dle2)
    return dle

#------------------------------------------------------------------------------
#   local cooling algorithm                                                
#------------------------------------------------------------------------------ 
def cool(f,a,delx, seed, xs, n, ncool):     
    random.seed(seed)
    nhit = 10
    delxp= 0.1*delx
    for k in range(ncool+1):
        for i in range(1,n):
            xpm = (xs[i]-xs[i-1])/a
            xpp = (xs[i+1]-xs[i])/a
            t = 1.0/4.0*(xpm**2+xpp**2)
            v = (xs[i]**2-f**2)**2
            sold = a*(t+v)
            for j in range(nhit):          
                xnew = xs[i] + delxp*(2.0*random.random()-1.0)
                xpm = (xnew-xs[i-1])/a
                xpp = (xs[i+1]-xnew)/a
                t = 1.0/4.0*(xpm**2+xpp**2)
                v = (xnew**2-f**2)**2
                snew = a*(t+v)
                if snew < sold :
                    xs[i]=xnew
    return

#------------------------------------------------------------------------------
#     sort array ra(n)                                                   
#------------------------------------------------------------------------------      
def sort(n, ra):
    l = n//2 + 1
    ir = n
    while True:
        if l > 1:
            l = l - 1
            rra = ra[l-1]
        else:
            rra = ra[ir-1]
            ra[ir-1] = ra[0]
            ir = ir - 1
            if ir == 1:
                ra[0] = rra
                return
        i = l
        j = l + l
        while j <= ir:
            if j < ir and ra[j-1] < ra[j]:
                j = j + 1
            if rra < ra[j-1]:
                ra[i-1] = ra[j-1]
                i = j
                j = j + j
            else:
                j = ir + 1
        ra[i-1] = rra
        
#------------------------------------------------------------------------------
#   initialize instanton configuration                               
#------------------------------------------------------------------------------
def setup(nin,z,tmax, seed):
    random.seed(seed)
    for i in range(nin):
        z[i] = random.random()*tmax
        sort(nin,z)
    return

#------------------------------------------------------------------------------
#     sum ansatz path                                                  
#------------------------------------------------------------------------------
def xsum(nin, z, f, t):
    neven = nin - nin % 2
    xsum = -f
    for i in range(1, neven, 2):
        xsum += f * np.tanh(2.0 * f * (t - z[i])) - f * np.tanh(2.0 * f * (t - z[i+1]))
    if nin % 2 != 0:
        xsum += f * np.tanh(2.0 * f * (t - z[nin])) + f   
    return xsum

#------------------------------------------------------------------------------
#   save array z in zstore                                             
#------------------------------------------------------------------------------
def store(nin,z,zstore):
    for i in range(nin):
         zstore[i] = z[i]
    return 

#------------------------------------------------------------------------------
#   restore array z from zstore                                        
#------------------------------------------------------------------------------
def restore(nin,z,zstore):
    for i in range(nin):
         zstore[i] = z[i]
    return
#------------------------------------------------------------------------------
#     discretized action for configuration x(n)                           
#------------------------------------------------------------------------------
def action(n,x,f,a):
    stot = 0.0
    ttot = 0.0
    vtot = 0.0  
    for j in range(n-1):
        xp = (x[j+1]-x[j])/a
        t  = 1.0/4.0*xp**2
        v  = (x[j]**2-f**2)**2
        s  = a*(t+v)
        ttot += a*t
        vtot += a*v
        stot += s  
    return stot,ttot,vtot

#------------------------------------------------------------------------------
#   sumansatz configuration on grid x(n)                                
#------------------------------------------------------------------------------
def xconf(n,x,nin,z,f,a):
    for j in range(1,n):  
         xx = a*j
         x[j] = xsum(nin,z,f,xx)        
    x[0] = x[n-1]
    x    = np.append(x, x[1])
    return

#------------------------------------------------------------------------------
#     hard core                                                           
#------------------------------------------------------------------------------
def sshort(z,nin,tcore,score,tmax):
    shc = 0.0
    tcore2 = tcore**2
    if tcore == 0 and tcore2 == 0:
        return shc
    for i in range(1, nin+1):
        if i == 1:
            zm = z[nin-1] - tmax
        else:
            zm = z[i-2]
        dz = z[i-1] - zm
        shc = shc + score * np.exp(-dz/tcore)
    return shc