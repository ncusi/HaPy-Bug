from typing import Any
from bs4 import BeautifulSoup, NavigableString, builder as bsbuilder
from datetime import date 
from collections import Counter
from dateutil import parser
from datetime import datetime
from tqdm import tqdm
import json
import os
import re
import requests as req
import matplotlib.pyplot as plt
import multiprocessing as mp


from dateparse import DateParse
from json_encoder import JsonDatetimeEncoder
import nvd2sem as nvd


LOCAL_CVE_SERVER_URL = 'http://158.75.112.151:5000/api/cve/{cveId}'

CVES_DATA_DIRNAME                   = 'data'
CVE_REFERENCES_DIRNAME              = 'References'
ALL_CVES_DOWNLOAD_STATUS_FILENAME   = 'download_status.json'
ALL_CVES_FILE_URL_ASSOC_FILENAME    = 'hash_url_dict.json'
CVE_CHANGELOG_FILENAME              = 'NVD_Changelog.json'
CVE_DATES_PLOT_FILENAME             = 'dates_plot.png'
CVE_GROUPS_FILENAME                 = 'groups.json'



def group_by_prefix(url:str, prefix_groups:dict) -> None:
    ret = url.split("/")
    groups = []

    for i,e in enumerate(ret[2:]):
        if len(ret[2:2+i]) == 0 or not e:
            continue

        key = "/".join(ret[2:2+i])
        groups.append(key)
        prefix_groups.setdefault(key, list()).append(url)

    return groups



def make_figure(cve_dir, publish_date, cve_all_likely_dates, nvd_changelog_dates):

    dtzero = datetime.fromtimestamp(0).date()
    try:
        #found with likely formats and those extracted from NVD changelog
        likely_dates_counter = Counter([dt for dt in cve_all_likely_dates
                                           if dt <= publish_date and dt >= dtzero])                   
        
        nvd_changelog_datelist_counter = Counter([dt for dt in nvd_changelog_dates
                                                     if dt <= publish_date and dt >= dtzero])   
        #making and saving scatter plot of dates
        fig, ax = plt.subplots(layout='constrained')

        ax.scatter(likely_dates_counter.keys(), likely_dates_counter.values(),
                   c='blue', label='Parsed dates')
        ax.scatter(nvd_changelog_datelist_counter.keys(), nvd_changelog_datelist_counter.values(),
                   c='orange', label='NVD changelog dates')
        
        ax.set_ylabel('Occurances')
        ax.set_xlabel('Dates')
        #ax.set_xticklabels(labels=ax.get_xticklabels(), rotation=45)
        plt.setp(ax.get_xticklabels(), rotation=45)
        ax.legend()
        fig.savefig(os.path.join(cve_dir, CVE_DATES_PLOT_FILENAME))
        plt.close(fig)
    except:
        print(f'Figure Exception: {cve_dir}')



def dateExtraction(cve_refs_dir:str, 
                   reference_filename:str,
                   response_status_code:int) -> dict:
    
    """ Function parses given url in search of dates. It creates a .html file
        in the 'References' folder at a given path.

    Args:
        url (str): The URL address of the webpage where the dates are to be found

        referencesDirectory (str): Path to a folder with 'References' subfolder
        in which to save .html file requested from a given url

    Returns:
        dict: A dictionary with three fields: 'response_status' holding an int
            corresponding to the status of GET request response
            (10 in case of connection error, 11 in case of timeout error),
            'found_likely_dates' and 'found_specul_dates', both holding
            a list of two inner lists representing likely and speculative
            information about dates respectively, each of which holding tuples
            containing a date, additional context, and a tag where the date was found

        list: List of all dates found using 'likely' date formats

        list: List of all dates found using 'speculative' date formats
    """

    result = dict.fromkeys(['response_status', 'found_likely_dates', 'found_specul_dates'])
    result['response_status'] = response_status_code

    if response_status_code != 200:
        return result, [], []
    
    with open(os.path.join(cve_refs_dir, reference_filename), 'rb') as site:
        try:
            soup = BeautifulSoup(site, 'html.parser', from_encoding="iso-8859-1")
        except bsbuilder.ParserRejectedMarkup:
            print(f'bs4 Parser Exception, file: {reference_filename}')
            return result, [], []

    likely_found = {'min': date.max, 'max': date.min, 'likely': []}
    specul_found = {'min': date.max, 'max': date.min, 'speculative': []}
    
    refpage_all_html_tags = soup.find_all()

    refpage_all_likely = []
    refpage_all_specul = []

    for html_tag in refpage_all_html_tags:
        for child in html_tag.children:
            if isinstance(child, NavigableString):
                dates_parsed = DateParse(child.text)

                if dates_parsed[0] != [] :
                    likely_found['likely'].append({
                        'dates'              : dates_parsed[0], 
                        'additional_context' : re.sub(r'\s+', ' ',re.sub(r'\-{4,}', '---', child.text)),
                        'tag_mame'           : html_tag.name})
                    
                    refpage_all_likely += dates_parsed[0]
                    
                    likely_found['min'] = min([*dates_parsed[0], likely_found['min']], key=lambda x: x.toordinal())
                    likely_found['max'] = max([*dates_parsed[0], likely_found['max']], key=lambda x: x.toordinal())

                if dates_parsed[1] != [] :
                    specul_found['speculative'].append({
                        'dates'              : dates_parsed[1],
                        'additional_context' : re.sub(r'\s+', ' ', re.sub(r'\-{4,}', '---', child.text)),
                        'tag_mame'           : html_tag.name})
                    
                    refpage_all_specul += dates_parsed[1]
   
                    specul_found['min'] = min([*dates_parsed[1], specul_found['min']], key=lambda x: x.toordinal())
                    specul_found['max'] = max([*dates_parsed[1], specul_found['max']], key=lambda x: x.toordinal())
 
    if likely_found['max'] == date.min: likely_found['max'] = None
    if likely_found['min'] == date.max: likely_found['min'] = None  
    if specul_found['max'] == date.min: specul_found['max'] = None
    if specul_found['min'] == date.max: specul_found['min'] = None

    result['found_likely_dates'] = likely_found
    result['found_specul_dates'] = specul_found

    return result, refpage_all_likely, refpage_all_specul




