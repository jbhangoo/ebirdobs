from geopy.distance import geodesic
import json
import requests

from src.species import SpeciesCounts

class EbirdApi(object):
    def __init__(self, args):
        self.EBBaseURL = "https://api.ebird.org/v2/"
        self.EBApiKey = "h91aejb6l1hs"
        self.observationsJson = self.getEbirdObservations(
            args['lat'],
            args['lon'],
            args['region'],
            args['radius'],
            args['days'],
            args['notable'],
            args['species']
        )
        self.observations = json.loads(self.observationsJson)
        self.locSpecies = SpeciesCounts(self.observations)
        try:
            self.locSpeciesJson = json.dumps(self.locSpecies.locations)
        except Exception as ex:
            self.locSpeciesJson = json.dumps({"Error": str(ex)})

    def HttpGet(self, uri: str):
        ebird_header = {"X-eBirdApiToken": self.EBApiKey }
        resp = requests.get(uri, headers=ebird_header)

        if resp.status_code == 200:
            return resp.content
        else:
            return "Error: {}".format(resp.status_code)


    def HttpGetEbird(self, service:str, args:dict):
            url = self.EBBaseURL + EBServices[service]
            # Insert actual arguments for the tokens
            for akey,aval in args.items():
                url = url.replace("{{" + akey + "}}", str(aval))

            got = self.HttpGet(url)
            return got

    def getEbirdSpecies(self, speciesCode):
            ebcode = EBSpeciesCodes[speciesCode]
            species_url = "https://api.ebird.org/v2/ref/taxonomy/ebird?species={}&fmt=json".format(ebcode)
            return self.HttpGet(species_url)

    def getEbirdObservations(self, lat, lon, region:str, radius, days, notable, species):

            if species:
                ebcode = EBSpeciesCodes[species]
                args = { "lat": lat , "lng": lon , "speciesCode": ebcode , "dist": radius , "back": days }
                jsonResponse = self.HttpGetEbird("locationObservationsSpecies", args)
            elif notable == "r":
                args = { "lat": lat , "lng": lon , "dist": radius , "back": days }
                jsonResponse = self.HttpGetEbird("locationObservationsNotable", args)
            elif notable == "s":
                args = { "lat": lat , "lng": lon , "regionCode": "US-"+region[0:2] , "maxResults": "50", "back": days }
                jsonResponse = self.HttpGetEbird("regionObservationsNotable", args)
            elif notable == "c":
                args = { "lat": lat , "lng": lon , "regionCode": "US-"+region , "maxResults": "50", "back": days }
                jsonResponse = self.HttpGetEbird("regionObservationsNotable", args)
            elif notable == "e":
                args= { "lat": lat , "lng": lon , "regionCode": "US-"+region , "maxResults": "50", "back": days }
                jsonResponse = self.HttpGetEbird("regionObservations", args)
            else:
                args = { "lat": lat , "lng": lon , "dist": radius , "back": days, "maxResults": "50" }
                jsonResponse = self.HttpGetEbird("locationObservations", args)
            return jsonResponse


    def getEbirdChecklists(self, regionCode, txtLat, txtLon, radius):
        '''
        Returns a list of EbirdChecklist
        '''
        if regionCode:
            args = { "regionCode": "US-"+regionCode, "maxResults": "100" }
            jsonResponse = self.HttpGetEbird("regionChecklists", args)
            ListofChecklists = []
            for response in json.loads(jsonResponse):
                ListofChecklists.append(EbirdChecklist(response))

            maxRadius = float(radius) * 1000 # Convert to meters
            sLatitude = float(txtLat)
            sLongitude = float(txtLon)
            sCoord = (sLatitude, sLongitude)
            for chklist in ListofChecklists:
                eLatitude = chklist.loc.latitude
                eLongitude = chklist.loc.longitude
                eCoord = (eLatitude, eLongitude)

                cdist = geodesic(sCoord, eCoord).km
                if cdist < maxRadius:
                    ListofChecklists.append(chklist)
                if len(ListofChecklists) > 20:
                    return ListofChecklists
            return ListofChecklists
        else:
            return []


