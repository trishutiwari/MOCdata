#!/usr/bin/env python

import redis, sys, json, time, fnmatch, traceback

client = redis.Redis("107.23.57.121")

arg = sys.argv[1]

for key in client.keys(arg):
  data = json.loads(client.get(key))
  tag =  key[15:26].replace("-","_")
  for i in data.keys():
    try:
      if (fnmatch.fnmatch(i,"mac_addr_*")) or i=="timestamp": 
        continue #because all the mac addresses are 0 and we don't want to register the timestamp as a seperate value
      else:
        sys.stdout.write(("mechanical_irc,irc_ID={0} {1}={2} {3}\n").format(tag,i,data[i],int(data["timestamp"])*10**9))
    except KeyError: #some json objects don't have a timestamp, so we assign one ourselves
      sys.stdout.write(("mechanical_irc,irc_ID={0} {1}={2} {3}\n").format(tag,i,data[i],time.time()*10**9))