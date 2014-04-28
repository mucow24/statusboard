import darksky
import wunderground
import json
import time
import sys
import os

Darksky_Lat = 40.697017
Darksky_Lon = -73.995267

def log(string):
  print "%s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string)

def main(argv):
  output_file = os.path.expanduser(argv[1])
  ds_key = argv[2]
  wund_key = argv[3]

  first = True
  last_ts = 0
  ctr = 0
  while True:
    ts = int(time.time())
     
    if ts == last_ts:
      time.sleep(1)
      continue

    if first or (ts % 120 == 0):
      # Update dark sky:
      log("updating ds")
      d = darksky.getWeather(key = ds_key)
      p = darksky.makeRainPlot(d)
      ds_json = json.dumps(p, indent = 2)
      last_ts = ts

    if first or (ts % 600 == 0):
      log("updating wu")
      # Update wunderground
      d = wunderground.getHourlyData(wund_key, 11201)
      p = wunderground.processHourlyData(d)
      wu_json = wunderground.makeStatusBoard(p)
      last_ts = ts

    # Cycle plot data:
    if first or (ts % 30 == 0):
      last_ts = ts
      f = open(output_file, 'w')
      if ctr % 2:
        log("wrote ds")
        f.write(ds_json)
      else:
        log("wrote wu")
        f.write(wu_json)
      f.close()
      ctr = ctr + 1
    first = False
    time.sleep(1)

if __name__ == "__main__":
  main(sys.argv)
