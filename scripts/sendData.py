import json
import time
import requests
from datetime import datetime

sampleRate = 5 #how often the node should be pinged for metrics (in seconds)

addr = "http://0.0.0.0:52117/metrics"

while 1:
    time.sleep(sampleRate)

    req = requests.get(addr)
    jsonData = req.json()
    print jsonData
