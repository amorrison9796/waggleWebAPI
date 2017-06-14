from flask import Flask, render_template
from dateutil.parser import parse
from datetime import datetime

import subprocess
import datetime
import pytz
import re

app = Flask(__name__,static_url_path='')

@app.route("/")
def home():
        #basic home page
        return render_template('home.html')

@app.route("/generalInfo")
def generalInfo():
        #get general info about machine using 'hostnamectl'
	getHostName = subprocess.check_output('hostnamectl', shell=True)
	findPattern = r"\s*[a-zA-Z]*:\s*.\n|\s*[a-zA-Z]*\s*[a-zA-Z]*:\s*.*\n"
	
	getInfo = re.findall(findPattern,getHostName)
        return render_template('genInfo.html',getInfo=getInfo)


@app.route("/memInfo")
def memInfo():
	memList = []

        #get info from /proc/meminfo file
	memFile = open('/proc/meminfo')
	memInfo = memFile.readlines()

        #get info from /proc/cpuinfo file
	cpuFile = open('/proc/cpuinfo')
	cpuInfo = [line.split('\n') for line in cpuFile.readlines()]

	#for each line in memInfo, find the given information that fits the reg. exp.
	for x in range(len(memInfo)):

    		findPattern = r"[a-zA-Z0-9]+\([a-zA-Z0-9]+\):\s*[0-9]|[a-zA-Z0-9]+:\s*[0-9]"
    		if re.search(findPattern, memInfo[x]): #replace re.search() with re.finall()?
			memList.append(memInfo[x])
   		else:
    			memList.append(None)

	return render_template('memInfo.html', memList=memList, cpuInfo=cpuInfo)

@app.route("/services")
def services():

	getInfo = subprocess.check_output('systemctl|grep running',shell=True)

	getServices = r".*\.service"
	getSystemdServices = r"systemd-.*\.service"

	#All running services
	runningServList = re.findall(getServices,getInfo)

	#All running services with systemd as the first word
	systemdServList = re.findall(getSystemdServices,getInfo)

	statusList = []
	startTimeList =[]
	upTime = []

        #retreive the status of each systemd service
	for i in systemdServList:
    		command = "systemctl status " + i
    		status = subprocess.check_output(command,shell=True)
    		statusList.append(status)

        #parse out the line containing "Active: " and
    	#parse out the start time of the service
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

        return render_template('services.html', runningServList=runningServList, systemdServList=systemdServList, upTime=upTime)


if __name__ == "__main__":
	app.run()
