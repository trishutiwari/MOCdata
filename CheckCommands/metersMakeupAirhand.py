#!/usr/bin/env python

import redis, sys, json, time, fnmatch, traceback

client = redis.Redis("107.23.57.121")

for key in client.keys():
  if fnmatch.fnmatch(key,"electrical:meters:*") or fnmatch.fnmatch(key,"mechanical:makeup*") or fnmatch.fnmatch(key,"mechanical:airhand*"):
    try:
      data = json.loads(client.get(key))
    except redis.exceptions.ResponseError:
      continue #some keys are not data sets
    value = data['value']
    tags = data['tags']
    try:
      timestamp = ("%f" % (int(data["timestamp"])*10**9))[:-7]
    except KeyError: #if there is no timestamp
      timestamp = ("%f" % (time.time()*10**9))[:-7]
    if fnmatch.fnmatch(key,"mechanical:airhand*"):
      field = "airhandlingunit"
      metric = "mechanical_cooling"
      devID = data['tags']
      value = data['value']
    elif fnmatch.fnmatch(key,"electrical:meters:*"):
      metric = "electrical_meter"
      field = data['metric'].replace(".","_").replace("electrical_meter_","")
      devID = tags['deviceid'].replace("-","_")
    else:
      field = "makeupairunit"
      metric = "mechanical_cooling"
      devID = data['tags']
      value = data['value']
    sys.stdout.write("{0},dev_ID={1} {2}={3} {4}\n".format(metric, devID, field, value, timestamp))

sys.exit(0)  