### MOC Data
#Transferring MOC data from Redis to InfluxDB using python

I used Python and the following technologies to carry out the project:

1) [Sensu](https://sensuapp.org/)
   Sensu is a monitoring framework used to collect the specefied data from client computers at regular intervals.

2) [Redis](http://redis.io/)
   Redis is a key-value database. This was the database in which all the MOC Data was originally stored.
   
3) [InfluxDB](https://influxdata.com/)
   InfluxDB is a time-series database. This is the database to which I transferred all the data from Redis.

4) [Uchiwa](https://uchiwa.io/)
   Uchiwa is a framework used to monitor the data sent out by Sensu.

5) [Grafana](http://grafana.org/)
   Grafana provides beautiful dashboards for us to graph data stored in InfluxDB.

#Overview:

![logo](https://github.com/trishutiwari/MOCdata/blob/master/Overall-FrameWork.png)

In a nutshell, I have written 4 python scripts that Sensu executes every minute. Each time the scripts are executed, they
create a connection with a the Redis database that holds the MOC Data. These scripts then get all the data keys from Redis,
parse their values, pick out the relevant information, and format them properly. This formatted data is then sent
through a UDP connection to influxDB, which then stores the data.  

#Redis Data

I categoriezed the different keys (there are around 1300-1400 keys in total (the actual number fluctuates) )
in the redis instance into 4 types:
 
1) Electrical busplug

2) Mechanical IRC 

3) Electrical meters, Mechanical makeup, and mechanical airhand

4) Others

#Sensu Monitoring

Here is a simplified version of how sensu works:

![logo](https://github.com/trishutiwari/MOCdata/blob/master/Sensu-Model.png)

This is how sensu works in general. However, I have used Sensu's standalone model, which means that the sensu-server
and sensu-client are running on the same machiene.

In order to build a sensu framework, I needed to define a sensu-client. The client is just a json file that declares its
subscriptions to checks on the server:

Here is what a client file looks like:

``` json
{
"client":{

  "name": "ubuntu",

  "address": "127.0.0.1",
  "subscriptions":["metersMakeupAirhand","others","mechanicalIRCR1","mechanicalIRCR2","mechanicalIRCR3","mechanicalIRCR4","mechanicalIRCR5","mechanicalIRCR6","mechanicalIRCR7","mechanicalIRCR8","busplugR1PA","busplugR1PB","busplugR1PC","busplugR2PA","busplugR2PB","busplugR2PC","busplugR3PA","busplugR3PB","busplugR3PC","busplugR4PA","busplugR4PB","busplugR4PC","busplugR5PA","busplugR5PB","busplugR5PC","busplugR6PA","busplugR6PB","busplugR6PC","busplugR7PA","busplugR7PB","busplugR7PC","busplugR8PA","busplugR8PB","busplugR8PC"],

  "socket": {

    "bind": "127.0.0.1",

    "port": 3030

  }
      
 }
    
}
```
The subscriptions line is important, as this line tells the sensu-server what checks the client wishes to execute.
The IP address is the loopback adderess as this is a standalone framework.

I then needed to define checks on the sensu server. Checks are also json formatted files. Here is a sample check:

```json
{"checks":
	{"others":
		{"type":"metric",
                "command":"others.py",
		"standalone": true,
		"subscribers":["others"],
		"handler":"influxdb",
		"interval":60
		}

	}
}
```
The "command" argument tells sensu which script to execute on the client, and the "interval" tells the server 
how often to do so.

I wrote check command scripts (found in the CheckCommands Folder) for each category defined in the beginning. 

Each command simply creates a connection with the Redis database, like so:

```python
import redis
client = redis.Redis("ip address of machiene with redis")
```
The script then gets the keys that fall within its category (Busplug, IRC, .etc)
Each of the keys had values formatted in json, so I had to use python's json module to parse it:

```python
import json
data = json.loads(client.get("Some Redis Key"))
```  
Now the data variable just holds a regular python dictionary. I could then pick out the relevant keys and values and then
format it as per the influxDB requirements. 

Now that the data is formatted, I simply needed to write it out to sys.stdout.

We can easily check if these checks are working through Uchiwa, which is basically provides a UI for looking at the results
published by sensu checks.
Here is what some of our check results look like in Uchiwa:

![logo](https://github.com/trishutiwari/MOCdata/blob/master/uchiwaScreenShot.png)

The great thing about Uchiwa is that it keeps updating itself, thereby allowing us to monitor data in real time.

Once the data is written to stdout, something must take that data from there and transfer it to influxDB. Here is where the
sensu handlers and mutators come in.

So a sensu handler is just a file that tells sensu what to do with the output data. In our case, the handler is configured
to send out the data through a udp port.

InfluxDB also has a UDP api, and so I needed to modify the influxDB configuration file to activate this api.

The mutator, as it's name suggests, is used to mutate the data before its being sent to influxDB through the handler. 

I needed to have a mutator because in addition to the formatted data we print out to stdout, sensu also adds some of its own
meta data before transferring it to the handler. I needed to get rid of this extra data before sending it so as to not cause 
any problems with influxDB's line protocol.
This is what a mutator looks like:

```json
{
"mutators":
 {
"only_check_output": { //this is the name of our mutator
"command": "only_check_output.py"
}
 }

}
```
Here again, the "command" points to the actual python script that will run to pick out only the desired output before
sending it off to InfluxDB.

Side note:
While writing check definitions, I realized that there was too much data in categories 1) and 2) (Electrical Busplug and
Mechanical IRC) to be handled by single checks. 
Hence, I created individual checks for each subset of the busplug and irc data (these can be found in the irc and
busplug folders within the CheckDefinitions folder)

