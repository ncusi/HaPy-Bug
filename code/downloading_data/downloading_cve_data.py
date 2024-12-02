import requests
import json
from joblib import Parallel, delayed
import os


def getCveJson(cve_id, address="158.75.112.151:5000"):
    """Parameters:
    cve_id is a CVE number, for example: CVE-2016-3333.
    address is an IP address with port number where the CVE Search is hosted.
    Returns a json with data about CVE with given number."""
    response = requests.get("http://" + address + "/api/cve/" + cve_id)
    return response.json()


def saveCveJson(cve_id, path="."):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, cve_id + ".json"), "w") as f:
        json.dump(getCveJson(cve_id), f)


def parallelSaveJsons(cve_ids, path="."):
    Parallel(n_jobs=-1)(delayed(saveCveJson)(id, os.path.join(path, id)) for id in cve_ids)
