#!/usr/bin/env python

import influxdb, sys, fnmatch, datetime, time

client = influxdb.InfluxDBClient(database='MOCdata')

tagsrs = client.query("show tag values from electrical_busplug with key = busplug_ID")

def pod(x):
  return x['value'] if fnmatch.fnmatch(x['value'],sys.argv[1]) else None
    
tags = sorted([x for x in map(pod,tagsrs[tagsrs.keys()[0]]) if x != None])

#print tagsrs

power = []
energy = []
rackp = dict()
racke = dict()

for tag in tags:
  rs = client.query("select sum(active_power) as ap, sum(metered_active_energy) as mae from electrical_busplug where time > now() - 3h and busplug_ID = '{0}' group by time(1h) fill(0)".format(tag))
  data = list(rs[rs.keys()[0]])[1]
  power.append(data['ap'])
  energy.append(data['mae'])
timestamp = '%d' % (time.mktime(datetime.datetime.strptime(data['time'],'%Y-%m-%dT%H:%M:%SZ').timetuple())*10**9)

try:
  for n,tag in enumerate(tags):
    if 'R12' in tag:
      rackp[tag[:-2]] = power[n]
      racke[tag[:-2]] = energy[n]     
    elif fnmatch.fnmatch(tag[:-2],tags[n+2][:-2]): #there don't seem to be any racks with 4 busplugs, but checking anyways as it was mentioned in the email
      rackp[tag[:-3]] = sum(power[n:n+4])
      racke[tag[:-3]] = sum(energy[n:n+4])
    else:
      rackp[tag[:-3]] = sum(power[n:n+2])
      racke[tag[:-3]] = sum(energy[n:n+2])
except IndexError:
  pass
  
for i in range(len(rackp)):
  busplug_id = rackp.keys()[i]
  p = rackp[busplug_id] 
  e = racke[busplug_id]
  sys.stdout.write('aggregate,busplug_ID={0} active_power={1},metered_active_energy={2} {3}\n'.format(busplug_id,p,e,timestamp))
  