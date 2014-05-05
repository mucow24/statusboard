import txt_pb2
import gtfs_realtime_pb2
import urllib2
import time
import math
import logging

Uptown_Express_Track   = '4'
Uptown_Local_Track     = '3'
Downtown_Local_Track   = '2'
Downtown_Express_Track = '1'

def getData(key):
  Max_Tries = 30
  failed = False
  for i in range(Max_Tries):
    try:
      fetch_url = "http://datamine.mta.info/mta_esi.php?key=%s" % key
      logging.debug("Updating data: url: %s" % fetch_url)
      data = gtfs_realtime_pb2.FeedMessage()
      u = urllib2.urlopen(fetch_url)
      data.ParseFromString(u.read())
      if failed:
        logging.warn("Update successful.")
      return data
    except Exception as e:
      sleep_time = 5 
      logging.warn("Update failed: %s" % e)
      logging.debug("sleeping %s seconds." % sleep_time)
      time.sleep(sleep_time)

class Stop:
  def __init__(self, name, stop_ids):
    self.name     = name
    self.stop_ids = stop_ids
    self.arrivals = {}
    self.tracks   = []
  
  def __repr__(self):
    return "S[%s, %s, %s]" % (self.name, self.stop_ids, self.tracks)

  def addArrival(self, arrival):
    if arrival.track not in self.arrivals:
      self.arrivals[arrival.track] = []
      self.tracks.append(arrival.track)
      self.tracks.sort()
    self.arrivals[arrival.track].append(arrival)
    self.arrivals[arrival.track].sort()

  def arrivalsForTrack(self, track):
    return self.arrivals[track]

  def tracks(self):
    return self.tracks

class Arrival:
  def __init__(self, route_id, track, arrival_timestamp):
    self.route_id  = route_id
    self.track     = track
    self.timestamp = arrival_timestamp

  def __repr__(self):
    return "A[%s, %s, %s]" % (self.route_id, self.track, self.timestamp)

  def arrivalMin(self):
    return (self.timestamp - time.time()) / 60.

  def due(self):
    return (self.arrivalMin() < 1.0 and self.arrivalMin > -0.5)

  def elapsed(self):
    return (self.arrivalMin() < -0.5)

  def __lt__(self, other):
    return self.timestamp < other.timestamp

def getCh(d):
  ch = []
  for e in d.entity:
    if e.trip_update.IsInitialized():
      route_id = e.trip_update.trip.route_id
      for s in e.trip_update.stop_time_update:    
        if "137" in s.stop_id:
          ch.append( (route_id, s) )
  return ch


def loadStops(stops_filename):
  map = {}
  with open(stops_filename, 'rb') as f:
    while True:
      line = f.readline()
      if not line:
        break
      sp = line.split(',')
      stop_id = sp[0]
      name    = sp[1]
      map[stop_id] = name
  return map

def makeStops(data, stop_data):
  stop_map = {} 
  for e in data.entity:
    if e.trip_update.IsInitialized():
      # print e.trip_update
      route_id = e.trip_update.trip.route_id
      for s in e.trip_update.stop_time_update:
        # print s
        if s.Extensions[txt_pb2.nyct_stop_time_update].actual_track:
          track = s.Extensions[txt_pb2.nyct_stop_time_update].actual_track
        else:
          track = s.Extensions[txt_pb2.nyct_stop_time_update].scheduled_track

        stop_id = s.stop_id
        if 'N' in stop_id:
          stop_id = stop_id[:-1]
        elif 'S' in stop_id:
          stop_id = stop_id[:-1]

        stop_name = stop_data[stop_id]

        if stop_id not in stop_map:
          stop_map[stop_id] = Stop(stop_name, [stop_name])

        stop_map[stop_id].addArrival(Arrival(route_id, track, s.arrival.time))

  return stop_map

def routeToColor(route):
  if route in ('1', '2', '3'):
    return "#EE352E"
  elif route in ('4', '5', '6'):
    return "#00933C"
  elif route is '7':
    return "#B933AD"
  else:
    return "#808183"

def pruneArrivals(stop):
  valid_arrivals = {}
  for track in stop.tracks:
    if track not in valid_arrivals:
      valid_arrivals[track] = []
    arrivals = stop.arrivalsForTrack(track)
    # print "%-15s" % track,
    # num_printed = 0
    for arrival in arrivals:
      if not arrival.elapsed():
        valid_arrivals[track].append(arrival)
  return valid_arrivals

def printArrivals(stop, num_to_print=5):
  valid_arrivals = {}
  for track in stop.tracks:
    if track not in valid_arrivals:
      valid_arrivals[track] = []
    arrivals = stop.arrivalsForTrack(track)
    # print "%-15s" % track,
    # num_printed = 0
    for arrival in arrivals:
      if not arrival.elapsed():
        valid_arrivals[track].append(arrival)

  for track in stop.tracks:
    track_name = track
    if track == '1':
      track_name = "Downtown Lcl"
    elif track == '2':
      track_name = "Downtown Exp"
    elif track == '3':
      track_name = "Uptown Exp"
    elif track == '4':
      track_name = "Uptown Lcl"


    print "%-15s" % track_name,
  print

  for i in range(num_to_print):
    for track in stop.tracks:
      s = ""
      if track in valid_arrivals:
        if i < len(valid_arrivals[track]):
          arrival = valid_arrivals[track][i]
          s = "%1s - " % arrival.route_id
          if arrival.due():
            s = s + "DUE"
          else:
            s = s + "%2s min" % int(arrival.arrivalMin())
        
      print "%-15s" % s,
    print
