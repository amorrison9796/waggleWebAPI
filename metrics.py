from dateutil.parser import parse
from datetime import datetime

import subprocess
import datetime
import json
import time
import pytz
import re

def getGeneralInfo():
    #get general info about node using 'hostnamectl'
    getHostName = str(subprocess.check_output('hostnamectl', shell=True).decode('ascii'))
    pattern = r"\s*[a-zA-Z]*:\s*.\n|\s*[a-zA-Z]*\s*[a-zA-Z]*:\s*.*\n"
    info = re.findall(pattern,getHostName)

    genInfoList = {}

    for i in info:
        metricRE = r"\s*[a-zA-Z]*:|\s*[a-zA-Z]*\s*[a-zA-Z]*:"
        valueRE = r":\s*.*\n"
        metric = re.findall(metricRE, i)
        value = re.findall(valueRE, i)
        
        genInfoList.update({metric[0].replace(":","").replace(" ",""):value[0].replace(": ","").replace("\n","")})

    return genInfoList

def getNodeUptime():
    #get uptime of node
    nodeUptime = {}
    upTimeCmd = str(subprocess.check_output('cat /proc/uptime', shell=True))

    pattern = r"\d*\.\d*"
    uptime = re.findall(pattern,upTimeCmd)

    nodeUptime.update({"UptimeSeconds":uptime[0]})
    nodeUptime.update({"UptimeFormatted":str(datetime.timedelta(seconds=int(float(uptime[0]))))})

    return nodeUptime

def getUSBDevs():
    #get USB devices that are connected to node
    getDevs = str(subprocess.check_output('lsusb',shell=True).decode('ascii'))
    pattern = r"Bus\s*\d+\s*Device\s*\d+:\s*ID.+"
    info = re.findall(pattern,getDevs)
    devs = {}

    for i in range(0,len(info)):
        metricRE = r"Bus\s*\d+\s*Device\s*\d+:"
        valueRE = r"Bus\s*\d+\s*Device\s*\d+:.*"
        metric = "USBDev"+str(i)
        value = re.findall(valueRE, info[i])
        devs.update({metric:value[0].replace(": ","")})

    return devs

def getMemInfo():
    #get RAM info from node
    memInfoList = {}
        
    #get info from /proc/meminfo file
    getInfo = str(subprocess.check_output('cat /proc/meminfo', shell=True).decode('ascii'))

    memFile = open('/proc/meminfo')
    
    fileData = str(memFile.readlines())
    fileData = getInfo
    memFreeRE = r"MemFree:\s*.*\n"
    #memAvailableRE = r"MemAvailable:\s*.*\n"
    memTotalRE = r"MemTotal:\s*.*\n"
   
    memFreeInfo = re.findall(memFreeRE,getInfo)
    #memAvailableInfo = re.findall(memAvailableRE,getInfo)
    memTotalInfo = re.findall(memTotalRE,getInfo)

    memFreeInfo = re.findall(memFreeRE,fileData)
    #memAvailableInfo = re.findall(memAvailableRE,fileData)
    memTotalInfo = re.findall(memTotalRE,fileData)

    memFree = re.sub(r"MemFree:\s*","",memFreeInfo[0])
    #memAvailable = re.sub(r"MemAvailable:\s*","",memAvailableInfo[0])
    memTotal = re.sub(r"MemTotal:\s*","",memTotalInfo[0])
    memInfoList = {"MemFree":memFree,"MemTotal":memTotal}
        
    return memInfoList

def getCPUInfo():
    #get CPU info from node
    getInfo = str(subprocess.check_output('cat /proc/cpuinfo', shell=True).decode('ascii'))

    coreRE = r"cpu cores\s*:.*"
    vendorRE = r"vendor_id\s*:.*"
    modelRE = r"model name\s*:.*"
    
    if re.search(vendorRE,getInfo): #if statements to be removed (for testing purposes)
        vendorInfo = str(re.search(vendorRE,getInfo).group(0))
        cpuInfo = str(re.search(coreRE,getInfo).group(0))
        modelInfo = str(re.search(modelRE,getInfo).group(0))

        cpuCores = re.sub(r"cpu cores\s*:\s*", "", cpuInfo)
        vendorId = re.sub(r"vendor_id\s*:\s*", "", vendorInfo)
        modelName = re.sub(r"model name\s*:\s*", "", modelInfo)
        
        cpuInfo = {"CPUCores":cpuCores,"VendorID":vendorId,"ModelName":modelName}
        
    elif re.findall(r"Processor\s*:\s*.*",getInfo):
        procInfo = re.findall(r"Processor\s*:\s*.*",getInfo)

        procOne = procInfo[0]
        proc = re.sub(r".*:","",procOne)

        cpuInfo = {"Processor":str(proc)}

    return cpuInfo

