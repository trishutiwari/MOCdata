#!/usr/bin/env python

import redis, sys, json, time, fnmatch

client = redis.Redis("107.23.57.121")

for key in client.keys():
  if not (fnmatch.fnmatch(key,"electrical:meters:*") or fnmatch.fnmatch(key,"mechanical:makeup*") or fnmatch.fnmatch(key,"mechanical:airhand**") or fnmatch.fnmatch(key,"mechanical:irc*") or fnmatch.fnmatch(key,"electrical:busplug*")): #these keys are already dealt with by other checks
    if "JSON" in key: #the ones that don't have "JSON" are not data points
      data = json.loads(client.get(key))
      try:
        timestamp = ("%f" % (data['timestamp']*10**9))[:-7] #getting rid of scientific notation and trailng zeroes
      except KeyError:
        timestamp = ("%f" % (time.time()*10**9))[:-7]
      if key == "mechanical:cooling:CTTotal:JSON":
        #special case, lots of data points
        v1 = data["tons_daily_avg"]
        v2 = data["gpm_daily_avg"]
        v3 = data["gal_makeup_total"]
        v4 = data["gal_blowdown_total"]
        sys.stdout.write("mechanical_cooling CTTotal_tons_daily_avg={0},CTTotal_gpm_daily_avg={1},CTTotal_gal_makeup_total={2},CTTotal_gal_blowdown_total={3} {4}\n".format(v1,v2,v3,v4,timestamp))
      elif fnmatch.fnmatch(key,"mechanical:cooling*"):
        k = data.keys()[1]
        field = key[19:-4].replace(':','_')+ '(' + k.replace(':','_') + ')' 
        value = data[k]
        sys.stdout.write("mechanical_cooling {0}={1} {2}\n".format(field,value,timestamp))
      elif fnmatch.fnmatch(key,"electrical:generator*"):
        k = data.keys()[1]
        field = k + "_" + key[21:25]
        value = data[k]
        sys.stdout.write("electrical_generator {0}={1} {2}\n".format(field,value,timestamp))
      else:
        try:
          devID = data['tags'].replace("-","_")
          metric = data['metric'].replace(devID,'').replace(':','_').replace('JSON','')[:-2]
          value = data['value']
          sys.stdout.write("{0},dev_ID={1} value={2} {3}\n".format(metric,devID,value,timestamp))
        except KeyError:
          if 'status' in key: #just two data points that are wierd. 
            metric = key.replace(":","_").replace("JSON","")
            iteration = data["iteration"]
            lastfetch = data["lastfetch"].replace(",","").replace(" ","_") #the commas and spaces cause problems with the influxdb line protocol
            lastredisupdate = data["lastredisupdate"].replace(",","").replace(" ","_") 
            sys.stdout.write("{0},lastFetch={1},lastRedisUpdate={2} iteration={3} {4}\n".format(metric,lastfetch,lastredisupdate,iteration,timestamp))
          else:
            measurement = data.keys()[1]
            value = data[measurement]
            key = key.replace(":","_").replace("JSON","")
            sys.stdout.write("{0} {1}={2} {3}\n".format(key, measurement,value,timestamp))
             