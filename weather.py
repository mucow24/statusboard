import darksky
import wunderground
import json
import time
import sys
import os

Darksky_Lat = 40.697017
Darksky_Lon = -73.995267


def main(argv):
  output_file = os.path.expanduser(argv[1])
  ds_key = argv[2]
  wund_key = argv[3]

  first = True
  last_ts = 0
  while True:
    ts = int(time.time())
     
    if ts == last_ts:
      time.sleep(1)
      continue

    if first or (ts % 120 == 0):
      # Update dark sky:
      print "updating ds"
      d = darksky.getWeather(key = ds_key)
      p = darksky.makeRainPlot(d)
      ds_json = json.dumps(p, indent = 2)
      last_ts = ts

    if first or (ts % 600 == 0):
      print "updating wu"
      print ts 
      # Update wunderground
      d = wunderground.getHourlyData(wund_key, 11201)
      p = wunderground.processHourlyData(d)
      wu_json = wunderground.makeStatusBoard(p)
      last_ts = ts

    # Every 5 seconds, cycle the plot data:
    if first or (ts % 15 == 0):
      print "%s | %s" % (last_ts, ts)
      last_ts = ts
      f = open(output_file, 'w')
      if ts % 2:
        print "wrote ds"
        f.write(ds_json)
      else:
        print "wrote wu"
        f.write(wu_json)
      f.close()
    first = False

if __name__ == "__main__":
  main(sys.argv)