def extract_dates_from_cve_refs(cve_id:str, base_dir:str, 
                                prefix_groups:dict, hash_url_dict:dict, responses:dict,
                                nvd_right_time_condition:mp.Condition,
                                nvd_demand_semaphore:mp.Semaphore,
                                nvd_complete_semaphore:mp.Semaphore):

    """Function for extracting dates and additional information
        taken from each website given as an element in the input list.
        As a side effect it creates the folder structure described in README file.

    Args:
        cveId (str): An id for a given CVE, for example CVE-2021-3177

        baseDirPath (str): A path to the desired location in which to create
            the file structure described in README [/mnt/data/CVE]

        prefixg (defaultdict): A dictionary holding prefix groups of parsed URLs
            as keys and full URL addresses as values, 
            present as a argument for the purpose of sharing this object
            over different processes created by joblib.

        throttle: Object of class nvdRequests defined in aux_classes.py,
            present as a argument for the purpose of sharing 
            this object over different processes created by joblib.

    Returns:
        dict: A dictionary with URLs as keys and inner dictionaries as values.
            Fields of those inner dictionaries are 'resposne_status' holing an integer
            corresponding to the status of GET request response for a given URL,
            'content', which holds a list of results likely to be dates,
            returned by the dateExtraction function and 'label' holding a list
            of tags extracted from nist nvd.

        dict: A dictionary with similar structure as the first returned object,
            with elements in the field 'content' found using more speculative date formats.
    """
        
    CVEinfoLikely = dict()
    CVEinfoSpecul = dict()

    # building the structure, in which files are saved
    cve_dir = os.path.join(base_dir, CVES_DATA_DIRNAME, cve_id)    

    nvd_url_list = {}
    nvd_changelog_datelist = []

    nvd_throttle = nvd.NVDThrottle(nvd_right_time_condition,
                                   nvd_demand_semaphore, nvd_complete_semaphore)

    nvd_cve_info = nvd_throttle.get(cve_id, nvd.NVDAPI.Info)
    if nvd_cve_info.status_code == 200:
        nvdStruct = json.loads(nvd_cve_info.content)
    
        publish_date = parser.parse(nvdStruct['vulnerabilities'][0]['cve']['published']).date()
        nvdTags = nvdStruct['vulnerabilities'][0]['cve']['references']
        for ref in nvdTags:
            if 'tags' in ref.keys():
                nvd_url_list[ref['url']] = ref['tags']
    else:
        tqdm.write(f'{cve_id} Info: status {nvd_cve_info.status_code}')
        try:
            response_cve_data = req.get(LOCAL_CVE_SERVER_URL.format(cveId=cve_id))
        except:
            pass
        else:
            publish_date = parser.parse(json.loads(response_cve_data.content)['Published']).date()


    nvd_changelog =  nvd_throttle.get(cve_id, nvd.NVDAPI.History)
    if nvd_changelog.status_code == 200:
        with open(os.path.join(cve_dir, CVE_CHANGELOG_FILENAME), 'wb') as f:
            f.write(nvd_changelog.content)
        nvd_changelog_datelist = sorted([ parser.parse(change['change']['created']).date()
                                          for change in json.loads(nvd_changelog.content)['cveChanges']])
    else:
        tqdm.write(f'{cve_id} History: {nvd_changelog.status_code}')
     

    cve_all_likely_dates = []
    cve_all_specul_dates = []

    cve_refs_dir = os.path.join(cve_dir, CVE_REFERENCES_DIRNAME)
    for cve_ref_file_name in (file.name for file in
                              filter(lambda entry: not entry.is_dir() and entry.name.endswith('.html'),
                                    os.scandir(cve_refs_dir))):
        
        cve_ref_url = hash_url_dict[cve_ref_file_name]
        result, ref_likely_dates, ref_specul_dates = dateExtraction(cve_refs_dir,
                                                        cve_ref_file_name,
                                                        responses[cve_ref_url])

        cve_all_likely_dates += ref_likely_dates
        cve_all_specul_dates += ref_specul_dates

        status = result['response_status']
        urlInfoLikely = {'response_status' : status, 'label': [], 'content' : {}}
        urlInfoSpecul = {'response_status' : status, 'label': [], 'content' : {}}
        
        if cve_ref_url in nvd_url_list.keys():
            #using group_by_prefix function
            urlInfoLikely['label'] += nvd_url_list[cve_ref_url]
            urlInfoSpecul['label'] += nvd_url_list[cve_ref_url]
        else:
            #grouping references with NVD tags if they are present,
            groups = group_by_prefix(cve_ref_url, prefix_groups)                                                   
            urlInfoLikely['label'] += groups
            urlInfoSpecul['label'] += groups

        #if urlInfoLikely['response_status'] == 200:
        if status == 200:
            urlInfoLikely['content'] = result['found_likely_dates']
            urlInfoSpecul['content'] = result['found_specul_dates']

        CVEinfoLikely[cve_ref_url] = urlInfoLikely  
        CVEinfoSpecul[cve_ref_url] = urlInfoSpecul

    # writing CVEinfo dictionaries and two way dictionary
    with open(os.path.join(cve_dir, f'{cve_id}_likely.info.json'), 'w') as f:               
        f.write(json.dumps(CVEinfoLikely, cls=JsonDatetimeEncoder))
    # with hash <-> url correspondence to a adequate folder
    with open(os.path.join(cve_dir, f'{cve_id}_specul.info.json'), 'w') as f:
        f.write(json.dumps(CVEinfoSpecul, cls=JsonDatetimeEncoder))
    make_figure(cve_dir, publish_date, cve_all_likely_dates, nvd_changelog_datelist)
        
    return CVEinfoLikely, CVEinfoSpecul




