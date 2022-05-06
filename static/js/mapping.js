// Grid constants for geographic conversion
const MAP_LIMITS = {
    'xmin' :-15,
    'xmax' : -7.65,
    'ymin' : 7,
    'ymax' : 12.7
};

const GRID_WIDTH = 147;
const GRID_HEIGHT = 114;

const DEGREES_PER_PIXEL_X = (MAP_LIMITS['xmax'] - MAP_LIMITS['xmin']) / GRID_WIDTH;
const DEGREES_PER_PIXEL_Y = (MAP_LIMITS['ymax'] - MAP_LIMITS['ymin']) / GRID_HEIGHT;

// Leaflet Map
const topleft = L.latLng(12.7, -15);
const botright = L.latLng(7, -7.65);
const midpt = L.latLng(10, -11);
const bounds = L.latLngBounds(topleft, botright);
var mymap = L.map('geo', {zoomSnap:1, minZoom:6}).fitBounds(bounds);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
}).addTo( mymap );

// Layer for simulated results plot
var simLayer = L.layerGroup().addTo(mymap);

function minmax(arr) {
    let min = Infinity;
    let max = 0;
    for (const x in arr) {
        const row = arr[x];
        for (const y in row) {
            const cell = row[y];
            min = (cell < min) ? cell : min;
            max = (cell > max) ? cell : max;
        }
    }
    return {'min':min, 'max':max};
}

function drawMap(x, y, cells) {
    simLayer.clearLayers();

    const poptype = document.getElementById('poplist').value;

    // Sum up all states per cell that contain the requested population type
    const populations = cells.map( function( row ) {
        return row.map( function( cell ) {
            // Need to test each state since they are not mutually exclusive
            let statepop = 0;
            for (const state in cell) {
                if (state.indexOf(poptype) >= 0) {
                    statepop += cell[state];
                }
            }
            return parseInt( statepop );
        } );
    } );
    const totals = cells.map( function( row ) {
        return row.map( function( cell ) {
            return parseInt( cell['total'] );
        } );
    } );

    try {
        for (var i=0; i<x.length; i++) {
            const lon = MAP_LIMITS['xmin'] + x[i] * DEGREES_PER_PIXEL_X;
            const lat = MAP_LIMITS['ymax'] - y[i] * DEGREES_PER_PIXEL_Y;
            let mapval = populations[x[i]][y[i]];
            const opt = getMarkerOptions(mapval, minmax(populations));
            const gridcell = getCellPolygon(x[i], y[i], opt);
            gridcell.x = x[i];
            gridcell.y = y[i];
            gridcell.on('click', onMarkerClick);
            gridcell.bindTooltip(`(${lat.toFixed(2)},${lon.toFixed(2)}): ${mapval.toFixed(1)}`);
            gridcell.addTo(simLayer);
        }
        document.getElementById("mapinfo").innerHTML = "Showing "+document.getElementById(poptype).innerHTML;
    } catch (error) {
        document.getElementById("mapinfo").innerHTML = error;
    }
}

function getCellPolygon(x, y, options) {
    const startLat = MAP_LIMITS['ymax'] - y * DEGREES_PER_PIXEL_Y;
    const startLon = MAP_LIMITS['xmin'] + x * DEGREES_PER_PIXEL_X;
    const ul = [startLat, startLon];
    const ll = [startLat-DEGREES_PER_PIXEL_Y, startLon];
    const ur = [startLat, startLon+DEGREES_PER_PIXEL_X];
    const lr = [startLat-DEGREES_PER_PIXEL_Y, startLon+DEGREES_PER_PIXEL_X];
    var cell = new L.Polygon([ll, ul, ur, lr], options);
    return cell;
}

function onMarkerClick(e) {
    let infected = 0;
    let vaccinated = 0;
    let population = 0;
    const states = cellDetails[e.target.x][e.target.y];
    // Sum each relevant class over all ages
    // Classes are NOT EXCLUSIVE so check for string within every state
    for (const state in states) {
        if ((state.includes('I1')) || (state === 'I')) {
            infected += states[state];
        }
        if (state.includes('I2')) {
            vaccinated += states[state];
        }
        if (state === 'total') {
            population = states[state];
        }
    }
    document.getElementById("mapinfo").innerHTML=`Infected=${infected} Vaccinated=${vaccinated}  Total=${population}`;
}

function getMarkerOptions(level, minmax) {
    const minLevel = minmax['min'];
    const maxlevel = minmax['max'];
    const mcolor = score2color(level, minLevel, maxlevel);
    return {
        radius: 1,
        fillColor: mcolor,
        color: mcolor,
        weight: 1,
        opacity: 0.6,
        fillOpacity: 0.6
    };
}

function score2color(score, min, max) {
    var base = (max - min);

    if (base == 0) { score = 100; }
    else {
        score = (score - min) / base * 100;
    }
    var r, g, b = 0;
    if (score < 50) {
        g = 255;
        r = Math.round(5.1 * score);
    }
    else {
        r = 255;
        g = Math.round(510 - 5.10 * score);
    }
    var h = r * 0x10000 + g * 0x100 + b * 0x1;
    return '#' + ('000000' + h.toString(16)).slice(-6);
}
