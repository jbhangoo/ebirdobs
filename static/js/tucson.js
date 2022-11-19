function onChange() {
    const daySelected = document.getElementById("sDays").value;
    const speciesSelected = document.getElementById("ddlSpecies").value;
    getResults(daySelected, speciesSelected);
}

function getEbirdObs() {
    document.getElementById("obstable").innerHTML = "";
    getResults(30, '');
}

// Submit HTTP GET grid for particular day of the simulation
function getResults(day, species) {
    const lat = 32.2;
    const lon = -110.9;
    const diam = 45*1000;
    const url = `/ebirdobs?lat=${lat}&lon=${lon}&diam=${diam}&days=${day}&species=${species}`;
    fetch(url)
        .then(function (response) {
            response.json().then(function (observations) {
                display(observations);
            });
        });
}

function onLocClick(e) {
    const mid = e.target.options.mid;
    const locList = locLists[mid];
    const locElt = document.getElementById("loclist");
    locElt.innerHTML = locList;
}

// Automatically update every 15 minutes
var updateTimer = setInterval(update, 15*60*1000);

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

    document.getElementById("stdout").innerHTML = output['stdout'];

    let errors = output['stderr'];
    if (errors === '')
        errors = "No errors";
    document.getElementById("stderr").innerHTML = errors;
}


