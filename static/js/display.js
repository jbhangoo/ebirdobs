var midGen = 1;
var markers = [];
var locLists = [];
var obsLayer = null;

var mymap;

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


function getCurrentLocation(curLoc, freeze) {
    mymap = L.map('mapid', {center: curLoc, zoom: 11, minZoom: 7, tap: false});
    // const curMarker = new L.circleMarker(curLoc,{radius: 20, color: 'red', weight: 3}).addTo(mymap);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    }).addTo( mymap );
    if (freeze) {
        mymap.dragging.disable();
        mymap.zoomControl.disable();
        mymap.doubleClickZoom.disable();
        mymap.scrollWheelZoom.disable();
        mymap.boxZoom.disable();
        mymap.keyboard.disable();
    } else {
        mymap.on('zoomend', getEbirdObs);
        mymap.on('dragend', getEbirdObs);
    }
    getEbirdObs();

    //new L.marker(curLoc, {icon: curIcon}).addTo(mymap);
    //display(observations);
}
function display(observations) {
    var obsTable = "<table class='fixed_header'><thead><tr><th>Common Name</th><th>Count</th><th>Days Ago</th>"
                    +"<th>Place</th><th>Reviewed</th><th>Verified</th></tr></thead><tbody>";

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
        if (!('obs' in locData))
            return;

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