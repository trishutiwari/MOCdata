#!/usr/bin/env python

import influxdb, sys, datetime, time

client = influxdb.InfluxDBClient(host='10.13.37.179',database='sensu_db')

tagsrs = client.query("show tag values from electrical_busplug with key = busplug_ID")

tags = sorted(map(lambda x: x['value'],tagsrs[tagsrs.keys()[0]]))

#print tags
poda = [] 
podb = []
podc = []

powera = []
energya = []
powerb = []
energyb = []
powerc = []
energyc = []

timestamp = 0

for tag in tags:
  if 'PA' in tag:
    poda.append(tag) 
  elif 'PB' in tag:
    podb.append(tag) 
  elif 'PC' in tag:
    podc.append(tag) 

def resultCalc(pod,power,energy):
  global timestamp 
  for tag in pod:
    rs = client.query("select sum(active_power) as ap, sum(metered_active_energy) as mae from electrical_busplug where time > now() - 3h and busplug_ID = '{0}' group by time(1h) fill(0)".format(tag))
    data = list(rs[rs.keys()[0]])[1]
    power.append(data['ap'])
    energy.append(data['mae'])
  timestamp = '%d' % (time.mktime(datetime.datetime.strptime(data['time'],'%Y-%m-%dT%H:%M:%SZ').timetuple())*10**9)

resultCalc(poda,powera,energya)
resultCalc(podb,powerb,energyb)
resultCalc(podc,powerc,energyc)


sys.stdout.write('aggregate,pod=A active_power={0},metered_active_energy={1} {2}\n'.format(('%f' % sum(powera)),('%f' %sum(energya)),timestamp))
sys.stdout.write('aggregate,pod=B active_power={0},metered_active_energy={1} {2}\n'.format(('%f' % sum(powerb)),('%f' %sum(energyb)),timestamp))
sys.stdout.write('aggregate,pod=C active_power={0},metered_active_energy={1} {2}\n'.format(('%f' % sum(powerc)),('%f' %sum(energyc)),timestamp))