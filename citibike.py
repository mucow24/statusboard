import urllib2
import json

def getData():
  url = "http://citibikenyc.com/stations/json"
  u = urllib2.urlopen(url)
  d = json.loads(u.read())
  return d

def getStationData(data, station_id):
  for station in data['stationBeanList']:
    if int(station['id']) == int(station_id):
      return station
