from collections import OrderedDict

class SpeciesCounts(object):

    def __init__(self, ebird_responses:dict):
        self.locations = self.extractLocationObservations(ebird_responses)

    def extractLocationObservations(self, ebird_responses):
        obsLocations = {}
        for obs in ebird_responses:
            locId = obs['locId']
            if locId not in obsLocations:
                obsLocations[locId] = self.getLocData(obs)
            locDate = obs['obsDt']
            if locDate not in obsLocations[locId]['obs']:
                obsLocations[locId]['obs'][locDate] = OrderedDict()
            species = obs['comName']
            obsLocations[locId]['obs'][locDate][species] = self.getObsData(obs)
        return obsLocations


    def getLocData(self, loc):
        locData = {}
        locData['name'] = loc['locName']
        locData['coords']= (loc['lat'], loc['lng'])
        locData['private'] = loc['locationPrivate']
        locData['obs'] = OrderedDict()
        return locData

    def getObsData(self, obs):
        obsData = {}
        if 'howMany' in obs:
            obsData['count'] = obs['howMany']
        else:
            obsData['count'] = 0
        obsData['checklist'] = obs['subId']
        obsData['reviewed'] = obs['obsReviewed']
        obsData['valid'] = obs['obsValid']
        return obsData

class EbirdChecklist(object):
    def __init__(self, values:dict):
        self.locId = None  # "L7516403",
        self.subId = None  # "S81818535",
        self.userDisplayName = None  # "Sharon Goldwasser",
        self.numSpecies = None  # 11,
        self.obsDt = None  # "17 Feb 2021",
        self.obsTime = None  # "10:49",
        self.subID = None  # "S81818535",
        loc = None