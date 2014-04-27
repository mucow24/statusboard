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
  ret = {}
  ret['graph'] = {}
  graph = ret['graph']
  graph['title'] = "Dark Sky Next Hour"
  graph['type']  = "line"
  graph['yAxis'] = { 'minValue' : 0, 'maxValue' : 0.5 }
  graph['datasequences'] = []
  dataseq = graph['datasequences']
  dataseq.append({})
  seq = dataseq[0]
  seq['title'] = "Rain (in/hr)"
  seq['refreshEveryNSeconds'] = 15
  seq['color'] = 'aqua'
  seq['datapoints'] = []
  for e in data['minutely']['data']:
    time_str = time.strftime("%H:%M", time.localtime(e['time']))
    precip   = e['precipIntensity']
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
