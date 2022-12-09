import pyvisa
import numpy as np
import time
import os

# scan and list devices
def getDevices():
    rm = pyvisa.ResourceManager()
    
    if len(rm.list_resources())==0:
        return
    
    resources=[]
    devices=[]
    for i in rm.list_resources():
        resources.append(i)
        devices.append(rm.open_resource(i).query('*IDN?').strip())
        
    return [devices, resources]

# select function generator
def selectDevice(resource='ASRL4::INSTR'):
    return pyvisa.ResourceManager().open_resource(resource) 


def createConfig():
    with open('config.txt', 'w+') as f:
        f.write('# config file for FG\n\nFREQ(Hz)\tAMPL(Vpp)\tTime (hh:mm:ss)\tFunction\n1000\t\t0.5-2.5\t00:01:00\t\tSIN\n1000\t\t2.5 \t\t03:00:00\t\tSIN\n1000-2\t2.5 \t\t00:01:00\t\tSIN\n2\t\t2.5 \t\t00:00:30\t\tSIN\n\n')



# get parameters from config.txt
def getParameters(configLocation='config.txt'):
    if not os.path.exists(configLocation):
        print(configLocation+" not found, create one...")
        createConfig()
        
    configList=[]
    with open(configLocation,'r') as fp:
        for line in fp:
            if line[0].isdigit():
                configList.append(line)
    
    parList = [item.split() for item in configList]
    
    for i in range(len(parList)):
        Ttemp=parList[i][2].split(':')
        parList[i][2]=int(Ttemp[0])*3600+\
        int(Ttemp[1])*60+\
        int(Ttemp[2])
        
        parList[i].insert(1,parList[i][0])
        parList[i].insert(3,parList[i][2])
        if '-' in parList[i][0]:
            freqR=parList[i][0].split('-')
            parList[i][0]=freqR[0]
            parList[i][1]=freqR[1]
        if '-' in parList[i][2]:
            vppR=parList[i][2].split('-')
            parList[i][2]=vppR[0]
            parList[i][3]=vppR[1]
    
    return parList


# reset and initiate device
def resett(fgen):
    fgen.write("OUTPut ON")
    fgen.write("OUTPut OFF")
    fgen.write("*RST")
    fgen.write("*CLS")

# report function status on screen
def funReport(fgen):
    fgen.query("SOUR1:APPL?")
    print(
    fgen.query("SOUR1:FUNC?")[0:3] + "\t" +
    str(round(float(fgen.query(f"SOUR1:FREQ?")),2)) + " \t\t" +
    str(round(float(fgen.query(f"SOUR1:AMPL?")),2)),
    end="\r"
    )


# initiate function generator
def funinit(fgen):
    resett(fgen)
    fgen.write("SOUR1:FUNC SIN")
    fgen.write("SOUR1:FREQ 0.1")
    fgen.write("SOUR1:AMPL 0")
    fgen.write("SOUR1:DCO 0")
    funReport(fgen)
    print("init")

# format time
def secToclock(tf): # secs
    tf=int(tf)
    mins, secs = divmod(tf, 60)
    hrs, mins = divmod(mins, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hrs, mins, secs)

# report function status on screen with time remains
def funReportT(fgen,t):
    fgen.query("SOUR1:APPL?")
    print(
    fgen.query("SOUR1:FUNC?")[0:3] + "\t" +
    str(round(float(fgen.query(f"SOUR1:FREQ?")),2)) + " \t\t" +
    str(round(float(fgen.query(f"SOUR1:AMPL?")),2)) + "\t\t",
    secToclock(t),
    end="\r"
    )
    
# generate programmed function by parameters
def genfunTime(fgen, p, init=False):
    """duration: min"""
    tsteps=p['duration']
    tf=np.linspace(tsteps, 1, tsteps)
    freqs=np.linspace(float(p['freqI']), float(p['freqF']), tsteps)
    amps=np.linspace(float(p['ampI']), float(p['ampF']), tsteps)
    
    print("FUN\tFREQ(Hz)\tAMPL(Vpp)\t")
    if init:
        funinit(fgen)
        fgen.write("OUTPut ON")
    
    print("start \t"+str(p['freqI'])+" \t\t"+str(p['ampI']), "\t\t",secToclock(tsteps))
    for f, a, t in zip(freqs,amps, tf):
        fgen.write("SOUR1:FREQ " + str(f))
        fgen.write("SOUR1:AMPL " + str(a))
        funReportT(fgen,t)
        time.sleep(1)
    print("\n")
