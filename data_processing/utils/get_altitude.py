import requests

def get_altitude(latitude: float, longitude: float) -> float:

    addr = 'https://api.opentopodata.org/v1/mapzen'
    r = requests.get(f'{addr}?locations={latitude},{longitude}')
    r = r.json()

    if r['status'] == 'OK':
        altitude = r['results'][0]['elevation']
        return altitude

    else:
        return -1000