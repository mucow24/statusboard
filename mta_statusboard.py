import ConfigParser
import json
import logging
import os
import sys
import time
import tokenmanager

import mta

def makeStationUpdate(name, direction, arrivals):
  station_update = {}
  station_update['stationName']      = name
  station_update['stationDirection'] = direction
  station_update['stationArrivals']  = []
  station_arrivals = station_update['stationArrivals'] 
  for t, r in arrivals:
    station_arrivals.append({'arrivalTime'  : t,
                             'arrivalRoute' : r,
                             'routeColor'   : mta.routeToColor(r) })
  print station_update
  return station_update

def main(argv):
  if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
    print "Usage: %s ini_file" % argv[0]
    sys.exit(1)
  ini_file = argv[1]

  Defaults = {'update_interval_s' : '60',
              'log_level'         : 'INFO',
              'ugcs_refresh_s'    : '-1',
              'num_arrivals'      : '3'}

  config = ConfigParser.SafeConfigParser(Defaults)
  config.read(ini_file)

  output_file = None
  mta_key = None
  update_interval_s = None
  num_arrivals = None
  station_list = None 
  log_file = None
  ugcs_refresh_s = None
  try:
    if config.has_option('general', 'log_file'):
      log_file = config.get('general', 'log_file')
    
    log_level = config.get('general', 'log_level')
    if log_level == "DEBUG":
      log_level = logging.DEBUG
    elif log_level == "INFO":
      log_level = logging.INFO
    elif log_level == "WARNING":
      log_level = logging.WARNING
    elif log_level == "ERROR":
      log_level = logging.ERROR
    elif log_level == "CRITICAL":
      log_level = logging.CRITICAL
    else:
      print "Invalid log level: %s" % log_level
      print "Valid options are DEBUG, INFO, WARNING, ERROR, or CRITICAL"
      sys.exit(1)

    output_file  = os.path.expanduser(config.get('general', 'output_file'))
    mta_key      = config.get('mta', 'api_key')
    num_arrivals = config.getint('mta', 'num_arrivals')
    stations     = config.get('mta', 'stations').split(',')
    stops_file   = os.path.expanduser(config.get('mta', 'stops_file'))
    update_interval_s = config.getint('mta',     'update_interval_s') 
    ugcs_refresh_s    = config.getint('general', 'ugcs_refresh_s')
  except Exception as e:
    print "Error parsing  file: %s" % e
    sys.exit(1) 
  
  log_format = "%(asctime)s %(levelname)s %(message)s"
  if log_file:
    logging.basicConfig(filename=log_file, level=log_level, format=log_format)
  else:
    logging.basicConfig(level=log_level, format=log_format)

  tm = tokenmanager.TokenManager(ugcs_refresh_s)

  while True:
    tm.updateTokensIfNecessary()

    logging.debug("updating data...")
    d = mta.getData(mta_key)
    sd = mta.loadStops(stops_file)
    d = mta.makeStops(d, sd)
    logging.debug("writing json...")

    output = {}
    output['lastUpdateTime'] = time.time()
    output['stationUpdates'] = []
    station_updates = output['stationUpdates']

    for s in stations:
      arr = mta.pruneArrivals(d[s])
      uptown = []
      downtown = []
      for track in arr:
        for i, arrival in enumerate(arr[track]):
          if i >= num_arrivals:
            break
          if track == mta.Uptown_Express_Track or track == mta.Uptown_Local_Track:
            uptown.append( (arrival.timestamp, arrival.route_id) )
          else:
            downtown.append( (arrival.timestamp, arrival.route_id) )
      station_updates.append(makeStationUpdate(d[s].name, 'Uptown',   uptown))
      station_updates.append(makeStationUpdate(d[s].name, 'Downtown', downtown))


    f = open(output_file, 'w')
    f.write(json.dumps(output, indent=2))
    f.close()
    logging.debug("done")
    time.sleep(update_interval_s)

if __name__ == "__main__":
  main(sys.argv)
