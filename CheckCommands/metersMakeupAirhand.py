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
      metric = data['metric'][:26].replace(":","_")
    elif fnmatch.fnmatch(key,"electrical:meters:*"):
      field = data['metric'].replace(".","_").replace("electrical_meter_","")
      tagValue = tags['deviceid'].replace("-","_")
      sys.stdout.write("electrical_meter,device_id={0} {1}={2} {3}\n".format(tagValue, field,value,timestamp))
      continue
    else:
      metric = data['metric'][:24].replace(":","_")
    try:
      tagKey = tags.keys()[0].replace("-","_")
      tagValue = tags[tagKey].replace("-","_")
      sys.stdout.write("{0},{1}={2} value={3} {4}\n".format(metric, tagKey, tagValue, value, timestamp))
    except AttributeError: #if tags is not a dictionary
      sys.stdout.write("{0},device_id={1} value={2} {3}\n".format(metric, tags.replace("-","_"), value, timestamp))

sys.exit(0)  