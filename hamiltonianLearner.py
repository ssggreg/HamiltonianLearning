from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import scipy
from scipy.misc import derivative
import operator as op

def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

def numberOfMonomials(degree,numberOfVariables):
    return ncr(degree+numberOfVariables-1,degree)

def triangularNumber(degree):
    if degree==0:
        return 1
    else:
        return triangularNumber(degree-1)+(degree+1)

def partial_derivative(func, var=0, point=[]):
    args = point[:]
    def wraps(x):
        args[var] = x
        return func(*args)
    return derivative(wraps, point[var], dx = 1e-6)

def MyPolyHamiltonian(d,monomialCoeff,phaseCoord):
    poly= PolynomialFeatures(degree=d)
    monomials=poly.fit_transform(phaseCoord)
    #print(monomials)
    neededLength=triangularNumber(d)
    gap=neededLength-len(monomialCoeff)
    if gap>0:
        #print('padding')
        monomialCoeff=np.pad(monomialCoeff,(0,gap),'constant')
        #print(monomialCoeff)
    elif gap<0:
        #print('cutting')
        monomialCoeff=monomialCoeff[0:neededLength]
        #print(monomialCoeff)
    else:
        #print('ok')
        #print(monomialCoeff)
        pass
    result=np.dot(monomials,monomialCoeff)
    #print(result)
    return result

#def MyExpHamiltonian(d,monomialCoeff,phaseCoord):
    # Make Laurent polynomial in e^x and e^p variables from degrees -d to d

#def MyTrigHamiltonian(d,monomialCoeff,phaseCoord):
    # Make Laurent polynomial in e^ix and e^ip variables from degrees -d to d to get the various trig functions

#def MyTotalHamiltonian(degreeParams,monomialParams,phaseCoord):
    #let the first two arguments be lists of 3 separate versions to handle a sum of poly,exp,trig terms

def getdHdx(degree,monomialCoeff,phaseCoord):
    dHdx=partial_derivative(lambda a,b: MyPolyHamiltonian(3,monomialCoeff,[[a,b]]),0,phaseCoord)
    #print(dHdx)
    return dHdx

def getdHdp(degree,monomialCoeff,phaseCoord):
    dHdp=partial_derivative(lambda a,b: MyPolyHamiltonian(3,monomialCoeff,[[a,b]]),1,phaseCoord)
    #print(dHdp)
    return dHdp

def lossFunction(inputdata,degree,monomialCoeff):
    loss = 0
    for i in np.arange(len(inputdata)-1):
        qnow = inputdata[i,0]
        qlater = inputdata[i+1,0]
        pnow = inputdata[i,1]
        plater = inputdata[i+1,1]
        tnow = inputdata[i,2]
        tlater = inputdata[i+1,2]
        deltat = tlater - tnow
        if (deltat>0):
            qdot = (qlater - qnow)/deltat
            pdot = (plater - pnow)/deltat
            loss = loss + (qdot - getdHdp(degree,monomialCoeff,[qnow,pnow]))**2
            loss = loss + (pdot + getdHdx(degree,monomialCoeff,[qnow,pnow]))**2
    # add an L1 regularization that makes as few nonzero terms as possible
	return loss


MyPolyHamiltonian(3,np.arange(20),[[0,0],[1,1],[2,3],[5,7]])
res=getdHdp(2,[0,0,5,0,3,0],[2,2])
print(res)

degree = 2

testdata = np.load("harmonicOscillatorTraj.npy")
toOptimize = lambda monomialCoeff: lossFunction(testdata,degree,monomialCoeff)

fittedParam=scipy.optimize.minimize(toOptimize,[0,0,0,1,2.25,0])

print(fittedParam)