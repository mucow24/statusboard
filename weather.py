import darksky
import wunderground
import json
import time
import sys
import os
import ConfigParser 
import logging

Darksky_Lat = 40.697017
Darksky_Lon = -73.995267


def main(argv):
  if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
    print "Usage: %s ini_file" % argv[0]
    sys.exit(1)
  ini_file = argv[1]

  Defaults = {'update_interval_s' : '120',
              'log_level'         : 'INFO',
              'latitude'          : Darksky_Lat,
              'longitude'         : Darksky_Lon,
              'zip'               : '11201',
              'cycle_interval_s'  : '15',
              'ugcs_refresh_s'    : '0'}
  config = ConfigParser.SafeConfigParser(Defaults)
  config.read(ini_file)

  output_file = None
  log_file = None
  ds_key = None
  ds_refresh_s = None
  
  wu_refresh_s = None
  wu_key = None
  wu_zip = None
  
  cycle_s      = None
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

    ds_refresh_s = config.getint('darksky', 'update_interval_s')
    ds_key       = config.get('darksky', 'api_key')
    wu_refresh_s = config.getint('wunderground', 'update_interval_s')
    wu_key       = config.get('wunderground', 'api_key')
    cycle_s      = config.getint('general', 'graph_cycle_s')
    ugcs_refresh_s = config.getint('general', 'ugcs_refresh_s')
    
    output_file = os.path.expanduser(config.get('general', 'output_file'))
  except Exception as e:
    print "Error parsing  file: %s" % e
    sys.exit(1) 
  
  log_format = "%(asctime)s %(levelname)s %(message)s"
  if log_file:
    logging.basicConfig(filename=log_file, level=log_level, format=log_format)
  else:
    logging.basicConfig(level=log_level, format=log_format)
    
  first = True
  last_ts = 0
  ctr = 0
  while True:
    ts = int(time.time())
     
    if ts == last_ts:
      time.sleep(1)
      continue

    if first or (ts % ds_refresh_s == 0):
      # Update dark sky:
      logging.debug("updating ds")
      d = darksky.getWeather(key = ds_key)
      p = darksky.makeRainPlot(d)
      ds_json = json.dumps(p, indent = 2)
      last_ts = ts

    if first or (ts % wu_refresh_s == 0):
      logging.debug("updating wu")
      # Update wunderground
      d = wunderground.getHourlyData(wu_key, wu_zip)
      p = wunderground.processHourlyData(d)
      wu_json = wunderground.makeStatusBoard(p)
      last_ts = ts

    # Cycle plot data:
    if first or (ts % cycle_s == 0):
      last_ts = ts
      f = open(output_file, 'w')
      if ctr % 2:
        logging.debug("wrote ds")
        f.write(ds_json)
      else:
        logging.debug("wrote wu")
        f.write(wu_json)
      f.close()
      ctr = ctr + 1

  # UGCS Specific -- update tokens:
  if ugcs_refresh_s:
    if (ts % ugcs_refresh_s == 0 or first):
      logging.info("Updating UGCS tokens")
      os.system('kinit -R && aklog')
  
  first = False
  time.sleep(1)

if __name__ == "__main__":
  main(sys.argv)
