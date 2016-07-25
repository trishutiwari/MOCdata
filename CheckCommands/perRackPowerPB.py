#!/usr/bin/env python

import influxdb, sys, fnmatch, datetime, time

client = influxdb.InfluxDBClient(database='sensu_db')

tagsrs = client.query("show tag values from electrical_busplug with key = busplug_ID")

def pod(x):
  return x['value'] if fnmatch.fnmatch(x['value'],sys.argv[1]) else None
    
tags = sorted([x for x in map(pod,tagsrs[tagsrs.keys()[0]]) if x != None])


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

c = 0
try:
  for tag in tags:
    if 'R12' in tags[c]:
      rackp[tags[c][:-3]] = power[c]
      racke[tags[c][:-3]] = energy[c]
      c+=1
    elif len(tags[c]) == 12:
      rackp[tags[c][:-3]] = sum(power[c:c+2])
      racke[tags[c][:-3]] = sum(energy[c:c+2])
      c+=2     
    elif len(tags[c]) == 14: #if a rack has 3 or 4 busplugs
      if fnmatch.fnmatch(tags[c][:-4],tags[c+3][:-4]): #if a rack has 4 busplugs
        rackp[tags[c][:-5]] = sum(power[c:c+4])
        racke[tags[c][:-5]] = sum(energy[c:c+4])
        c+=4
      elif fnmatch.fnmatch(tags[c][:-4],tags[c+2][:-4]): #if a rack has 3 busplugs
        rackp[tags[c][:-5]] = sum(power[c:c+3])
        racke[tags[c][:-5]] = sum(energy[c:c+3])
        c+=3
except IndexError:
  pass
  
for i in range(len(rackp)):
  busplug_id = rackp.keys()[i]
  p = rackp[busplug_id] 
  e = racke[busplug_id]
  sys.stdout.write('aggregate,busplug_ID={0} active_power={1},metered_active_energy={2} {3}\n'.format(busplug_id,p,e,timestamp))
  