EBServices = {
                 "speciesCode": "ref/taxonomy/ebird/species",
                 "locationHotspot": "ref/hotspot/geo?lat={{lat}}&lng={{lng}}",
                 "locationObservations": "data/obs/geo/recent?lat={{lat}}&lng={{lng}}&dist={{dist}}&back={{back}}&maxResults={{maxResults}}",
                 "locationObservationsSpecies": "data/obs/geo/recent/speciesCode?lat={{lat}}&lng={{lng}}&dist={{dist}}&back={{back}}",
                 "locationObservationsNotable": "data/obs/geo/recent/notable?lat={{lat}}&lng={{lng}}&dist={{dist}}&back={{back}}",
                 "regionHotspots": "ref/hotspot/regionCode",
                 "regionSpecies": "product/spplist/regionCode",
                 "regionChecklists": "product/lists/regionCode?maxResults={{maxResults}}" ,
                 "regionInfo": "ref/region/info/regionCode",
                 "regionObservations": "data/obs/regionCode/recent?maxResults={{maxResults}}&back={back}",
                 "regionObservationsSpecies": "data/obs/regionCode/recent/speciesCode",
                 "regionObservationsNotable": "data/obs/regionCode/recent/notable?maxResults={{maxResults}}&back={{back}}"
            }

