import mta
import sys
import os
import time

def log(string):
  print "%s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string)

def main(argv):
  output_file = os.path.expanduser(argv[1])
  key         = argv[2]
  stops_file  = argv[3]
  stations    = argv[4:]

  Max_Arrivals = 3

  while True:
    d = mta.getData(key)
    d = mta.makeStops(d)
    sd = mta.loadStops(stops_file)
    f = open(output_file, 'w')
    f.write("50%,50%\n")
    for s in stations:
      arr = mta.pruneArrivals(d[s])
      name = sd[s]
      uptown = []
      downtown = []
      for track in arr:
        for i, arrival in enumerate(arr[track]):
          if i >= Max_Arrivals:
            break
          if track == '1' or track == '2':
            uptown.append(int(arrival.arrivalMin()))
          else:
            downtown.append(int(arrival.arrivalMin()))
      uptown.sort()
      downtown.sort()
      f.write("%s [Uptown]," % name)
      f.write("\"%s min" % uptown[0])
      for a in uptown[1:]:
        f.write(", %s min" % a)
      f.write("\"\n")
      f.write("%s [downtown]," % name)
      f.write("\"%s min" % downtown[0])
      for a in downtown[1:]:
        f.write(", %s min" % a)
      f.write("\"\n")
    print "done"
    time.sleep(30)

if __name__ == "__main__":
  main(sys.argv)
