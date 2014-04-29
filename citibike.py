import urllib2
import json

def getData():
  url = "http://citibikenyc.com/stations/json"
  u = urllib2.urlopen(url)
  d = json.loads(u.read())
  data_by_station_id = {}
  for station in d['stationBeanList']:
    data_by_station_id[int(station['id'])] = station
  return data_by_station_id

