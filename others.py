#!/usr/bin/env python

import redis, sys, json, time, fnmatch, traceback, re

client = redis.Redis("107.23.57.121")

for key in client.keys():
  if not (fnmatch.fnmatch(key,"electrical:meters:*") or fnmatch.fnmatch(key,"mechanical:makeup*") or fnmatch.fnmatch(key,"mechanical:airhand**") or fnmatch.fnmatch(key,"mechanical:irc*") or fnmatch.fnmatch(key,"electrical:busplug*")): #these keys are already dealt with by other checks
    if "JSON" in key: #the ones that don't have json are not data points
      data = json.loads(client.get(key))
      try:
        devID = data['tags'].replace("-","_")
        metric = data['metric'].replace(devID,'').replace(':','_').replace('JSON','')[:-2]
        timestamp = ("%f" % (data['time']*10**9))[:-7] #getting rid of scientific notation and trailng zeroes
        value = data['value']
        sys.stdout.write("{0},dev_ID={1} value={2} {3}\n".format(metric,devID,value,timestamp))
      except KeyError:
        try:
          timestamp = ("%f" % (data['timestamp']*10**9))[:-7]
          measurement = data.keys()[1]
          value = data[measurement]
          key = key.replace(":","_").replace("JSON","")
          sys.stdout.write("{0} {1}={2} {3}\n".format(key, measurement,value,timestamp))
        except KeyError: #just two data points that are wierd. 
          metric = key.replace(":","_").replace("JSON","")
          iteration = data["iteration"]
          lastfetch = data["lastfetch"].replace(",","").replace(" ","_") #the commas and spaces cause problems with the influxdb line protocol
          lastredisupdate = data["lastredisupdate"].replace(",","").replace(" ","_")
          timestamp = ("%f" % (time.time()*10**9))[:-7] 
          sys.stdout.write("{0},lastFetch={1},lastRedisUpdate={2} iteration={3} {4}\n".format(metric,lastfetch,lastredisupdate,iteration,timestamp)) 