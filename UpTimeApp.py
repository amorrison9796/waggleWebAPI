from flask import Flask, render_template, Response
from dateutil.parser import parse
from datetime import datetime

import subprocess
import datetime
import json
import html
import pytz
import re

app = Flask('UpTimeApp',static_url_path='')

@app.route("/")
def sendUpTime():
    #send up time
    
    nodeUpTime = getNodeUpTime()
    nodeId = getNodeId()
    
    data = {}
    
    data.update({nodeUpTime:nodeId})
    jsonData = json.load(data)
    
    return Response(json.dumps(jsonData), mimetype='application/json')

def getNodeUpTime():
    #get up time of the current node
    nodeUpTime = []
    upTimeCmd = subprocess.check_output('cat /proc/uptime', shell=True)

    pattern = r"\d*\.\d*\s+"
    upTime = re.findall(pattern,upTimeCmd)

    nodeUpTime = str(upTime[0])
    return nodeUpTime
        
def getNodeId():
    hostInfo = subprocess.check_output('hostnamectl', shell=True)

    pattern = r"Static\s+hostname:.+\n"
    hostName = re.findall(pattern,hostInfo)

    return hostName[0]



if __name__ == "__main__":
    app.run(host= '0.0.0.0',port='6000')

    
    