However, to avoid code duplication, I have used the same check command script for all the busplug checks, and the same one 
for all irc checks. Therefore, the check command for each check points to the same python file, but the command also 
includes a command line argument that instructs each check to look at only a subset of the busplug/irc data.

For example:

the busplugR1PA.json check file includes the following command:

``` json
"command":"busplug.py electrical:busplug*R1*PA*"
```

So this tells the check to execute the busplug.py file, and look at only the busplug keys of the form ```json "electrical:busplug*R1*PA*"```. 
Similarly, other busplug checks also point towards the busplug.py file, but have different command line arguments (for instance,
```json electrical:busplug*R1*PB*, electrical:busplug*R2*PA* ```, etc).
So all of them use the same script but with different inputs. 

Once our data is recieved by InfluxDB, it is extremely easy for us to visualize it using Grafana. 

Here are a few screenshots of the data (in Grafana):

Here is some of the Mechanical IRC and apparent/displacement pf data:

Like Uchiwa, graphs in Grafana too can continuosly update themselves to reflect the newer data as it comes in:

To create graphs in grafana, we must first connect to the InfluxDB database. This can be done by going to the "datasources" tab on the grafana homepage.

Once we have connected with our database, all we need to do is to create new dashboards and graphs.

After creating a dashboard, we can add a new row to it, and then add a graph to the row. 

We then click on edit, and go to the metrics part of the graph. Here, we enter an InfluxDB query which specefies what data we want to plot.
We can also select an auto refresh time. In our case, most graphs refresh every minute since that's how often we're collecting the data.

Our grafana instance has the following dashboards:

Electrical Busplug: current,voltage,power and energy

![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/busplugReacPowerEnergy.png)
![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/busplugVoltageCurrent.png)

Mechanical IRC: temperatures

![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/IRC1.png)
![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/IRC2.png)

Mechanical cooling: chillingtowers, exhaust fans, pumps

![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/mechanicalCooling1.png)
![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/mechanicalCooling2.png)
![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/mechanicalCooling3.png)

Electrical Meters: power, energy

![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/metersPowerEnergy.png)

Electrical Generator

![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/electricalGenerator.png)

Weather Station: temperature

![logo](https://github.com/trishutiwari/MOCdata/blob/master/ResultsImages/weatherstation.png)

Aggregate Data: busplug per rack and  per pod power and energy consumption, total datacenter compute energy
