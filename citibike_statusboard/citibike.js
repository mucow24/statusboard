
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
    req.open("GET", 'citibike.json', true);
    req.send(null);
  }

  Initial_Request_Sent = false;
  Table_Data = { 'station_rows' : [] };

  function init() {
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
      var n_stations = Data.stationData.length;
      for (var s = 0; s < n_stations; ++s) {
        sd = Data.stationData[s];
        var row = table.insertRow(-1);
        var name_cell = row.insertCell(0);
        var name_span = document.createElement('span');
        name_span.setAttribute('class', 'name');
        name_cell.appendChild(name_span);

        var bike_cell = row.insertCell(-1);
        var bike_span = document.createElement('span');
        bike_span.setAttribute('class', 'bike');
        bike_cell.appendChild(bike_span);
        var bike_img = document.createElement('img');
        bike_img.src = "bike.svg";
        bike_cell.appendChild(bike_img);
        bike_cell.setAttribute('class', 'bike_cell');

        var dock_cell = row.insertCell(-1);
        var dock_span = document.createElement('span');
        dock_span.setAttribute('class', 'dock');
        dock_cell.appendChild(dock_span);
        var dock_img = document.createElement('img');
        dock_img.src = "dock.png";
        dock_cell.appendChild(dock_img);
        dock_cell.setAttribute('class', 'dock_cell');

        Table_Data.station_rows[s] = { 'name_span'     : name_span,
                                       'bike_span'     : bike_span,
                                       'dock_span'     : dock_span};

        name_cell.innerHTML  = sd.name;
      }
      update();
    }
  }

  function update() {
    var table = document.getElementById("arrTable");
    if (table == null) {
      console.log("Table is null!?");
      return;
    }
    var now = new Date();
    now = Math.floor(now.getTime() / 1000);
    for (var s = 0; s < table.rows.length; ++s) {
      var srow    = Table_Data.station_rows[s];
      var supdate = Data.stationData[s];
      var update_delta = now - Data.lastUpdateTime;
      var data_color = 'white';
      if (update_delta > 480) {
        data_color = "red";
      } else if (update_delta > 240) {
        data_color = "yellow";
      }
      srow.bike_span.innerHTML = supdate.bikes;
      srow.bike_span.style.color = data_color;

      srow.dock_span.innerHTML = supdate.docks;
      srow.dock_span.style.color = data_color;
    }
    var t = setTimeout( function () { update() }, 5000);
  }

  window.onload = init;

