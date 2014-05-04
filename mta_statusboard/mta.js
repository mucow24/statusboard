
  Data = null;

  function updateData() {
    var t = setTimeout( function () { updateData() }, 10000);
    var req = new XMLHttpRequest();
    req.overrideMimeType("application/json");

    req.onreadystatechange = function() {
      if (req.readyState == 4) { 
        var now = new Date();
        now = Math.floor(now.getTime() / 1000);
        Data = JSON.parse(req.responseText);
        age = now - Data.lastUpdateTime;
        console.log("data updated: age: " + Math.floor(age));
      }
    }
    req.open("GET", 'test.json', true);
    req.send(null);
  }

  Initial_Request_Sent = false;
  Table_Data = { 'station_rows' : [] };

  function init() {
    Num_Arrivals = 3;
    if (!Initial_Request_Sent) {
      console.log("initial req...");
      updateData();
      Initial_Request_Sent = true;
    }
    if (Data == null) {
      console.log("waiting...");
      var t = setTimeout( function () { init() }, 100);
      return;
    }
      
    var table = document.getElementById("arrTable");
    if (Data == null) {
      console.log('null');
    }
    if (table != null && Data != null) {
      var n_stations = Data.stationUpdates.length;
      for (var s = 0; s < n_stations; ++s) {
        update = Data.stationUpdates[s];
        var row = table.insertRow(-1);
        var dir_cell = row.insertCell(0);
        var name_cell = row.insertCell(-1);
        Table_Data.station_rows[s] = { 'name_cell'     : name_cell,
                                       'dir_cell'      : dir_cell,
                                       'arrival_cells' : [] };

        var dir = update.stationDirection;
        if (dir == "Uptown") {
          dir = "↑";
        } else if (dir == "Downtown") {
          dir = "↓";
        }
        dir_cell.innerHTML  = dir;
        dir_cell.setAttribute('class', 'dir_cell');
        name_cell.innerHTML = update.stationName;
        for (var a = 0; a < Num_Arrivals; ++a) {
          var a_cell = row.insertCell(-1);
          a_cell.style.width = "135px";
          var cell_span = document.createElement('span');
          a_cell.appendChild(cell_span);
          Table_Data.station_rows[s].arrival_cells[a] = { 'cell'         : a_cell,
                                                          'cell_span'    : cell_span,
                                                          'arr_str'      : ""};
        }
      }
    }
    updateArrivals();
  }

  function updateArrivals() {
    var table = document.getElementById("arrTable");
    if (table == null) {
      console.log("Table is null!?");
      return;
    }
    var now = new Date();
    now = Math.floor(now.getTime() / 1000);
    for (var s = 0; s < table.rows.length; ++s) {
      var srow    = Table_Data.station_rows[s];
      var supdate = Data.stationUpdates[s];

      // Find first arrival that's in the future:
      var arr_index;
      for (arr_index = 0; arr_index < supdate.stationArrivals.length; ++arr_index) {
        if (supdate.stationArrivals[arr_index].arrivalTime > now) {
          break;
        }
      }

      for (var a_i in srow.arrival_cells) {
        var arrival_cell = srow.arrival_cells[a_i]; 
        if (arr_index < supdate.stationArrivals.length) {
          var arrival = supdate.stationArrivals[arr_index];
          var route = arrival.arrivalRoute;
          var color = arrival.routeColor;
          var time  = arrival.arrivalTime;
          var time_delta = time - now;
          var update_delta = now - Data.lastUpdateTime;
          var min_str;
          var arr_color = "white";
          if (update_delta > 240) {
            arr_color = "red";
          } else if (update_delta > 120) {
            arr_color = "yellow";
          }
          if (time_delta < 60) {
            //console.log("td:" + time_delta);
            min_str = "DUE";
          } else {
            var minutes = Math.floor(time_delta / 60);
            //console.log("min: " + minutes);
            min_str = minutes + " min";
          }
          if (arrival_cell.arr_str != min_str) { 
            var next_cell = document.createElement('span');
            next_cell.setAttribute('class', 'slideInDown');
            var route_div = document.createElement('span');
            route_div.setAttribute('class', 'circle');
            route_div.style.background = color;
            route_div.innerHTML = route;
            var arr_span = document.createElement('span');
            arr_span.style.color = arr_color;
            arr_span.innerHTML = min_str;
            next_cell.appendChild(route_div);
            next_cell.appendChild(arr_span);

            arrival_cell.cell_span.style.color='white';
            arrival_cell.cell_span.setAttribute('class', 'slideOutDown');
            arrival_cell.arr_str = min_str;

            function makeListener(ac, nc) { 
              return function(e) {
                ac.cell_span.parentNode.replaceChild(nc, ac.cell_span);
                ac.cell_span = nc;
              }
            }
            arrival_cell.cell_span.addEventListener(
                "webkitAnimationEnd", makeListener(arrival_cell, next_cell), false);

            
          }
          ++arr_index;
        } else {
          arrival_cell.cell_span.setAttribute('class', 'slideOutDown');
          arrival_cell.cell_span.innerHTML = "";
        }
      }
    }
    var t = setTimeout( function () { updateArrivals() }, 500);
  }
  window.onload = init;

