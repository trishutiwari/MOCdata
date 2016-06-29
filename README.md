# MOCdata
Transferring MOC data from redis to influxDB using python

I categoriezed the different keys (there were 1302 keys in total) in the redis instance into 4 types:
 
1) Electrical busplug

2) Mechanical IRC 

3) Electrical meters, Mechanical makeup, and mechanical airhand

4) Others

I wrote check command scripts for each category (found in the CheckCommands Folder)

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
