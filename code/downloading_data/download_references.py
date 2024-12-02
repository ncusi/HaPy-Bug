import requests as req
import multiprocessing as mp
import json
import queue
import os
from os import path
from hashlib import sha256
from twowaydict import TwoWayDict
from tqdm import tqdm


CVES_DATA_DIRNAME                   = 'data'
CVE_REFERENCES_DIRNAME              = 'References'
ALL_REFERENCES_DIRNAME              = 'All_References'
ALL_CVES_DOWNLOAD_STATUS_FILENAME   = 'download_status.json'
ALL_CVES_FILE_URL_ASSOC_FILENAME    = 'hash_url_dict.json'
CVE_CHANGELOG_FILENAME              = 'nvd_changelog.json'
CVE_DATES_PLOT_FILENAME             = 'dates_plot.png'
CVE_GROUPS_FILENAME                 = 'groups.json'
CVE_BY_REFURL_FILENAME              = 'references_in_cves.json'


def hash_url_worker(base_dir_path: str, hash_queue, should_stop):  
    hashUrlDict = TwoWayDict()    

    while not should_stop.is_set():
        try:
            url, url_filename = hash_queue.get(timeout = 3)
        except queue.Empty:
            continue

        hashUrlDict[url] = url_filename

    with open(path.join(base_dir_path, ALL_CVES_FILE_URL_ASSOC_FILENAME), 'w') as f:
        f.write(json.dumps(hashUrlDict.copy()))



def ref_download(url : str, cve_id : str, base_path: str, url_queue, url_resp_dict : dict) -> int:
    
    url_filename = sha256(url.encode()).hexdigest() + '.html'
    all_references_path = path.join(base_path, ALL_REFERENCES_DIRNAME, url_filename)

    if url in url_resp_dict and url_resp_dict[url] == 200:
        os.link(all_references_path, path.join(base_path, CVES_DATA_DIRNAME, cve_id, CVE_REFERENCES_DIRNAME, url_filename))
    else:
        try:
            response = req.get(url)
        except req.exceptions.ConnectionError:
            return 10
        except req.exceptions.Timeout:
            return 11
        except req.exceptions.TooManyRedirects:
            return 12
        except req.exceptions.InvalidSchema:
            return 13

        if response.status_code != 200:
            return response.status_code
    
        try:
            with open(all_references_path, 'wb') as f:
                f.write(response.content)
                url_queue.put((url, url_filename))
        except:
            pass
        else:
            os.link(all_references_path, path.join(base_path, CVES_DATA_DIRNAME, cve_id, CVE_REFERENCES_DIRNAME, url_filename))

    return 200


#base_path : path to the base dir [/mnt/data/CVE]
def make_cve_struct(params):
    cve_id, base_path, url_resp_dict, url_cves, url_queue, = params
    
    LOCAL_CVE_SERVER_URL = f"http://158.75.112.151:5000/api/cve/{cve_id}"
    try:
        response = req.get(LOCAL_CVE_SERVER_URL)
    except:
        return
    else:
        if response.status_code != 200:
           return

    content_cve = json.loads(response.content)

    os.makedirs(path.join(base_path, CVES_DATA_DIRNAME, cve_id, CVE_REFERENCES_DIRNAME), exist_ok=True)

    for url in content_cve['references']:
        req_status = ref_download(url, cve_id,  base_path, url_queue, url_resp_dict)
        url_resp_dict.setdefault(url, req_status)
        url_cves.setdefault(url, list()).append(cve_id)


#base_path : path to the main folder [/mnt/data/CVE]
def main(base_path : str, cve_ids_filename: str):

    with open(path.join(base_path, cve_ids_filename), 'r') as f:
        cve_ids = [line.strip() for line in f.readlines()]

        os.makedirs(os.path.join(base_path, ALL_REFERENCES_DIRNAME), exist_ok=True)

        manager = mp.Manager()
        url_queue = manager.Queue()
        sem_przybysz = manager.Semaphore(value=10)
        url_responses = manager.dict()
        url_cves = manager.dict()
        should_stop = mp.Event()

        hash_url_worker_process = mp.Process(target=hash_url_worker,
                                             args=(base_path, url_queue, should_stop))
        hash_url_worker_process.start()

        with mp.Pool(48) as pool:
            params = [(id,
                       base_path,
                       url_responses, url_cves,
                       url_queue,) for id in cve_ids]
            
            for _ in tqdm(pool.imap_unordered(make_cve_struct, params), total=len(params), 
                          dynamic_ncols=True, unit=''):
                pass

        should_stop.set()
        hash_url_worker_process.join()

        # Zapis słownika URLi po zapisaniu wszystkich
        with open(path.join(base_path, ALL_CVES_DOWNLOAD_STATUS_FILENAME), 'w') as f:
            f.write(json.dumps(url_responses.copy()))

        with open(path.join(base_path, CVE_BY_REFURL_FILENAME), 'w') as f:
            f.write(json.dumps(url_cves.copy()))



if __name__ == '__main__':
    main('/mnt/data/CVE', 'cve_ids.txt')