def main(base_dir:str):
    
    with open(os.path.join(base_dir, ALL_CVES_FILE_URL_ASSOC_FILENAME), 'r') as f:
        hash_url_dict = json.load(f)
        with open(os.path.join(base_dir, ALL_CVES_DOWNLOAD_STATUS_FILENAME), 'r') as f:
            responses = json.load(f)

            cve_folders = [file.name for file in filter(
                lambda entry: entry.is_dir() and entry.name.startswith('CVE'),
                os.scandir(os.path.join(base_dir, CVES_DATA_DIRNAME)))]
            
            manager = mp.Manager()

            prefix_groups = manager.dict()
            responses_proxy = manager.dict(responses)
            hash_url_dict_proxy = manager.dict(hash_url_dict)

            nvd_throttle_condition = manager.Condition()
            nvd_demand_semaphore = manager.Semaphore(value=0)
            nvd_complete_semaphore = manager.Semaphore(value=0)

            should_stop = mp.Event()

            throttle_manager = mp.Process(target=nvd.nvd_throttle_manager,
                                          args=(nvd_throttle_condition,
                                                nvd_demand_semaphore,
                                                nvd_complete_semaphore,
                                                should_stop))
            throttle_manager.start()
            pbar = tqdm(total=len(cve_folders), unit='', dynamic_ncols=True)

            def progress_update(completed): pbar.update()
            def worker_error(failed): tqdm.write(f'Error: {failed}')

            with mp.Pool(min(nvd.NVD_REQUESTS_LIMIT, mp.cpu_count())) as pool:
                task_params = [(cve_id, base_dir, prefix_groups,
                                hash_url_dict_proxy, responses_proxy,
                                nvd_throttle_condition, 
                                nvd_demand_semaphore, nvd_complete_semaphore,
                                ) for cve_id in cve_folders]

                asyncresult_list = [pool.apply_async(extract_dates_from_cve_refs,
                                                     params,
                                                     callback=progress_update,
                                                     error_callback=worker_error)
                                                     for params in task_params]
                pool.close()
                pool.join()
                                                        
            should_stop.set()
            throttle_manager.join()
            pbar.close()

            with open(os.path.join(base_dir, CVE_GROUPS_FILENAME), 'w') as f:
                f.write(json.dumps(prefix_groups.copy()))



if __name__ == '__main__':
    main('/mnt/data/CVE')
    #main('cve_data')





