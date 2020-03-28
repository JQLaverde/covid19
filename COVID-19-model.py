#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 18:59:14 2020

@author: jcorrea
"""

import   numpy  as  np
import  matplotlib.pyplot as  plt
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from scipy.optimize import minimize,curve_fit,leastsq


population={'australia':8858775, 'algeria':42228429, 'italy':60359546, 
            'austria':8858775, 'belgium':11455519, 
            'brazil':210147125, 'canada':36994000, 'china':1395380000, 
            'france':67012883, 'spain':45692492, 
            'denmark':5806081, 'germany':83019213, 'greece':10724599,
            'Hong-kong':7486000, 'indonesia':264162000, 
            'iran':82360000, 'iraq':38433600, 'ireland':4904240, 'us':327352000, 
            'uk':66647112, 'malaysia':32385000, 
            'netherlands':17282163, 'norway':5328212, 'philipphines':106651922,
            'poland':37972812, 'portugal':10276617, 'sweden':10230185, 
            'south-korea':51635000, 'switzerland':8544527}

    
def readDataCountry(nameCountry):
    ''' Specify the name of the country in lowercase
        return Total, Activos , ndays 
	! Las variables son locales, se ejecuta con la funcion antenrior 
    '''
    data = pd.read_excel('../data/covid19-Database.xls',sheet_name=nameCountry)
    Activos = np.array(data['Currently Infected'])
    Totales = np.array(data['Cases'])
    Ai=np.nonzero(Activos==0)
    Totales =np.delete(Totales,Ai)
    Activos=np.delete(Activos,Ai)
    ndays = len(Activos)
    return Activos, Totales, ndays


def  model(ndays,N, Ni,bt,gmm):
    h=1E-3
    npt=int(ndays/h)
    R=np.zeros(npt,np.double)
    I=np.zeros(npt,np.double)
    S=np.zeros(npt,np.double)
    I[0] = Ni/N
    S[0]=(N-Ni)/N
    R[0]=0
    IR=[]
    SR=[]
    RR=[]
    IR.append(I[0])
    SR.append(S[0])
    RR.append(R[0])
    ct=0
    cd=1
    for i  in  range(0,npt-1):
        S[i+1]=-h*bt*S[i]*I[i]+S[i]
        I[i+1]= h*bt*S[i]*I[i]+(1-h*gmm)*I[i]
        R[i+1]= h*gmm*I[i]+R[i]
        ct+=1
        if ct==1000 and cd<ndays:
            IR.append(I[i])
            SR.append(S[i])
            RR.append(R[i])
            ct=0
            cd+=1

    return np.array(IR),np.array(SR),np.array(RR)


def  model2(ndays,N, Ni,bt,gmm,pp):
    h=1E-3
    npt=int(ndays/h)
    R=np.zeros(npt,np.double)
    I=np.zeros(npt,np.double)
    S=np.zeros(npt,np.double)
    I[0] = Ni/N
    S[0]=(N-Ni)/N
    R[0]=0
    IR=[]
    SR=[]
    RR=[]
    IR.append(I[0])
    SR.append(S[0])
    RR.append(R[0])
    ct=0
    cd=1
    for i  in  range(0,npt-1):
        S[i+1]=-h*bt*S[i]*I[i]-pp*S[i]+S[i]
        I[i+1]= h*bt*(1-pp)*S[i]*I[i]+(1-h*gmm)*I[i]
        R[i+1]= h*gmm*I[i]+R[i]
        ct+=1
        if ct==1000 and cd<ndays:
            IR.append(I[i])
            SR.append(S[i])
            RR.append(R[i])
            ct=0
            cd+=1

    return np.array(IR),np.array(SR),np.array(RR)

def  model3(ndays,N, Ni,bt,gmm,pp):
    h=1E-3
    npt=int(ndays/h)
    R=np.zeros(npt,np.double)
    I=np.zeros(npt,np.double)
    S=np.zeros(npt,np.double)
    I[0] = Ni/N
    S[0]=(N-Ni)/N
    R[0]=0
    IR=[]
    SR=[]
    RR=[]
    IR.append(I[0])
    SR.append(S[0])
    RR.append(R[0])
    ct=0
    cd=1
    for i  in  range(0,npt-1):
        S[i+1]=-h*bt*S[i]*I[i]-pp*S[i]+S[i]
        I[i+1]= h*bt*S[i]*I[i]+(1-h*gmm)*I[i] + (1-pp)*S[i]
        R[i+1]= h*gmm*I[i]+R[i]
        ct+=1
        if ct==1000 and cd<ndays:
            IR.append(I[i])
            SR.append(S[i])
            RR.append(R[i])
            ct=0
            cd+=1

    return np.array(IR),np.array(SR),np.array(RR)



def fun(x,p1,p2):
   global ndays,N,Ni
   I,S,R = model(ndays,N,Ni,p1,p2)
   return np.concatenate((I*N,N*(I-R)))

def fun2(x,p1,p2,p3):
   global ndays,N,Ni
   I,S,R = model2(ndays,N,Ni,p1,p2,p3)
   return np.concatenate((I*N,N*(I-R)))

def fun3(x,p1,p2,p3):
   global ndays,N,Ni
   I,S,R = model3(ndays,N,Ni,p1,p2,p3)
   return np.concatenate((I*N,N*(I-R)))



def   fit_country(ctr,md):
    global ndays,N,Ni,Total, Actv
    data =  np.concatenate((Total, Actv))
    xdata = np.concatenate((np.arange(1,ndays+1,1),np.arange(1,ndays+1,1)))
    if  md ==1:
        res, res2 = curve_fit(fun,xdata,data,p0=[0.1,0.3],bounds=(0.,1.))
    if  md ==2:
        res, res2 = curve_fit(fun2,xdata,data,p0=[0.1,0.3,0.1],bounds=(0.,1.))  
    if  md ==3:
        res, res2 = curve_fit(fun3,xdata,data,p0=[0.1,0.3,0.1],bounds=(0.,1.)) 
    return res

ctr='italy'  
md =2
N=population[ctr]
Actv,Total,ndays=readDataCountry(ctr)
Ni=Actv[0]
res = fit_country(ctr,md)
print(res)
if md ==1:
    I,S,R = model(ndays,N,Ni,res[0],res[1])
if md ==2:
    I,S,R = model2(ndays,N,Ni,res[0],res[1],res[2])
if md ==3:
    I,S,R = model3(ndays,N,Ni,res[0],res[1],res[2])
plt.xlabel("Day")
plt.ylabel("Total Cases /Poblation")
plt.plot(N*I)
plt.plot(np.resize(Total,ndays),"*")
plt.show()
plt.plot(N*(I-R))
plt.plot(np.resize(Actv,ndays),"*")
plt.show()
print("Parameters",res)
print("Total  infectados:",N*I[-1])
print("Total  activos:",N*(I[-1]-R[-1]))

#for  ctr in  population:
#    N=population[ctr]
#    Actv,Total,ndays=readDataCountry(ctr)
#    Ni=Actv[0]
#    data =  np.concatenate((Total, Actv))
#    xdata = np.concatenate((np.arange(1,ncut+1,1),np.arange(1,ncut+1,1)))
#    res, res2 = curve_fit(fun,xdata,data,p0=[0.1,0.3],bounds=(0.,1.))
#    print(ctr+";"+str(res[0])+";"+str(res[1]))

#res, res2 = curve_fit(fun2,xdata,data,p0=[0.1,0.3,0.005],bounds=(0.,1.))
#I,S,R = model2(ndays,N,Ni,res[0],res[1],res[2])
    


