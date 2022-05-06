
var updateTimer = setInterval(update, 5*1000);

// Submit HTTP POST for update to the grid
function update() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
    try {
        processUpdate(this.responseText);
     } catch (e) {
        document.getElementById("status").innerHTML = '';
     }
    };
    xhttp.open("POST", "/update/");
    xhttp.send();
}

var cell_grid;
function processUpdate(content) {
    const output = JSON.parse(content)

    const first_day = output['day'][0];
    const last_day = output['day'][1];
    const last_grid = output['grid'];
    cell_grid = last_grid;
    //processGrid();

    document.getElementById("stdout").innerHTML = output['stdout'];

    let errors = output['stderr'];
    if (errors === '')
        errors = "No errors";
    document.getElementById("stderr").innerHTML = errors;

    // If simulation finished
    if (output['stdout'].includes("finished")) {
        // Disable update timer
        clearInterval(updateTimer);
        window.location.assign('/geotiff');

        // Indicate status = Completed
        document.getElementById("iWait").src = "/static/img/please-wait.gif";
        document.getElementById("status").innerHTML = "<span style='color:green;font-weight:bold;'>Completed</span>"+
                            "<div style='font-weight:bold;'>Please wait for map to load</div>";
        // Display entire timeline
       /* const selt = document.getElementById("dayslider");
        selt.min = first_day;
        selt.max = last_day;
        selt.value = last_day;
        document.getElementById("slidervalue").innerHTML = last_day;
        const melt = document.getElementById("mapcontrols");
        melt.style = "width:100%;visibility:visible;";'*/
    } else {
        document.getElementById("status").innerHTML = `Currently at day ${last_day-first_day+1}\n\n`;;
    }
}

var cellDetails;
function processGrid() {
    let x = [];
    let y = [];
    cellDetails = new Array();
    for (const pixel in cell_grid) {
        const h = pixel % GRID_WIDTH;
        const v = Math.floor(pixel / GRID_WIDTH);
        const cell = cell_grid[pixel];
        if (typeof cellDetails[h] === 'undefined') {
            cellDetails[h] = new Array();
        }
        if (typeof cellDetails[h][v] === 'undefined') {
            cellDetails[h][v] = new Array();
        }
        cellDetails[h][v]['total'] = 0;
        for (const state in cell) {
            cellDetails[h][v]['total'] = 0;
            cellDetails[h][v][state] = 0;
            for (const age in cell[state]) {
                if (age != 'NA') {
                    cellDetails[h][v]['total'] += cell[state][age];
                    cellDetails[h][v][state] += cell[state][age];
                }
            }
        }
        x.push(h);
        y.push(v);
    }
    document.getElementById("mapinfo").innerHTML = x.length.toString();
    drawMap(x, y, cellDetails);
}

function onSliderChange() {
    const daySelected = document.getElementById("dayslider").value;
    var melt = document.getElementById("mapcontrols");
    melt.style = "width:100%;visibility:hidden;";
    document.getElementById("slidervalue").innerHTML = daySelected;
    getResults(daySelected);
}

function onListChange() {
    const daySelected = document.getElementById("dayslider").value;
    var melt = document.getElementById("mapcontrols");
    melt.style = "width:100%;visibility:hidden;";
    document.getElementById("slidervalue").innerHTML = daySelected;
    getResults(daySelected);
}

// Submit HTTP GET grid for particular day of the simulation
function getResults(day) {
    document.getElementById("mapinfo").innerHTML = "Redrawing...";
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        processResults(this.responseText);
    };
    xhttp.open("GET", `/getGrid?day=${day}`);
    xhttp.send();
}

function processResults(grid) {
        cell_grid = JSON.parse(grid);
        processGrid();
        var melt = document.getElementById("mapcontrols");
        melt.style = "width:100%;visibility:visible;";
}

