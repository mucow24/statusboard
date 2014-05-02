import time
import urllib2
import json
import sys

Default_Lat = 40.697017
Default_Lon = -73.995267

Request_Url = "https://api.forecast.io/forecast"

def getWeather(key, lat = Default_Lat, lon = Default_Lon):
  request = "%s/%s/%s,%s" % (Request_Url, key, lat, lon)
  u = urllib2.urlopen(request)
  return json.loads(u.read())

def makeRainPlot(data):
  # Find max precip:
  Inch_to_MM = 25.4
  max_rain_mm = 5
  for e in data['minutely']['data']:
    if e['precipIntensity'] * Inch_to_MM > max_rain_mm:
      max_rain_mm = e['precipIntensity'] * Inch_to_MM
  
  ret = {}
  ret['graph'] = {}
  graph = ret['graph']
  graph['title'] = "Dark Sky Next Hour"
  graph['type']  = "bar"
  graph['yAxis'] = { 'minValue' : 0, 'maxValue' : max_rain_mm }
  graph['datasequences'] = []
  graph['refreshEveryNSeconds'] = 15
  dataseq = graph['datasequences']
  dataseq.append({})
  seq = dataseq[0]
  seq['title'] = "Rain (mm/hr)"
  seq['color'] = 'aqua'
  seq['datapoints'] = []
  ctr = 0
  for e in data['minutely']['data']:
    ctr = ctr + 1
    if ctr % 2 == 0:
      continue
    time_str = time.strftime("%H:%M", time.localtime(e['time']))
    precip   = e['precipIntensity'] * Inch_to_MM
    seq['datapoints'].append({'title' : time_str, 'value' : precip})
  return ret

def main(argv):
  refresh_interval = int(argv[0])
  output_file = argv[1]
  while True:
    d = getWeather()
    p = makeRainPlot(d)
    f = open(output_file, 'w')
    f.write(json.dumps(j, indent = 2, separators = (',', ': ')))
    f.close()
    sleep(refresh_interval)

if __name__ == "__main__":
  main(sys.argv)
