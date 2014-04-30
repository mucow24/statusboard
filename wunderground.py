import urllib2
import json
import statusboard

reload(statusboard)

def getHourlyData(key, zipcode): 
  req_url = "http://api.wunderground.com/api/%s/hourly10day/q/%s.json" % (key, zipcode)
  u = urllib2.urlopen(req_url)
  return json.loads(u.read())

def processHourlyData(hourly_data, units="english"):
  data = hourly_data['hourly_forecast']
  ret = {}
  ret['temps'] = []
  ret['winds'] = []
  ret['rains'] = []
  ret['pops']  = []
  ret['times'] = []
  temps = ret['temps']
  winds = ret['winds'] 
  rains = ret['rains']
  pops  = ret['pops']
  times = ret['times']

  day_count = 0
  ctr = 0
  for ent in data:
    temps.append(int(ent['temp'][units]))
    winds.append(int(ent['wspd'][units]))
    pops.append(int(ent['pop']))
    hour = int(ent['FCTTIME']['hour'])
    if hour > 12:
      hour = hour - 12
    elif hour == 0:
      hour = 12

    if ent['FCTTIME']['hour'] == '0':
      day_count = day_count + 1
    if day_count == 4:
      break

    time = "%s %s%s" % (ent['FCTTIME']['weekday_name_abbrev'],
                        hour,
                        ent['FCTTIME']['ampm'])

    # time = int(ent['FCTTIME']['epoch'])
    times.append(time)
    # if ent['FCTTIME']['hour'] == "0":
    #   days.append(time)

  #print temps
  #print pops
  #orange = "#ff6b00"
  #aqua   = "#0068EA"
  #plt.figure(figsize=(762, 122), dpi=1, facecolor='black', edgecolor='black', frameon=False)
  #plt.subplot('111', axisbg='black')
  #plt.ylim( (0, 100) )
  #plt.step(times, temps, color=orange, linewidth=2)
  #plt.step(times, winds, color='lightgreen')
  #plt.bar(times, pops, color=aqua, edgecolor=aqua, width = 3600)
  #for day in days:
  #  plt.axvline(day, color='white')
  ##plt.step(times, rains)
  #plt.show()
  return ret
  
def makeStatusBoard(processed_hourly_data):
  g = statusboard.Graph("Wunderground Forecast")
  g.setLimits(ymin = 0, ymax = 100)
  temp   = statusboard.DataSequence("Temp (F)")
  precip = statusboard.DataSequence("Precip (%)")
  wind   = statusboard.DataSequence("Wind (mph)")
  temp.color   = statusboard.DataSequence.Color.RED
  precip.color = statusboard.DataSequence.Color.AQUA
  wind.color   = statusboard.DataSequence.Color.YELLOW
  for i in range(len(processed_hourly_data['times'])):
    time_str = processed_hourly_data['times'][i]
    temp.addDatapoint(time_str, processed_hourly_data['temps'][i])
    precip.addDatapoint(time_str, processed_hourly_data['pops'][i])
    wind.addDatapoint(time_str, processed_hourly_data['winds'][i])
  g.addDatasequence(temp)
  g.addDatasequence(precip)
  g.addDatasequence(wind)
  g.refresh = 15
  return json.dumps(g.render(), indent=2)
