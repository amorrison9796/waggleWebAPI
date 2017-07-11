# waggleWebAPI README

## Overview of Directories/Files

* **beehive-dev-node-0000-code** dir: contains files for connecting to beehive (files written by Bill Catino)
* **static** dir: Flask directory containing the .ico image for the local web app and the CSS style sheet
* **templates** dir: Flask directory containing the html page templates for the local web app
* **testFiles** dir: contains files that were used in the creation of the web app; for backup purposes
* **testFiles/genFakeData** dir: contains files used in creation of fake data; for backup purposes
* **send-node-metrics.service** file: service that sends the node data to the RabbitMQ node-metrics queue (to be placed in /etc/systemd/system)
* **sendData.py** file: pushes node data to beehive (contains code written by Bill Catino)
* **start-web-app.service** file: service that starts the local web app on the node (to be placed in /etc/systemd/system)
* **waggleApp.py** file: creates the local web app and sends node data to sendData
* **waggleApp.pyc** file: compiled waggleApp.py file
