from flask import Flask, render_template, Response
from dateutil.parser import parse
from datetime import datetime

import subprocess
import datetime
import json
import time
import pytz
import re

app = Flask(__name__,static_url_path='',template_folder="templates")

@app.route("/")
def home():
    #basic home page - does not need a get function
    return render_template('home.html')

@app.route("/generalInfo")
def generalInfo():
    #pass general info to html template
    genInfo = getGeneralInfo()
    nodeUpTime = getNodeUpTime()
    usbDevs = getUSBDevs()
	
    return render_template('genInfo.html',genInfo=genInfo,upTimeSecs=nodeUpTime[0],upTimeFormat=nodeUpTime[1],usbDevs=usbDevs)

def getGeneralInfo():
    #get general info about machine using 'hostnamectl'
    getHostName = subprocess.check_output('hostnamectl', shell=True)
    findPattern = r"\s*[a-zA-Z]*:\s*.\n|\s*[a-zA-Z]*\s*[a-zA-Z]*:\s*.*\n"

    genInfoList = re.findall(findPattern,getHostName)
    return genInfoList

def getNodeUpTime():
    #get up time of the current node
    nodeUpTime = []
    upTimeCmd = subprocess.check_output('cat /proc/uptime', shell=True)

    pattern = r"\d*\.\d*"
    upTime = re.findall(pattern,upTimeCmd)

    nodeUpTime.insert(0,str(upTime[0]))
    nodeUpTime.insert(1,str(datetime.timedelta(seconds=int(float(upTime[0])))))

    return nodeUpTime

def getUSBDevs():
    #retrieve the USB devices that are connected to the system
    getDevs = subprocess.check_output('lsusb',shell=True)
    pattern = r"Bus\s*\d+\s*Device\s*\d+:\s*ID.+"

    devs = re.findall(pattern,getDevs)

    return devs

#REMOVE THIS EVENTUALLY BUT LEAVE IT IN FOR NOW FOR ZACH
@app.route("/nodeApi")
def sendGenInfo():
    #test function that sends general computer info to Zach's API
    getInfo = getGeneralInfo()
    with open('/home/adammorr/waggleWebAPI/testFiles/genFakeData/jsonFile.json') as data:
        jsonData = json.load(data)
    return Response(json.dumps(jsonData), mimetype='application/json')

@app.route("/memInfo")
def memInfo():
    #pass memory and CPU info to html template
    memoryInfo = getMemInfo()
    cpuInfo = getCPUInfo()
    diskInfo = getDiskInfo()
    
    return render_template('memInfo.html', memoryInfo=memoryInfo, cpuInfo=cpuInfo,diskInfo=diskInfo)

def getMemInfo():

    memInfoList = []
        
    #get info from /proc/meminfo file
    memFile = open('/proc/meminfo')
    fileData = memFile.readlines()

    #for each line in memInfo, find the given information that fits the regular expression
    for x in range(len(fileData)):
    	findPattern = r"[a-zA-Z0-9]+\([a-zA-Z0-9]+\):\s*[0-9]|[a-zA-Z0-9]+:\s*[0-9]"
    	if re.search(findPattern, fileData[x]): #replace re.search() with re.findall()?
	    memInfoList.append(fileData[x])
   	else:
    	    memInfoList.append(None)
    return memInfoList
	
def getCPUInfo():
    #get info from /proc/cpuinfo file
    cpuFile = open('/proc/cpuinfo')
    cpuInfoList = [line.split('\n') for line in cpuFile.readlines()]

    return cpuInfoList
