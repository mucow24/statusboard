import citibike
import sys
import os
import time
import ConfigParser 
import logging
import tokenmanager
import json

def main(argv):
  if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
    print "Usage: %s ini_file" % argv[0]
    sys.exit(1)
  ini_file = argv[1]

  Defaults = {'update_interval_s' : '120',
              'log_level'         : 'INFO',
              'ugcs_refresh_s'    : '-1'}
  config = ConfigParser.SafeConfigParser(Defaults)
  config.read(ini_file)

  logfile = None
  stations = []
  update_interval = None
  log_level = None
  ugcs_refresh_s = None
  try:
    if config.has_option('config', 'log_file'):
      logfile = config.get('config', 'log_file')

    log_level = config.get('config', 'log_level')
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

    update_interval = config.getint('config', 'update_interval_s')

    stations = config.get('config', 'stations')
    stations = map(int, stations.split(','))
    
    output_file = os.path.expanduser(config.get('config', 'output_file'))
    ugcs_refresh_s    = config.getint('config', 'ugcs_refresh_s')
  except Exception as e:
    print "Error parsing config file: %s" % e
    sys.exit(1) 
  
  log_format = "%(asctime)s %(levelname)s %(message)s"
  if logfile:
    logging.basicConfig(filename=logfile, level=log_level, format=log_format)
  else:
    logging.basicConfig(level=log_level, format=log_format)

  try:
    f = open(output_file, 'w')
    f.write('test')
    f.close()
  except:
    err = "Error opening output_file: %s" % output_file
    print err
    logging.critical(err)
    sys.exit(1)
    
  logging.debug("Checking stations...")
  d = citibike.getData()
  for station in stations:
    if station not in d:
      logging.error("\tUnknown station ID: %s" % station)
      sys.exit(1)
    else:
      logging.debug("\tStation OK: %3s (%s)" % (station, d[station]['stationName']))
  logging.info("Citibike StatusBoard Daemon Starting")
  logging.info("Update Interval: %s seconds" % update_interval)

  tm = tokenmanager.TokenManager(ugcs_refresh_s)
  while True:
    tm.updateTokensIfNecessary()
    logging.debug("Updating All Stations...")
    f = open(output_file, 'w')
    try:
      d = citibike.getData()
      ret = {'lastUpdateTime' : time.time() }
      ret['stationData'] = []
      for station in stations:
        sd = d[station]
        bikes = sd['availableBikes']
        docks = sd['availableDocks']
        name  = sd['stationName']
        name = name.replace(" & ", "/")
        name = name.replace(" St", "")
        ret['stationData'].append(
            { 'name'  : name,
              'bikes' : bikes,
              'docks' : docks
            })
      f.write(json.dumps(ret, indent=2))
      f.close()
    except Exception as e:
      logging.error("Exception: %s" % e)
      f.write("%s" % e)
      f.close()
    logging.debug("\tDone.")
    time.sleep(120)

if __name__ == "__main__":
  main(sys.argv)
