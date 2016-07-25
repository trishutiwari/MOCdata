#!/usr/bin/env python

import redis, sys, json, fnmatch

client = redis.Redis("107.23.57.121")

arg = sys.argv[1]

for key in client.keys(arg):
  data = json.loads(client.get(key))
  tag = key[19:-5].replace("-","_").replace(':','_')
  sep = tag.split('_')
  row = sep[0]
  pod = sep[1]
  rack = sep[2]
  bid = sep[3] +"_"+ sep[4] if len(sep) == 5 else sep[3] 
  ap = data['active_power']/10
  cl3h = data['current_l3_hires']/10
  cl3l = data['current_l3_lowres']
  cl1l = data['current_l1_lowres']
  cl1h = data['current_l1_hires']/10
  cl2h = data['current_l2_hires']/10
  cl2l = data['current_l2_lowres']
  cnh = data['current_n_hires']/10
  cnl = data['current_n_lowres']
  freq = data['frequency']/10 
  mae = data['metered_active_energy']
  app = data['apparent_power']/10
  v1 = data['voltage_ln1']/10
  v2 = data['voltage_ln2']/10
  v3 = data['voltage_ln3']/10
  timestamp = int(data["timestamp"])*10**9
  rp = data['reactive_power']/10
  pf = data['power_factor']/1000
  ae = data['active_energy']  
  sys.stdout.write(("electrical_busplug,busplug_ID={0},row={20},pod={21},rack={22},b_id={23} active_power={1},current_l1_hires={2},current_l1_lowres={3},current_l2_hires={4},current_l2_lowres={5},current_l3_hires={6},current_l3_lowres={7},current_n_hires={8},current_n_lowres={9},frequency={10},metered_active_energy={11},apparent_power={12},voltage_ln1={13},voltage_ln2={14},voltage_ln3={15},reactive_power={16},power_factor={17},active_energy={18} {19}\n").format(tag,ap,cl1h,cl1l,cl2h,cl2l,cl3h,cl3l,cnh,cnl,freq,mae,app,v1,v2,v3,rp,pf,ae,timestamp,row,pod,rack,bid))