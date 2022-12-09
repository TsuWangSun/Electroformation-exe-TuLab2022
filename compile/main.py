#import pyvisa
#import numpy as np
import time
from fgcontrol import *

# connect device
if not getDevices():
    input("insert device and start again...")
    raise SystemExit
elif len(getDevices())/2 ==1:
    fgen2=selectDevice(getDevices()[1][0])
    print('using '+fgen2.query('*IDN?').strip()+"\n")
else:
    print(getDevices())
    sel=input("\ntype 0 to exit\nselect device manually (eg. 'ASRL4::INSTR'): ")
    if sel==0:
        raise SystemExit
    fgen2=selectDevice(sel)
    print('using '+fgen2.query('*IDN?').strip())

#time.sleep(1)
resett(fgen2)
#funinit(fgen2)
#fgen2.close()

# read parameters in config file
kk=['freqI', 'freqF', 'ampI', 'ampF', 'duration']
pars=[dict(zip(kk,p)) for p in getParameters()]


startT=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
startD=time.strftime("%Y-%m-%d", time.localtime())
start_time = time.time()

#genfunTime(fgen2,pars[0],init=True)
for i in range(len(pars)):
    if i==0:
        init=True
    else:
        init=False
    genfunTime(fgen2,pars[i],init)


endT=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

print("start time:\t", startT)
print("end time:\t", endT)
print("duration:\t", secToclock(time.time() - start_time))

fgen2.write("OUTPut OFF")

with open("config.txt") as f:
    fileoutput = f.readlines()
with open("FGlog-"+startD+".txt", "a+") as f1:
    f1.write("Function Generator task "+startD+"\n")
    f1.write('using '+fgen2.query('*IDN?').strip()+"\n\n")
    for line in fileoutput:
        f1.write(line)
        f1.flush()
    f1.write("start time:\t"+startT+"\n")
    f1.write("end time:\t"+endT+"\n")
    f1.write("duration:\t"+secToclock(time.time() - start_time)+"\n\n")
#genfunTimeMT(fgen2,getParameters()[1])


print("\nlog file created: "+"FGlog-"+startD+".txt\n")
wait = input("Press Enter to continue...")
print("You did a great job!")





