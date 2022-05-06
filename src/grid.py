from geopy.distance import geodesic

# Grid constants for geographic conversion
MAP_LIMITS = {
    'xmin' :-15,
    'xmax' : -7.65,
    'ymin' : 7,
    'ymax' : 12.7
}

GRID_WIDTH = 147
GRID_HEIGHT = 114

DEGREES_PER_PIXEL_X = (MAP_LIMITS['xmax'] - MAP_LIMITS['xmin']) / GRID_WIDTH
DEGREES_PER_PIXEL_Y = (MAP_LIMITS['ymax'] - MAP_LIMITS['ymin']) / GRID_HEIGHT

def latlon_distance(coordinate1: tuple, coordinate2:tuple):
    '''

    :param coordinate1: tuple of (lat, long)
    :param coordinate2: tuple of (lat, long)
    :return: distance between arguments in km
    '''
    #distance_in_miles = geodesic(coordinate1, coordinate2).miles
    distannce_in_km = geodesic(coordinate1, coordinate2).km
    return distannce_in_km

def latlon_to_pixel(lat, lon):
    if (MAP_LIMITS['xmin'] < lon < MAP_LIMITS['xmax']) and \
       (MAP_LIMITS['ymin'] < lat < MAP_LIMITS['ymax']):
        x = int( (lon - MAP_LIMITS['xmin']) / DEGREES_PER_PIXEL_X )
        y = int( (MAP_LIMITS['ymax'] - lat) / DEGREES_PER_PIXEL_Y )
        return (y * GRID_WIDTH) + x
    return None

def pixel_to_latlon(pixel):
    if 0 < pixel < GRID_WIDTH*GRID_HEIGHT:
        x = pixel % GRID_WIDTH
        y = pixel // GRID_WIDTH
        lat = MAP_LIMITS['ymax'] - DEGREES_PER_PIXEL_Y * y
        lon = MAP_LIMITS['xmin'] + DEGREES_PER_PIXEL_X * x
        return lat, lon
    return None

def pixels_to_latlon(pixels):
    coords = [pixel_to_latlon(pixel) for pixel in pixels]
    latlon = list(zip(*coords))
    return latlon[0],latlon[1]
