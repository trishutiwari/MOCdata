#!/usr/bin/env python

import influxdb, sys, datetime, time

client = influxdb.InfluxDBClient(host='10.13.37.179',database='sensu_db')

tagsrs = client.query("show tag values from electrical_busplug with key = busplug_ID")

tags = sorted(map(lambda x: x['value'],tagsrs[tagsrs.keys()[0]]))

power = 0
energy = 0
timestamp = 0

for tag in tags:
  rs = client.query("select sum(active_power) as ap, sum(metered_active_energy) as mae from electrical_busplug where time > now() - 3h and busplug_ID = '{0}' group by time(1h) fill(0)".format(tag))
  data = list(rs[rs.keys()[0]])[1]
  power += data['ap']
  energy += data['mae']
timestamp = '%d' % (time.mktime(datetime.datetime.strptime(data['time'],'%Y-%m-%dT%H:%M:%SZ').timetuple())*10**9)
for tag in ['SANDBOX','ER1_A','ER1_B','ER2_A','ER2_B']:
  rs = client.query("select sum(watts) as w, sum(watthours) as wh from electrical_meter where time > now() - 3h and dev_ID = '{0}' group by time(1h) fill(0)".format(tag))
  data = list(rs[rs.keys()[0]])[1]
  power += data['w']
  energy += data['wh']

energy = ("%f" % (energy))    
power = ("%f" % (power))

sys.stdout.write('aggregate  total_datacenter_power={0},total_datacenter_energy={1} {2}\n'.format(power,energy,timestamp))