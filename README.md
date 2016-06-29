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

However, to avoid code duplication, I have used the same check command for all the busplug checks, and the same one 
for all irc checks. The check command for each check therefore points to the same python file, but the command also 
includes a command line argument that instructs each check to look at only a subset of the busplug/irc data.

The check result from each of these checks is then handled by 