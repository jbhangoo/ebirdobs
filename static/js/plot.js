const AGES = [0, 1, 2];
const STATES = {'I':'Infected', 'I1':'Infected', 'I2':'Vaccinated'};

let plotData = new Array();

// Submit HTTP GET timeline of populations for a pixel
function getTimeline(pixel) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        processTimeline(this.responseText);
    };
    xhttp.open("GET", `/getTimeline?pixel=${pixel}`);
    xhttp.send();
}

function processTimeline(timeline) {
    try {
        document.getElementById("status").innerHTML = "";
        plotTimeline(JSON.parse(timeline));
    } catch {
        document.getElementById("status").innerHTML = "Timeline error detected";
    }
}

function plotTimeline(timeline) {
    let infected = [];
    let vaccinated = [];
    let totals = [];
    const days = Object.keys(timeline);
    const first_day = Math.min(...days);
    days.map(day => {
        infected[day] = 0;
        vaccinated[day] = 0;
        totals[day] = 0;
    });
    for (const day in timeline) {
        const populations = timeline[day];
        // Turn populations into parallel arrays of day numbers and values
        const states = Object.keys(populations);

        // Update arrays
        for (const i in states) {
            const state = states[i];

            if ((state.includes('I1')) || (state === 'I')) {
                infected[day] += populations[state];
            }
            if (state.includes('I2')) {
                vaccinated[day] += populations[state];
            }
            totals[day] += populations[state];
        }
    }

    // Plot arrays
    const x = Object.keys(totals).map(k=>parseInt(k)-first_day);
    if (x.length == 0) {
        document.getElementById("status").innerHTML = "NOTE: Point is outside simulation area";
        Plotly.newPlot('plot', [], {});
        return;
    }
    const trace1 = {
        x: x,
        y: Object.values(infected),
        name: `Infected`,
        type: 'scatter',
        mode: 'lines'
    };
    const trace2 = {
        x: x,
        y: Object.values(vaccinated),
        name: `Vaccinated`,
        type: 'scatter',
        mode: 'lines',
        line: {
            dash: 'dot',
            width: 4
          }
    };
    const trace3 = {
        x: x,
        y: Object.values(totals),
        name: `Tot Pop`,
        type: 'scatter',
        mode: 'lines',
        line: {
            dash: 'dash',
            width: 2
          }
    };
    const traces = [trace1, trace2, trace3];

    const layout = {
      title: 'Population trends',
      xaxis: {
        title: 'Day',
      },
      yaxis: {
        title: 'Population'
      },
      margin: { l: 50,
                r: 5,
                b: 30,
                t: 125,
                pad:1},
      legend: {x: 0.2, y: 1.2}
    };

    let modeBarButtons = [[ "toImage", "hoverClosestCartesian", "hoverCompareCartesian" ]];
    Plotly.newPlot('plot', traces, layout, {modeBarButtons: modeBarButtons, responsive: true});
}