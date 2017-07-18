from dateutil.parser import parse
from datetime import datetime

import subprocess
import datetime
import json
import time
import pytz
import re


#get general info about machine using 'hostnamectl'
getHostName = subprocess.check_output('hostnamectl', shell=True)
findPattern = r"\s*[a-zA-Z]*:\s*.\n|\s*[a-zA-Z]*\s*[a-zA-Z]*:\s*.*\n"

info = re.findall(findPattern,getHostName)

genInfoList = {}

for i in info:
    #metricRE = r"\s*[a-zA-Z]*:\s*.\n|\s*[a-zA-Z]*\s*[a-zA-Z]*:\s*.*\n"
    metricRE = r"\s*[a-zA-Z]*:|\s*[a-zA-Z]*\s*[a-zA-Z]*:"
    valueRE = r":\s*.*\n"#\s*\.*\n"
    metric = re.findall(metricRE, i)
    print metric
    value = re.findall(valueRE, i)
    print value
    genInfoList.update({metric[0].replace(":","").replace(" ",""):value[0].replace(": ","").replace("\n","")})

print genInfoList

