
function getEbirdObs() {
    document.getElementById("obstable").innerHTML = "";

    const northwest = mymap.getBounds().getNorthWest();
    const southeast = mymap.getBounds().getSouthEast();
    const dist = northwest.distanceTo(southeast);
    const diam = parseInt(Math.abs(dist));

    const center = mymap.getCenter();
    const lat = center.lat;
    const lon = center.lng;
    const rare = document.getElementById('flexRare').checked?"r":"";

    // To loading the jQuery code "https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"
    const url = `/ebirdobs?lat=${lat}&lon=${lon}&diam=${diam}&days=7&rare=${rare}&species=`;
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

function onTableClick(mid) {
    const curLoc = markers[mid].getLatLng();
    curMarker.setLatLng(curLoc);
}


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

