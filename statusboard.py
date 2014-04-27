import json

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

class Graph(object):
  Types = enum(LINE="line", BAR="bar")

  def __init__(self, title=""):
    self._datasequences = []
    self._title = title
    self._refresh = 120
    self._show_totals = False
    self._graph_type  = Graph.Types.LINE
    self._ymin = None
    self._ymax = None
    self._prefix = None
    self._suffix = None
    self._scale_to = 0
    self._showX    = True
    self._showY    = True

  @property
  def title(self):
    return self._title

  @title.setter
  def title(self, title):
    self._title = title

  def setLimits(self, ymin=None, ymax=None):
    self._ymin = ymin
    self._ymax = ymax

  @property
  def graphType(self):
    return self._graph_type

  @graphType.setter
  def graphType(self, gtype):
    self._graph_type = gtype
  
  @property
  def showTotals(self):
    return self._show_totals

  @showTotals.setter
  def showTotals(self, value):
   self._show_totals = value 

  @property
  def prefix(self):
    return self._prefix

  @prefix.setter
  def prefix(self, value):
   self._prefix = value 

  @property
  def suffix(self):
    return self._suffix

  @suffix.setter
  def suffix(self, value):
   self._suffix = value 

  def addDatasequence(self, sequence):
    self._datasequences.append(sequence)

  @property
  def datasequences(self):
    return self._datasequences

  @property
  def scaleTo(self):
    return self._scale_to

  @scaleTo.setter
  def scaleTo(self, value):
    self._scale_to = value

  def showAxes(xaxis = True, yaxis = True):
    self._showX = xaxis
    self._showY = yaxis

  def render(self):
    ret = {}
    ret['graph'] = {}
    graph = ret['graph']
    graph['title'] = self.title
    graph['total'] = self.showTotals
    graph['type']  = self.graphType
    graph['yAxis'] = {'scaleTo' : self.scaleTo,
                      'hide'    : self._showY }
    if self._ymin:
      graph['yAxis']['minValue'] = self._ymin
    if self._ymax:
      graph['yAxis']['maxValue'] = self._ymax
    if self._prefix or self._suffix:
      if 'units' not in graph['yAxis']:
        graph['yAxis']['units'] = {}
        if self._prefix:
          graph['yAxis']['units']['prefix'] = self._prefix
        if self._suffix:
          graph['yAxis']['units']['suffix'] = self._suffix
    graph['xAxis'] = {'hide' : self._showX}
    graph['datasequences'] = []
    for ds in self._datasequences:
      graph['datasequences'].append(ds.render())

    return ret

    
class DataSequence(object):
  Colors     = enum(RED="red", 
                    BLUE="blue",
                    GREEN="green",
                    YELLOW="yellow",
                    ORANGE="orange",
                    PURPLE="purple",
                    AQUA="aqua",
                    PINK="pink")
  def __init__(self, title=""):
    self._title      = title
    self._color      = DataSequence.Colors.RED 
    self._datapoints = []

  @property
  def title(self):
    return self._title
  
  @title.setter
  def title(self, title):
    self._title = title

  def addDatapoint(self, name, value):
    self._datapoints.append((name, value))

  @property
  def datapoints(self):
    return self._datapoints

  def render(self):
    ret = {}
    ret['title'] = self.title
    ret['color'] = self.color
    ret['datapoints'] = []
    for name, value in self.datapoints:
      ret['datapoints'].append( {'name' : name, 'value' : value} )
    return ret
