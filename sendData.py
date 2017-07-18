import json
import pika
import time
import requests
from datetime import datetime

from Aggregation import sendMetrics

dir = "/root/waggleWebAPI/beehive-dev-node-0000-code"

sampleRate = 3 #how often the node should be pinged for metrics (in seconds)

#addr = "http://0.0.0.0:52117/metrics"

credentials = pika.credentials.PlainCredentials('node', 'waggle')

ssl_options={'ca_certs' : dir + "/cacert.pem",
             'certfile' : dir + "/node/cert.pem",
             'keyfile'  : dir + "/node/key.pem"}
#print 'ssl_options = ', ssl_options

params = pika.ConnectionParameters(
                host="10.10.10.5", 
                port=23181, 
                credentials=credentials, 
                ssl=True, 
                ssl_options=ssl_options,
                retry_delay=10,
                socket_timeout=10)
#print 'params = {}'.format(params)

connection = pika.BlockingConnection(params)
#print 'connection = {}'.format(connection)

channel = connection.channel()
#print 'channel = {}'.format(channel)


properties = pika.BasicProperties(
            headers = {
                'value' : 80, 
                'reply_to' : "0000020000000000"},
            timestamp=int(time.time()),
            reply_to="0000020000000000")
#print 'properties = {}'.format(properties)

while 1:
    time.sleep(sampleRate)

    #req = requests.get(addr)
    #jsonData = req.json()
    jsonData = sendMetrics()
    #print str(jsonData)
    channel.basic_publish(exchange='node-metrics', 
                    routing_key='', 
                    body=str(jsonData), 
                    properties=properties)
    print json