def getDiskInfo():
    name = ""
    typeOf = ""
    used = ""
    free = ""

    getInfo = subprocess.check_output('~/waggleWebAPI/detectDiskDevices.sh', shell=True)

    print getInfo

    pattern = r".*memory card not recognized.*"
    if (re.search(pattern, getInfo)):
        name = ["test","test2"]
        typeOf = ["test","test2"]
        used = ["test","test2"]
        free = ["test","test2"]
    else:
        currDev = re.findall(r"CURRENT_DISK_DEVICE_NAME=.*",getInfo)
        otherDev = re.findall(r"OTHER_DISK_DEVICE_NAME=.*",getInfo)

        currType = re.findall(r"CURRENT_DISK_DEVICE_TYPE=.*",getInfo)
        otherType = re.findall(r"OTHER_DISK_DEVICE_TYPE=.*",getInfo)
        
        name = [currDev[0].replace("CURRENT_DISK_DEVICE_NAME=","Name:"),otherDev[0].replace("OTHER_DISK_DEVICE_NAME=","Name:")]
        typeOf = [currType[0].replace("CURRENT_DISK_DEVICE_TYPE=","Type:"),otherType[0].replace("OTHER_DISK_DEVICE_TYPE=","Type:")]
        used = ["Used: 17%","Used: 17%"]
        free = ["Free: 83%","Free: 83%"]

    diskInfo = [name,typeOf,used,free]
    #print diskInfo
    
    return diskInfo
 
@app.route("/services")
def services():
    #pass running services, systemd services, and up time info to html template
    runningServList = getRunningServices()
    systemdServList = getSystemdServices()

    upTime = getUpTime(systemdServList)

    return render_template('services.html', runningServList=runningServList, systemdServList=systemdServList, upTime=upTime)

def getRunningServices():
    getInfo = subprocess.check_output('systemctl|grep running',shell=True)

    getServices = r".*\.service"

    #All running services
    runningServices = re.findall(getServices,getInfo)

    return runningServices

def getSystemdServices():
    getInfo = subprocess.check_output('systemctl|grep running',shell=True)

    getSystemdServices = r"systemd-.*\.service"

    #All running services with systemd as the first word
    systemdServices = re.findall(getSystemdServices,getInfo)

    return systemdServices

def getUpTime(systemdServList):
    statusList = []
    startTimeList = []
    upTime = []
	
    #retreive the status of each systemd service
    for i in systemdServList:
    	command = "systemctl status " + i
    	status = subprocess.check_output(command,shell=True)
    	statusList.append(status)

    #parse out the line containing "Active: " and parse out the start time of the service
    for j in statusList:
    	active = r"\s*Active:\s*.*"
    	time = r"since\s.*;"

    	findActive = re.findall(active,j)
    	findTime = re.findall(time,findActive[0])
    	#print(findActive)
    	#print(findTime)
    	if findTime:
            startTimeList.append(findTime[0].replace("since ","").replace(";",""))
    	else:
            startTimeList.append(None)

    #Calculate the elapsed time since the service started
    for k in startTimeList:
    	if k:
            #Get current time in UTC
            currTime = pytz.utc.localize(datetime.datetime.utcnow().replace(microsecond=0))

            #Format the service start time and put it in UTC
            ufStartTime = parse(k)
            startTime = ufStartTime.astimezone(pytz.timezone("UTC"))

            #Subtract the two values to get the run time of the process
            upTime.append(currTime - startTime)
        else:
            upTime.append(None)
    return upTime

@app.route("/metrics")
def sendMetrics():
    #function that sends data to sendData.py via response/request
    nodeID = getNodeID()
    uptime = getNodeUpTime()[0]
        
    jsonData = {}
    jsonData = {'timestamp':float(time.time()),'nodename':nodeID,'uptime':uptime} #time format can be changed if needed

    return Response(json.dumps(jsonData), mimetype='application/json')

def getNodeID():
    #function that gets the node ID (name)
    hostInfo = subprocess.check_output('hostnamectl', shell=True)
    pattern = r"Static\s+hostname:.+\n"
    hostName = re.findall(pattern,hostInfo)

    nodeID = hostName[0].replace("Static hostname: ","").replace("\n","")
    return nodeID

if __name__ == "__main__":
    app.run(host='10.31.81.10',port='52117')
