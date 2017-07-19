from dateutil.parser import parse
from datetime import datetime

import subprocess
import datetime
import json
import time
import pytz
import re

#get CPU info from node
getInfo = subprocess.check_output('cat /proc/cpuinfo', shell=True)

coreRE = r"cpu cores\s*:.*"
vendorRE = r"vendor_id\s*:.*"
modelRE = r"model name\s*:.*"

vendorInfo = re.search(vendorRE,getInfo).group(0)
cpuInfo = re.search(coreRE,getInfo).group(0)
modelInfo = re.search(modelRE,getInfo).group(0)

cpuCores = re.sub(r"cpu cores\s*:\s*", "", cpuInfo)
vendorId = re.sub(r"vendor_id\s*:\s*", "", vendorInfo)
modelName = re.sub(r"model name\s*:\s*", "", modelInfo)

cpuInfo = {"CPUCores":cpuCores,"VendorID":vendorId,"ModelName":modelName}

return cpuInfo

