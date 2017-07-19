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
    getHostName = str(subprocess.check_output('hostnamectl', shell=True))
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
    getDevs = str(subprocess.check_output('lsusb',shell=True))
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
    memFile = open('/proc/meminfo')
    fileData = memFile.readlines()


    #for loop limits memInfoList to first 3 metrics but this can be changed
    for i in range(0,3):
        metricRE = r".*:"
        valueRE = r":.*\n"
        metric = str(re.findall(metricRE, fileData[i]))
        #print metric
        value = str(re.findall(valueRE, fileData[i]))
        #print value
        memInfoList.update({metric[0].replace(":","").replace(" ",""):value[0].replace(":","").replace(" ","").replace("\n","")})

    return memInfoList

def getCPUInfo():
    #get CPU info from node
    getInfo = str(subprocess.check_output('cat /proc/cpuinfo', shell=True))

    coreRE = r"cpu cores\s*:.*"
    vendorRE = r"vendor_id\s*:.*"
    modelRE = r"model name\s*:.*"

    vendorInfo = str(re.search(vendorRE,getInfo).group(0))
    cpuInfo = str(re.search(coreRE,getInfo).group(0))
    modelInfo = str(re.search(modelRE,getInfo).group(0))

    cpuCores = re.sub(r"cpu cores\s*:\s*", "", cpuInfo)
    vendorId = re.sub(r"vendor_id\s*:\s*", "", vendorInfo)
    modelName = re.sub(r"model name\s*:\s*", "", modelInfo)

    cpuInfo = {"CPUCores":cpuCores,"VendorID":vendorId,"ModelName":modelName}

    return cpuInfo

def getDiskInfo():
    #get information about disks on node
    getInfo = str(subprocess.check_output('~/waggleWebAPI/detectDiskDevices.sh', shell=True))

    pattern = r".*memory card not recognized.*"
    if (re.search(pattern, getInfo)):
        currDiskName = "test"
        otherDiskName = "test"
        currDiskType = "test"
        otherDiskType = "test"
        currentDiskUsed = "test"
        currentDiskFree = "test"
        currentDiskUsage = "test"
    else:
        currDev = str(re.findall(r"CURRENT_DISK_DEVICE_NAME=.*",getInfo))
        otherDev = str(re.findall(r"OTHER_DISK_DEVICE_NAME=.*",getInfo))
        currType = str(re.findall(r"CURRENT_DISK_DEVICE_TYPE=.*",getInfo))
        otherType = str(re.findall(r"OTHER_DISK_DEVICE_TYPE=.*",getInfo))

        currDiskName = currDev[0].replace("CURRENT_DISK_DEVICE_NAME=","")
        otherDiskName = otherDev[0].replace("OTHER_DISK_DEVICE_NAME=","")
        currDiskType = currType[0].replace("CURRENT_DISK_DEVICE_TYPE=","")
        otherDiskType = otherType[0].replace("OTHER_DISK_DEVICE_TYPE=","")

        currentDiskUsed = "to be implemented"
        currentDiskFree = "to be implemented"
        currentDiskUsage = "to be implemented"

    #diskInfo = {"CurrDiskName":currDiskName,"OtherDiskName":otherDiskName,"CurrDiskType":currDiskType,"OtherDiskType":otherDiskType}
    diskInfo = {"CurrentDiskName":currDiskName,"OtherDiskName":otherDiskName,"CurrentDiskType":currDiskType,"OtherDiskType":otherDiskType,"CurrentDiskUsed":currentDiskUsed,"CurrentDiskFree":currentDiskFree,"CurrentDiskUsage":currentDiskUsage}
    return diskInfo

def getRunningServices():
    #get running services on node and get their uptimes
    statusList = []
    services = {}

    getInfo = str(subprocess.check_output('systemctl|grep running',shell=True))
    
    getServices = r".*\.service"

    #All running services
    runningServices = str(re.findall(getServices,getInfo))

    #Get current time in UTC
    currTime = pytz.utc.localize(datetime.datetime.utcnow().replace(microsecond=0))

    #find uptime for each running service
    for i in runningServices:
        getStatus = "systemctl status " + i
        active = r"\s*Active:\s*.*"
        time = r"since\s.*;"
        
        #retreive the status of each service
        status = str(subprocess.check_output(getStatus,shell=True))
        statusList.append(status)
        
        #parse out the line containing "Active: " and parse out the start time of the service
        findActive = str(re.findall(active,status))
        findTime = str(re.findall(time,findActive[0]))
        
        if findTime:
            #Format the service start time and put it in UTC
            ufStartTime = parse(findTime[0].replace("since ","").replace(";",""))
            startTime = ufStartTime.astimezone(pytz.timezone("UTC"))
            
            #Subtract the two values to get the run time of the process
            uptime = str(currTime - startTime)
            services.update({i:uptime})
        else:
            services.update({"Error":"error in getRunningServices()"})

    return services

def getSystemdServices(): #to be deprecated
    getInfo = str(subprocess.check_output('systemctl|grep running',shell=True))

    getSystemdServices = r"systemd-.*\.service"

    #All running services with systemd as the first word
    systemdServices = str(re.findall(getSystemdServices,getInfo))

    return systemdServices

def getNodeID():
    #get the node ID (name)
    hostInfo = str(subprocess.check_output('hostnamectl', shell=True))
    pattern = r"Static\s+hostname:.+\n"
    hostName = str(re.findall(pattern,hostInfo))

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
    print "getGeneralInfo():"+"\n"+str(getGeneralInfo())+"\n"
    print "getNodeUptime():"+"\n"+str(getNodeUptime())+"\n"
    print "getUSBDevs():"+"\n"+str(getUSBDevs())+"\n"
    print "getMemInfo():"+"\n"+str(getMemInfo())+"\n"
    print "getCPUInfo():"+"\n"+str(getCPUInfo())+"\n"
    print "getDiskInfo():"+"\n"+str(getDiskInfo())+"\n"
    print "getRunningServices():"+"\n"+str(getRunningServices())+"\n"
    #print "getSystemdServices():","\n",getSystemdServices(),"\n"
    print "getNodeID():"+"\n"+str(getNodeID())+"\n"
    #print "sendMetrics():","\n",sendMetrics(),"\n"