def getDiskInfo():
    #get information about disks on node
    getDevices = str(subprocess.check_output('~/waggleWebAPI/detectDiskDevices.sh', shell=True).decode('ascii'))
    #getUsage = str(subprocess.check_output('df -k |grep sda2',shell=True).decode('ascii'))
    
    pattern = r".*memory card not recognized.*"
    if (re.search(pattern, getDevices)):
        currDiskName = "test"
        otherDiskName = "test"
        currDiskType = "test"
        otherDiskType = "test"
        currentDiskUsed = "test"
        currentDiskFree = "test"
        currentDiskUsage = "test"
    else:
        currDev = re.findall(r"CURRENT_DISK_DEVICE_NAME=.*",getDevices)
        otherDev = re.findall(r"OTHER_DISK_DEVICE_NAME=.*",getDevices)
        currType = re.findall(r"CURRENT_DISK_DEVICE_TYPE=.*",getDevices)
        otherType = re.findall(r"OTHER_DISK_DEVICE_TYPE=.*",getDevices)

        currDiskName = currDev[0].replace("CURRENT_DISK_DEVICE_NAME=","")
        otherDiskName = otherDev[0].replace("OTHER_DISK_DEVICE_NAME=","")
        currDiskType = currType[0].replace("CURRENT_DISK_DEVICE_TYPE=","")
        otherDiskType = otherType[0].replace("OTHER_DISK_DEVICE_TYPE=","")

        currentDiskUsed = "to be implemented"
        currentDiskFree = "to be implemented"
        currentDiskUsage = "to be implemented"

    diskInfo = {"CurrentDiskName":currDiskName,"OtherDiskName":otherDiskName,"CurrentDiskType":currDiskType,"OtherDiskType":otherDiskType,"CurrentDiskUsed":currentDiskUsed,"CurrentDiskFree":currentDiskFree,"CurrentDiskUsage":currentDiskUsage}
    return diskInfo

def getRunningServices():
    #get running services on node and get their uptimes
    statusList = []
    services = {}

    getInfo = str(subprocess.check_output("systemctl|grep '.service.*running'",shell=True).decode('ascii'))
    getServices = r".*[.]service"

    #All running services
    runningServices = re.findall(getServices,getInfo)

    #Get current time in UTC
    currTime = pytz.utc.localize(datetime.datetime.utcnow().replace(microsecond=0))

    #find uptime for each running service
    for i in runningServices:
        getStatus = "systemctl status " + str(i)
        active = r"\s*Active:\s*.*"
        time = r"since\s*[a-zA-Z]*\s*[0-9]*-[0-9]*-[0-9]*\s*[0-9]*:[0-9]*:[0-9]*\s*[a-zA-Z]*;"
        
        #retreive the status of each service
        status = str(subprocess.check_output(getStatus,shell=True))
                
        #parse out the line containing "Active: " and parse out the start time of the service
        findActive = re.findall(active,status)
        
        findTime = re.findall(time,findActive[0])
        
        #Format the service start time and put it in UTC
        ufStartTime = parse(findTime[0].replace("since ","").replace(";",""))
        startTime = ufStartTime.astimezone(pytz.timezone("UTC"))
           
        #Subtract the two values to get the run time of the process
        uptime = str(currTime - startTime)
        services.update({i:uptime})
  
    return services

def getSystemdServices(): #to be deprecated
    getInfo = str(subprocess.check_output('systemctl|grep running',shell=True))

    getSystemdServices = r"systemd-.*\.service"

    #All running services with systemd as the first word
    systemdServices = str(re.findall(getSystemdServices,getInfo))

    return systemdServices

def getNodeID():
    #get the node ID (name)
    hostInfo = str(subprocess.check_output('hostnamectl', shell=True).decode('ascii'))
    pattern = r"Static\s+hostname:.+\n"
    hostName = re.findall(pattern,hostInfo)

    ID = hostName[0].replace("Static hostname: ","").replace("\n","")

    nodeID = {"NodeID":ID}

    return nodeID

def sendMetrics():
    #function that sends data to sendData.py via response/request
    nodeID = getNodeID()
    uptime = getNodeUpTime()[0]
    
    jsonData = {}
    jsonData = {'timestamp':float(time.time()),'nodename':nodeID,'uptime':uptime} #time format can be changed if needed

    #print json.dumps(jsonData)
    return json.dumps(jsonData)

if __name__ == "__main__":
    print ("getGeneralInfo():"+"\n"+str(getGeneralInfo())+"\n")
    print ("getNodeUptime():"+"\n"+str(getNodeUptime())+"\n")
    print ("getUSBDevs():"+"\n"+str(getUSBDevs())+"\n")
    print ("getMemInfo():"+"\n"+str(getMemInfo())+"\n")
    print ("getCPUInfo():"+"\n"+str(getCPUInfo())+"\n")
    print ("getDiskInfo():"+"\n"+str(getDiskInfo())+"\n")
    print ("getRunningServices():"+"\n"+str(getRunningServices())+"\n")
    #print ("getSystemdServices():","\n",getSystemdServices(),"\n")
    print ("getNodeID():"+"\n"+str(getNodeID())+"\n")
    #print ("sendMetrics():","\n",sendMetrics(),"\n")

