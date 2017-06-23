from flask import Flask, render_template, Response
from dateutil.parser import parse
from datetime import datetime

import subprocess
import datetime
import json
import html
import pytz
import re

app = Flask('waggleWebAPI',static_url_path='')

@app.route("/")
def home():
        #basic home page - does not need a get function
        return render_template('home.html')

@app.route("/generalInfo")
def generalInfo():
        #pass general info to html template
	genInfo = getGeneralInfo()
	nodeUpTime = getNodeUpTime()
        return render_template('genInfo.html',genInfo=genInfo,upTimeSecs=nodeUpTime[0],upTimeFormat=nodeUpTime[1])

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

        pattern = r"\d*\.\d*\s+"
        upTime = re.findall(pattern,upTimeCmd)

        nodeUpTime.insert(0,str(upTime[0]))
        nodeUpTime.insert(1,str(datetime.timedelta(seconds=int(float(upTime[0])))))

        return nodeUpTime
        

@app.route("/nodeApi")
def sendGenInfo():
        #test function that sends general computer info to Zach's API
        getInfo = getGeneralInfo()
        with open('/home/adammorr/API/jsonFile.json') as data:
                jsonData = json.load(data)
        return Response(json.dumps(jsonData), mimetype='application/json')

@app.route("/memInfo")
def memInfo():
	#pass memory and CPU info to html template
        memoryInfo = getMemInfo()
        cpuInfo = getCPUInfo()
        
	return render_template('memInfo.html', memoryInfo=memoryInfo, cpuInfo=cpuInfo)

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

#if __name__ == "__main__":
	#app.run(host= '0.0.0.0',port='5000')
