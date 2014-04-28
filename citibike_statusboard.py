import citibike
import sys
import os
import time

def log(string):
  print "%s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string)

def main(argv):
  output_file = os.path.expanduser(argv[1])
  stations = argv[2:]
  map(int, stations)
  while True:
    log("Updating stations: %s" % stations)
    f = open(output_file, 'w')
    d = citibike.getData()
    f.write("60%,20%,20%\n")
    f.write("Station,Bikes,Docks\n")
    for station in stations:
      sd = citibike.getStationData(d, station)
      bikes = sd['availableBikes']
      docks = sd['availableDocks']
      name  = sd['stationName']
      name = name.replace(" & ", "/")
      name = name.replace("St", "")
      f.write("%s,%s,%s\n" % (name, bikes, docks))
    f.close()
    time.sleep(120)


if __name__ == "__main__":
  main(sys.argv)
