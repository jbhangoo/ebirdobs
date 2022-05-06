import json

class EbirdLoc(object):
    def __init__(self):
        self.locId = None # "L7516403",
        self.name = None # "Rolling Hills Park",
        self.latitude = None # 32.197719,
        self.longitude = None # -110.8041573,
        self.countryCode = None # "US",
        self.countryName = None # "United States",
        self.subnational1Name = None # "Arizona",
        self.subnational1Code = None # "US-AZ",
        self.subnational2Code = None # "US-AZ-019",
        self.subnational2Name = None # "Pima",
        self.isHotspot = None # true,
        self.locName = None # "Rolling Hills Park",
        self.lat = None # 32.197719,
        self.lng = None # -110.8041573,
        self.hierarchicalName = None # "Rolling Hills Park, Pima, Arizona, US",
        self.locID = None # "L75164

    def getRegion(self, lat, lon):
        jsonResponse = self.HttpGet("https://geo.fcc.gov/api/census/area?lat={0}&lon={1}".format(lat, lon))
        resultList = json.loads(jsonResponse)
        x = []
        for response in resultList:
            x.append(CensusResponse(response))
        region = x[0].results
        return region.state_code + '-' + region.county_fips.Substring(2)

class CensusResult(object):

    def __init__(self):
        self.block_fips = None
        self.bbox = (None, None, None, None)
        self.county_fips = None
        self.county_name = None
        self.state_fips = None
        self.state_code = None
        self.state_name = None
        self.block_pop_2015 = None
        self.amt = None
        self.bea = None
        self.bta = None
        self.cma = None
        self.eag = None
        self.ivm = None
        self.mea = None
        self.mta = None
        self.pea = None
        self.rea = None
        self.rpc = None
        self.vpc = None


class CensusResponse(object):
    def __init__(self, response):
        self.input = response['input']
        self.results = response['results']