EBSpeciesCodes = {
            "cago": "cangoo",
            "wodu": "wooduc",
            "mall": "mallar3",
            "nopi": "norpin",
            "agwt": "gnwtea",
            "canv": "canvas",
            "redh": "redhea",
            "rndu": "rinduc",
            "lesc": "lessca",
            "buff": "buffle",
            "home": "hoomer",
            "come": "commer",
            "rudu": "rudduc",
            "scqu": "scaqua",
            "gaqu": "gamqua",
            "mtzq": "monqua",
            "legr": "leagre",
            "pbgr": "pibgre",
            "eagr": "eargre",
            "wegr": "wesgre",
            "clgr": "clagre",
            "rodo": "rocpig",
            "eucd": "eucdov",
            "ritd": "eucdov",
            "indo": "incdov",
            "cogd": "cogdov",
            "wwdo": "whwdov",
            "modo": "moudov",
            "grro": "greroa",
            "ybcu": "yebcuc",
            "leni": "lesnig",
            "copw": "compoo",
            "vasw": "vauswi",
            "wtsw": "whtswi",
            "bchu": "bkchum",
            "anhu": "annhum",
            "cohu": "coshum",
            "bthu": "brthum",
            "ruhu": "rufhum",
            "cahu": "calhum",
            "bblh": "brbhum",
            "vira": "virrai",
            "sora": "sora",
            "como": "comgal1",
            "amco": "y00475",
            "bnst": "bknsti",
            "amav": "ameavo",
            "kill": "killde",
            "stsa": "stisan",
            "basa": "baisan",
            "lesa": "leasan",
            "pesa": "pecsan",
            "wesa": "wessan",
            "lbdo": "lobdow",
            "cosn": "wilsni1",
            "wiph": "wilpha",
            "rnph": "renpha",
            "spsa": "sposan",
            "sosa": "solsan",
            "grye": "greyel",
            "will": "willet1",
            "leye": "lesyel",
            "frgu": "fragul",
            "rbgu": "ribgul",
            "cote": "comter",
            "neco": "neocor",
            "dcco": "doccor",
            "brpe": "brnpel",
            "ambi": "amebit",
            "lebi": "leabit",
            "gbhe": "grbher3",
            "greg": "greegr",
            "sneg": "snoegr",
            "trhe": "triher",
            "caeg": "categr",
            "grhe": "grnher",
            "bcnh": "bcnher",
            "wfib": "whfibi",
            "blvu": "blkvul",
            "tuvu": "turvul",
            "ospr": "osprey",
            "goea": "goleag",
            "noha": "norhar1",
            "ssha": "shshaw",
            "coha": "coohaw",
            "cbha": "comblh1",
            "haha": "hrshaw",
            "grha": "gryhaw2",
            "swha": "swahaw",
            "ztha": "zothaw",
            "rtha": "rethaw",
            "bnow": "brnowl",
            "weso": "wesowl1",
            "ghow": "grhowl",
            "fepo": "fepowl",
            "elow": "elfowl",
            "buow": "burowl",
            "beki": "belkin1",
            "wisa": "wilsap",
            "ybsa": "yebsap",
            "rnsa": "rensap",
            "rbsa": "rebsap",
            "lewo": "lewwoo",
            "acwo": "acowoo",
            "giwa": "gilwoo",
            "nofl": "norfli",
            "gifl": "gilfli",
            "amke": "amekes",
            "merl": "merlin",
            "pefa": "perfal",
            "prfa": "prafal",
            "nbty": "nobtyr",
            "osfl": "olsfly",
            "wewp": "wewpew",
            "wifl": "wilfly",
            "lefl": "leafly",
            "hafl": "hamfly",
            "grfl": "gryfly",
            "dufl": "dusfly",
            "psfl": "pasfly",
            "cofl": "corfly",
            "blph": "blkpho",
            "saph": "saypho",
            "vefl": "verfly",
            "dcfl": "ducfly",
            "atfl": "astfly",
            "bcfl": "bncfly",
            "trki": "trokin",
            "caki": "caskin",
            "weki": "weskin",
            "eaki": "easkin",
            "wevi": "whevir",
            "bevi": "belvir",
            "huvi": "hutvir",
            "cavi": "casvir",
            "plvi": "plsvir",
            "wavi": "warvir",
            "losh": "logshr",
            "wesj": "cowscj1",
            "meja": "mexjay4",
            "chra": "chirav",
            "cora": "comrav",
            "brti": "britit",
            "verd": "verdin",
            "hola": "horlar",
            "nrws": "nrwswa",
            "puma": "purmar",
            "trsw": "treswa",
            "vgsw": "vigswa",
            "bans": "banswa",
            "bars": "barswa",
            "clsw": "cliswa",
            "cobu": "bushti",
            "rcki": "ruckin",
            "wbnu": "whbnut",
            "brcr": "brncre",
            "bggn": "buggna",
            "btgn": "bktgna",
            "rowr": "rocwre",
            "canw": "canwre",
            "howr": "houwre",
            "mawr": "marwre",
            "bewr": "bewwre",
            "cacw": "cacwre",
            "eust": "eursta",
            "cbth": "cubthr",
            "beth": "benthr",
            "crth": "crithr",
            "sath": "sagthr",
            "nomo": "normoc",
            "webl": "wesblu",
            "mobl": "moublu",
            "swth": "swathr",
            "heth": "herthr",
            "amro": "amerob",
            "cewa": "cedwax",
            "phai": "phaino",
            "hosp": "houspa",
            "ampi": "amepip",
            "hofi": "houfin",
            "recr": "redcro",
            "pisi": "pinsis",
            "lego": "lesgol",
            "lago": "lawgol",
            "amgo": "amegfi",
            "rwsp": "ruwspa",
            "casp": "casspa",
            "grsp": "graspa",
            "chsp": "chispa",
            "ccsp": "clcspa",
            "bcsp": "bkcspa",
            "brsp": "brespa",
            "btsp": "bktspa",
            "lasp": "larspa",
            "larb": "larbun",
            "fosp": "foxspa",
            "deju": "daejun",
            "wcsp": "whcspa",
            "wtsp": "whtspa",
            "sags": "sagspa1",
            "vesp": "vesspa",
            "savs": "savspa",
            "sosp": "sonspa",
            "lisp": "linspa",
            "cant": "cantow",
            "abto": "abetow",
            "rcsp": "rucspa",
            "gtto": "gnttow",
            "spto": "spotow",
            "ybch": "yebcha",
            "yhbl": "yehbla",
            "weme": "wesmea",
            "eame": "easmea",
            "hoor": "hooori",
            "buor": "bulori",
            "scor": "scoori",
            "rwbl": "rewbla",
            "broc": "brocow",
            "bhco": "bnhcow",
            "brbl": "brebla",
            "gtgr": "grtgra",
            "mgwa": "macwar",
            "coye": "comyel",
            "ywar": "yelwar",
            "yrwa": "yerwar",
            "btyw": "btywar",
            "towa": "towwar",
            "hewa": "herwar",
            "wiwa": "wlswar",
            "suta": "sumtan",
            "weta": "westan",
            "noca": "norcar",
            "pyrr": "pyrrhu",
            "bhgr": "bkhgro",
            "blgr": "blugrb1",
            "lazb": "lazbun",
            "inbu": "indbun",
            "vabu": "varbun"
}
