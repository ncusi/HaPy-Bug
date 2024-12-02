from collections import deque
from enum import IntEnum
import multiprocessing
import time
import requests
from tqdm import tqdm

NVD_RATE_LIMIT_WINDOW = 30
NVD_REQUESTS_LIMIT = 50
NVD_API_KEY = 'f94f1349-7d29-441a-95ea-855c42c90f48'


class NVDAPI(IntEnum):
    Info = 1
    History = 2

NVDAPIURLS = {  NVDAPI.Info     : r'https://services.nvd.nist.gov/rest/json/cves/2.0', 
                NVDAPI.History  : r'https://services.nvd.nist.gov/rest/json/cvehistory/2.0'}


class NVDThrottle:

    def __init__(self,
                 condition:multiprocessing.Condition,
                 sem_demand:multiprocessing.Semaphore,
                 sem_finish:multiprocessing.Semaphore) -> None:


        self.right_time_condition:multiprocessing.Condition = condition
        self.demand_semaphore:multiprocessing.Semaphore = sem_demand
        self.finish_semaphore:multiprocessing.Semaphore = sem_finish
       
    def get(self, cve_id:str, api_type:NVDAPI):
        with self.right_time_condition:
            self.demand_semaphore.release()
            self.right_time_condition.wait()

        response = requests.get(NVDAPIURLS[api_type],
                                params ={'cveId'  : cve_id},
                                headers={'apiKey' : NVD_API_KEY})
    
        self.finish_semaphore.release()
        #response.raise_for_status()
        return response


def nvd_throttle_manager(right_time_condition:multiprocessing.Condition,
                         demand_semaphore:multiprocessing.Semaphore,
                         finish_semaphore:multiprocessing.Semaphore,
                         should_stop:multiprocessing.Event) -> None:

    requests_queue = deque(maxlen=NVD_REQUESTS_LIMIT)

    while not should_stop.is_set():
        if demand_semaphore.acquire(timeout=3):
            if len(requests_queue) == NVD_REQUESTS_LIMIT:
                delay = NVD_RATE_LIMIT_WINDOW - (time.time() -  requests_queue.popleft())
                time.sleep(delay if delay > 0 else 0)

            with right_time_condition:
                right_time_condition.notify()

            while not finish_semaphore.acquire(timeout=3):
                if should_stop.is_set():
                    break
            else:
                requests_queue.append(time.time())
    
