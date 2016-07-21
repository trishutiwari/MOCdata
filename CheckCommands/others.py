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
      elif fnmatch.fnmatch(key,"mechanical*"):
        if 'tower' in key: #cooling tower and cooling tower pump
          if 'pump' in key:
            field = key[18:-12]
          else:
            field = key[18:-11]
          value = data['value']
          tags = data['tags']
          sys.stdout.write("mechanical_cooling,dev_ID={0} {1}={2} {3}\n".format(tags,field,value,timestamp))
        else: 
          if "cooling" in key: #CTTotal_gal_blowdown_total,	CTTotal_gal_makeup_total, etc
            k = data.keys()[1]
            value = data[k]
            if 'CH' in key:
              dev_id = key[19:-5].replace(':','_')
              sys.stdout.write("mechanical_cooling,dev_ID={0} chiller_kwh={1} {2}\n".format(dev_id,value,timestamp))
            else:
              if 'Sys' in key:
                field = key[19:-5]
              else:
                field = key[19:-5].replace(':','_')+ '_' + k.replace(':','_') 
              sys.stdout.write("mechanical_cooling {0}={1} {2}\n".format(field,value,timestamp))
          elif "status" not in key: #hotwater pump, chilled water pump, and exhaust fan
            if "hotwater" in key:
              field = "hotwaterpump"
            elif "chilled" in key:
              field = "chilledwaterpump"
            elif "exhaustfan" in key:
              field = "exhaustfan"
            dev_ID = data['tags']
            value = data['value']
            sys.stdout.write("mechanical_cooling,dev_ID={0} {1}={2} {3}\n".format(dev_ID,field,value,timestamp))
      elif fnmatch.fnmatch(key,"electrical:generator*"):
        k = data.keys()[1]
        field = k + "_" + key[21:25]
        value = data[k]
        sys.stdout.write("electrical_generator {0}={1} {2}\n".format(field,value,timestamp))
      else:
        if 'status' in key: #database update status stats 
          typ = key.replace(":","_").replace("JSON","")
          iteration = data["iteration"]
          lastfetch = data["lastfetch"].replace(",","").replace(" ","_") #the commas and spaces cause problems with the influxdb line protocol
          lastredisupdate = data["lastredisupdate"].replace(",","").replace(" ","_") 
          sys.stdout.write("collector_status,type={0},lastFetch={1},lastRedisUpdate={2} iteration={3} {4}\n".format(typ,lastfetch,lastredisupdate,iteration,timestamp))
        else: #environmental_weatherstation
          measurement = data.keys()[1]
          value = data[measurement]
          key = "environmental_weatherstation"
          sys.stdout.write("{0} {1}={2} {3}\n".format(key, measurement,value,timestamp))
          