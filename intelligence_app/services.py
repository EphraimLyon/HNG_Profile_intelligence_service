import requests

class ExternalAPIError(Exception):
    pass


def fetch_gender(name):
    res = requests.get(f"https://api.genderize.io?name={name}").json()

    if res.get("gender") is None or res.get("count", 0) == 0:
        raise ExternalAPIError("Genderize")
    ## returns gender from genderize api calls
    return res


def fetch_age(name):
    res = requests.get(f"https://api.agify.io?name={name}").json()
##returns age from agify api calls
    if res.get("age") is None:
        raise ExternalAPIError("Agify")

    return res


import requests

class ExternalAPIError(Exception):
    pass


def fetch_country(name):
    res = requests.get(f"https://api.nationalize.io?name={name}").json()

    countries = res.get("country", [])

    if not countries:
        raise ExternalAPIError("Nationalize")

    best = max(countries, key=lambda x: x["probability"])
        ##returns country id and probability from nationalize api calls 
    return {
        "country_id": best["country_id"],
        "probability": best["probability"]
    }
    res = requests.get(f"https://api.nationalize.io?name={name}").json()

    countries = res.get("country", [])
    if not countries:
        raise ExternalAPIError("Nationalize")

    best = max(countries, key=lambda x: x["probability"])
    return best