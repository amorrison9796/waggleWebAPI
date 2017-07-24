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
    mountedDevs = []
    #get information about disks on node
    getDevices = str(subprocess.check_output('~/waggleWebAPI/detectDiskDevices.sh', shell=True).decode('ascii'))
    pattern = r".*memory card not recognized.*"
    if (re.search(pattern, getDevices)):
        currDiskName = "test"
        otherDiskName = "test"
        currDiskType = "test"
        otherDiskType = "test"
        currentDiskUsed = "test"
        currentDiskFree = "test"
        currentDiskUsage = "test"
        diskInfo = {"CurrentDiskName":currDiskName,"OtherDiskName":otherDiskName,"CurrentDiskType":currDiskType,"OtherDiskType":otherDiskType,"CurrentDiskUsed":str(currentDiskUsed),"CurrentDiskFree":str(currentDiskFree),"CurrentDiskUsage":str(currentDiskUsage)}
        
    else:
        currDev = re.findall(r"CURRENT_DISK_DEVICE_NAME=.*",getDevices)
        otherDev = re.findall(r"OTHER_DISK_DEVICE_NAME=.*",getDevices)
        currType = re.findall(r"CURRENT_DISK_DEVICE_TYPE=.*",getDevices)
        otherType = re.findall(r"OTHER_DISK_DEVICE_TYPE=.*",getDevices)
##      print(currDev,otherDev,currType,otherType)
        currDiskName = currDev[0].replace("CURRENT_DISK_DEVICE_NAME=","")
        otherDiskName = otherDev[0].replace("OTHER_DISK_DEVICE_NAME=","")
        currDiskType = currType[0].replace("CURRENT_DISK_DEVICE_TYPE=","")
        otherDiskType = otherType[0].replace("OTHER_DISK_DEVICE_TYPE=","")

        devs = str(subprocess.check_output("mount | grep 'on /' |cut -f 1 -d ' ' | grep -o '/dev/mmcblk[0-1]p[0-2]'",shell=True).decode('ascii'))
        mountedDevs = re.findall(r"/dev/mmcblk[0-1]p[0-2]",devs)
##        if (len(mountedDevs) > 1):
##            part1 = "df -k | grep " + mountedDevs[0] + " | awk '{print $2}'"
##            part2 = "df -k | grep " + mountedDevs[1] + " | awk '{print $2}'"
##            part1Size = str(subprocess.check_output(part1,shell=True).decode('ascii'))
##            part2Size = str(subprocess.check_output(part2,shell=True).decode('ascii'))
##
##            if part1Size == "" or part1Size == " ":
##                part1Size = int("0")
##            if part2Size == "" or part2Size == " ":
##                part2Size = int("0")
##
##            if int(part1Size) > int(part2Size):
##                currPart = mountedDevs[0]
##            else:
##                currPart = mountedDevs[1]
##        else:
        currPart = mountedDevs[0]
            
        #getUsage = str(subprocess.check_output("df -k|grep /dev/mmcblk",shell=True).decode('ascii'))
##      print("currPart"),print(currPart),print("mountedDevs"),print(mountedDevs)
        diskInfoStr = "df -k |grep " + currPart #need to change this eventually - can't guarantee that the p2 partition will be the primary partition
        getUsage = str(subprocess.check_output(diskInfoStr,shell=True).decode('ascii'))
##      print ("getUsage:"), print(getUsage)
    
        used = str(subprocess.check_output("df -k | grep " + currPart + " | awk '{print $3}'",shell=True).decode('ascii'))
        total = str(subprocess.check_output("df -k | grep " + currPart + " | awk '{print $2}'",shell=True).decode('ascii'))
        available = str(subprocess.check_output("df -k | grep " + currPart + " | awk '{print $4}'",shell=True).decode('ascii'))
        usage = str(subprocess.check_output("df -k | grep " + currPart + "| awk '{print $5}'",shell=True).decode('ascii'))
#       print("used: "),print(used), print("total: "),print(total),print("available: "), print(available),print("usage: "),print(usage)

        used = used.replace("\n","")
        available = available.replace("\n","")
        currentDiskUsed = (float(used) * float(1024)) * float(10**-9)
        currentDiskFree = (float(available) * float(1024)) * float(10**-9)
        currentDiskUsage = usage
        diskInfo = {"CurrentDiskName":currDiskName,"OtherDiskName":otherDiskName,"CurrentDiskType":currDiskType,"OtherDiskType":otherDiskType,"CurrentDiskUsed":str(currentDiskUsed)+"GB","CurrentDiskFree":str(currentDiskFree)+"GB","CurrentDiskUsage":str(currentDiskUsage)}

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

