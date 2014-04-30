import mta
import sys
import os
import time
import ConfigParser
import logging

Style_Header = '''
<style>
.circle {
  width:  30px;
  height: 30px;
  border-radius: 15px;
  line-height:   30px;
  text-align:    center;
  font-family: "Helvetica";
  font-weight: bold;
  font-size:   24px;
  white-space: nowrap;
  display:     inline-block;
  vertical-align: text-top;
}
</style>
'''

Script_Header = '''
<script>
  function updateArrivals() {
    var now = new Date();
    now = Math.floor(now.getTime() / 1000);
    update_delta = now - Last_Update;

    for (var s = 0; s < arrival_times.length; ++s) {
      var st_arrivals = arrival_times[s];
      for (var a = 0; a < st_arrivals.length; ++a) {
        var arrival_time = st_arrivals[a];
        var delta = st_arrivals[a] - now;
        var id = 'a' + s.toString() + a.toString();
        var estimate;
        if (delta < 0) {
          estimate = "GONE";
        } else if (delta < 60) {
          estimate = "DUE";
        } else {
          estimate = (Math.floor(delta / 60)).toString() + " min";
        }
        var e = document.getElementById(id);
        if (e != null) {
          e.innerHTML = estimate;
          if (update_delta > 120) {
            e.style.color = 'red';
          } else if (update_delta > 90) {
            e.style.color = 'yellow';
          }
        }
      }
    }
    var t = setTimeout( function () { updateArrivals() }, 500);
  }
  window.onload = updateArrivals()
</script>
'''



def log(string):
  print "%s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string)

def main(argv):
  if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
    print "Usage: %s ini_file" % argv[0]
    sys.exit(1)
  ini_file = argv[1]

  Defaults = {'update_interval_s' : '60',
              'log_level'         : 'INFO',
              'ugcs_refresh_s'    : '0',
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

  last_token_update_time = time.time()
  if ugcs_refresh_s:
    logging.info("Updating UGCS tokens")
    if os.system('kinit -R && aklog') != 0:
      logging.critical("UGCS token update failed!")

  while True:
    if ugcs_refresh_s:
      now = time.time()
      since = now - last_token_update_time
      if since > ugcs_refresh_s:
        logging.info("Updating UGCS tokens")
        if os.system('kinit -R && aklog') != 0:
          logging.critical("UGCS token update failed!")

    logging.debug("updating data...")
    d = mta.getData(mta_key)
    sd = mta.loadStops(stops_file)
    d = mta.makeStops(d, sd)
    logging.debug("writing table...")
    f = open(output_file, 'w')
    f.write(Style_Header)
    # Write out arrival timestamps:
    f.write("<script>\n")
    f.write("  Last_Update = %s;\n" % time.time())
    f.write("  arrival_times = [\n");
    for s in stations:
      arr = mta.pruneArrivals(d[s])
      uptown   = []
      downtown = []
      for track in arr:
        for i, arrival in enumerate(arr[track]):
          if i >= num_arrivals:
            break
          if track == '1' or track == '2':
            uptown.append( (arrival.timestamp, arrival.route_id) )
          else:
            downtown.append( (arrival.timestamp, arrival.route_id) )
      uptown.sort()
      downtown.sort()
      f.write("    [")
      for i in range(len(uptown)):
        if i != 0:
          f.write(", ")
        f.write("%s" % uptown[i][0])
      f.write("],\n")
      f.write("    [")
      for i in range(len(downtown)):
        if i != 0:
          f.write(", ")
        f.write("%s" % downtown[i][0])
      f.write("],\n")
    f.write("  ];\n")
    f.write("</script>\n")
    
    f.write(Script_Header)
    f.write("<table>\n")
    s_ctr = 0
    for s in stations:
      arr = mta.pruneArrivals(d[s])
      name = d[s].name
      uptown = []
      downtown = []
      for track in arr:
        for i, arrival in enumerate(arr[track]):
          if i >= num_arrivals:
            break
          if track == '1' or track == '2':
            uptown.append( (arrival.timestamp, arrival.route_id) )
          else:
            downtown.append( (arrival.timestamp, arrival.route_id) )
      uptown.sort()
      downtown.sort()
      f.write("  <tr>\n")
      f.write("    <td> %s Up</td>\n" % name)
      a_ctr = 0
      for t, r in uptown:
        color = mta.routeToColor(r)
        f.write("    <td style='width:150px'>\n")
        f.write("      <div class='circle' style='background:%s'>\n" % color)
        f.write("        %s\n" % r)
        f.write("      </div>\n")
        f.write("      <span id='a%s%s'></span>\n" % (s_ctr, a_ctr))
        f.write("    </td>\n")
        a_ctr = a_ctr + 1
      f.write("  </tr>\n")

      f.write("  <tr>\n")
      f.write("    <td> %s Down</td>\n" % name)
      a_ctr = 0
      s_ctr = s_ctr + 1
      for t, r in downtown:
        color = mta.routeToColor(r)
        f.write("    <td style='width:150px'>\n")
        f.write("      <div class='circle' style='background:%s'>\n" % color)
        f.write("        %s\n" % r)
        f.write("      </div>\n")
        f.write("      <span id='a%s%s'></span>\n" % (s_ctr, a_ctr))
        f.write("    </td>\n")
        a_ctr = a_ctr + 1
      f.write("  </tr>\n")
      s_ctr = s_ctr + 1
    f.write("</table>\n")
    f.close()
    logging.debug("done")
    time.sleep(update_interval_s)

if __name__ == "__main__":
  main(sys.argv)
