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
Each of the keys  

Then I wrote check definitions for each. Soon, I realized that there was too much data in categories 1) and 2) to be 
handled by single checks. 
Hence, I created individual checks for each subset of the busplug and irc data (these can be found in the irc and
busplug folders within the CheckDefinitions folder)

However, to avoid code duplication, I have used the same check command script for all the busplug checks, and the same one 
for all irc checks. Therefore, the check command for each check points to the same python file, but the command also 
includes a command line argument that instructs each check to look at only a subset of the busplug/irc data.

For example:

the busplugR1PA.json check file includes the following command:

"command":"busplug.py electrical:busplug*R1*PA*"

So this tells the check to execute the busplug.py file, and look at only the busplug keys of the form "electrical:busplug*R1*PA*". 
Similarly, other busplug checks also point towards the busplug.py file, but have different command line arguments (for instance,
electrical:busplug*R1*PB*, electrical:busplug*R2*PA*, etc).
So all of them use the same script but with different inputs. 

Each check command script parses the json data stored in the redis keys, picks out the values needed, and then formats those values in the
influxdb format. This formatted data is then sent to sys.stdout, from where it is picked up by the handlers.

The check result from all checks is then handled by one handler called "influxdb" (located in the handlers.json file). 
This handler is responsible for transferring all the check results via udp (port 8090) to influxdb.

Before the handler is executed, however, we must remove all unecessary data that sensu adds to the check results.
This is done via a sensu mutator (called "only_check_output", and located in the mutator.json file), which picks out solely
the output that we wish to transfer. 

Once the mutator is excuted, the data is transferred by the handler and recieved by influxdb.
