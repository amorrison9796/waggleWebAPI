# waggleWebAPI README

## Overview of Directories/Files

* **beehive-dev-node-0000-code** dir: contains files for connecting to beehive (files written by Bill Catino)
* **presentationMaterial** dir: contains further information on this API and my research paper from summer 2017
* **static** dir: Flask directory containing the .ico image for the local web app and the CSS style sheet
* **templates** dir: Flask directory containing the html page templates for the local web app
* **testFiles** dir: contains files that were used in the creation of the web app; for backup purposes
* **testFiles/genFakeData** dir: contains files used in creation of fake data; for backup purposes
* **detectDiskDevices.sh** file: script that detects which media the node is booted from (file written by Peter Lane)
* **install.sh** file: script that can be run in order to install this system on a Node (NOTE: incomplete)
* **metrics.py** file: python module containing functions to get metrics from nodes
* **send-node-metrics.service** file: service that sends the node data to the RabbitMQ node-metrics queue (to be placed in /etc/systemd/system)
* **sendData.py** file: pushes node data to beehive (contains code written by Bill Catino)
* **start-web-app.service** file: service that starts the local web app on the node (to be placed in /etc/systemd/system)
* **waggleApp.py** file: creates the local web app and sends node data to sendData

# Overview of waggleWebAPI and Installation Notes
This directory contains files and other directories neccesary to run the Waggle Node Metrics API. This system runs on a Node and has three main parts: data aggregation, data transmittance, and the web app. The API can aggregate various metrics from a Node and package them in a Python dictionary in JSON format. It can also send this data to RabbitMQ for holding, where another team member's code would grab it and store it in the beehive-dev database. The final part is a local web view of the aggregated metrics using Flask in Python, HTML, CSS, and a bit of JavaScript. Please see the presentationMaterial directory for further explanation on this API.

**Note:** The beehive-dev-node-0000-code directory usually contains cert and other files that give it access to RabbitMQ. However, these files are not uploaded for security reasons, so new certificates would need to be generated and placed in this directory in order for the data transmittance part of the API to work correctly.

# Installation Notes

