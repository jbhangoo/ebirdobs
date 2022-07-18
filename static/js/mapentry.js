var midGen = 1;
var markers = [];
var locLists = [];
var obsLayer = null;
var curLoc;
var curMarker;

// User location marker
const curIcon = L.icon({
    iconUrl: '/static/img/plus2.png',
    iconSize:     [16, 16], // size of the icon
    iconAnchor:   [8, 8], // point of the icon which will correspond to marker's location
});

const obsIcon = L.icon({
    iconUrl: '/static/img/blue-square.png',
    iconSize:     [16, 16], // size of the icon
    iconAnchor:   [8, 8], // point of the icon which will correspond to marker's location
});

function onMapChanged() {
    document.getElementById("obstable").innerHTML = "";

    const northwest = mymap.getBounds().getNorthWest();
    const southeast = mymap.getBounds().getSouthEast();
    const dist = northwest.distanceTo(southeast);
    const diam = parseInt(Math.abs(dist));

    const center = mymap.getCenter();
    const lat = center.lat;
    const lon = center.lng;

    // To loading the jQuery code "https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"
    const url = `/load?lat=${lat}&lon=${lon}&diam=${diam}&days=7`;
    fetch(url)
        .then(function (response) {
            response.json().then(function (observations) {
                display(observations);
            });
        });

    document.getElementById("status").innerHTML = "Data for selected point";
}

function display(observations) {
    var obsTable = "<table class='fixed_header'><thead><tr><th>Common Name</th><th>Count</th><th>Days Ago</th>"
                    +"<th>Place</th><th>R</th><th>V</th></tr></thead><tbody>";

    if (obsLayer !== null)
    {
        obsLayer.remove();
        obsLayer = null;
    }

    locLists = [];
    markers = [];
    midGen = 0;
    for (const locId in observations)
    {
        if (locId === 'Error') {
            document.getElementById("status").innerHTML = observations[locId];
            return;
        }
        const locData = observations[locId];
        const locName = locData['locationPrivate']?"!PVT! ":"" + locData['name'];
        const coords = locData['coords'];

        const oidx = (midGen+1).toString();

        let locList = `<h4>${locName}</h4>`;
        let specieslist = new Set();
        for (const obsDate in locData['obs'])
        {
            const today = new Date();
            const odate = new Date(obsDate);
            const delta = Math.ceil( (odate - today) / (1000 * 60 * 60 * 24) );

            let chklist = new Set();
            locList += `<h6>${obsDate}</h6><ul>`;
            for (const species in locData['obs'][obsDate])
            {
                const speciesData = locData['obs'][obsDate][species];
                const reviewed = speciesData['reviewed'] ? "&#10004":"";
                const valid = speciesData['valid'] ? "&#10004":"";
                let spCount = speciesData['count'];
                if (isNaN(spCount))
                    spCount = '?';
                obsTable += `<tr onclick="onTableClick(${midGen})" >`;
                obsTable += `<td>${species}</td><td>${spCount}</td><td>${delta}</td>`;
                obsTable += `<td>${locData['name']}</td><td>${reviewed}</td><td>${valid}</td>`;
                obsTable += "</tr>";
                locList += `<li>${species}&nbsp;${spCount}</li>`;
                specieslist.add(species);
                chklist.add(speciesData['checklist']);
            }
            locList += "</ul>";
            chklist.forEach(async (chk) => {
                locList += `<a href='https://ebird.org/checklist/${chk}' target='_blank'>${chk}</a><br>`;
            })
        }

        locLists.push(locList);
        const speciesCount = locName.slice(0,11) + ':' + specieslist.size.toString();
        let marker = new L.marker(coords, {icon: obsIcon, mid: midGen});
        marker.bindTooltip(speciesCount,
            {
                permanent: true,
                direction: 'top'
            });
        //marker.bindPopup(locName);
        marker.on('mouseover', onLocClick);
        markers.push(marker);
        midGen++;
    }

    obsTable += "</tbody></table>";
    const obsElt = document.getElementById("obstable");
    obsElt.innerHTML = obsTable;

    obsLayer = L.featureGroup(markers);
    obsLayer.addTo(mymap);
    //mymap.fitBounds(obsLayer.getBounds());
}

function onLocClick(e) {
    const mid = e.target.options.mid;
    const locList = locLists[mid];
    const locElt = document.getElementById("loclist");
    locElt.innerHTML = locList;
}

function onTableClick(mid) {
    const curLoc = markers[mid].getLatLng();
    curMarker.setLatLng(curLoc);
}

function getCurrentLocation() {
  curLoc = L.latLng(32.2102866,-110.9235907);
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {curLoc = L.latLng(pos.coords.latitude , pos.coords.longitude);});
  } else {
    document.getElementById("status").innerHTML = "Geolocation is not supported by this browser.";
  }
}

getCurrentLocation();
var mymap = L.map('mapid', {center: curLoc, zoom: 11, minZoom: 7, tap: false});
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
}).addTo( mymap );
mymap.on('zoomend', onMapChanged);
mymap.on('dragend', onMapChanged);

curMarker = new L.circleMarker(curLoc,{radius: 20, color: 'red', weight: 3}).addTo(mymap);
 //new L.marker(curLoc, {icon: curIcon}).addTo(mymap);
display(observations);

/*
comName: "Acorn Woodpecker"
howMany: "1"
lat: "32.2102866"
lng: "-110.9235907"
locId: "L227274"
locName: "Reid Park"
locationPrivate: "False"
obsDt: "2022-04-09 06:58"
obsReviewed: "True"
obsValid: "True"
sciName: "Melanerpes formicivorus"
speciesCode: "acowoo"
subId: "S106597397"
*/

