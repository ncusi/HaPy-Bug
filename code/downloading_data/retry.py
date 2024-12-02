from urllib.parse import urlsplit
from collections import defaultdict
from hashlib import sha256
from twowaydict import TwoWayDict
import os
import httpx
import json


def make_groups(links : dict):
        link_groups = defaultdict(list)

        for link in links:
            if links[link] != 200:
                link_groups[urlsplit(link).netloc].append(link)

        return link_groups


def download_groups(base_dir : str):
    counter = 0

    with open(os.path.join(base_dir, 'download_status.json')) as f:
        links = json.load(f)
    with open(os.path.join(base_dir, 'references_in_cves.json'), 'r') as f:
        cve_ref_dict = json.load(f)
    with open(os.path.join(base_dir, 'hash_url_dict.json'), 'r') as f:
        hash_url_dict = TwoWayDict(json.load(f))

    link_groups = make_groups(links)
    with httpx.Client(http2 = True, follow_redirects = True) as client:
        for group in link_groups:
            omit = False
            for link in link_groups[group]:
                if omit: 
                    break

                status = 0
                try: 
                    response =  client.get(link)
                    status = response.status_code
                except httpx.ConnectError:
                    status = 10
                    omit = True
                    continue
                except httpx.ConnectTimeout:
                    status = 11
                    omit = True
                    continue
                except httpx.ReadTimeout:
                    omit = True
                    status = 12
                    continue
                except httpx.TooManyRedirects:
                    status = 13
                    continue
                except httpx.UnsupportedProtocol:
                    status = 14
                    continue
                except httpx.RemoteProtocolError:
                    status = 15
                    continue
                finally:
                    links[link] = status
                    print(f"{status} : {link}")
    
                hashed_url = sha256(link.encode()).hexdigest() + '.html'
                hash_url_dict[link] = hashed_url
                all_references_path = os.path.join(base_dir, "All_References", hashed_url)
                try:
                    with open(all_references_path, 'wb') as f:
                        f.write(response.content)
                        counter +=1
                except:
                    pass
                else:
                    for id in cve_ref_dict[link]:
                        os.link(all_references_path, os.path.join(base_dir, 'data', id, 'References'))

    with open(os.path.join(base_dir, 'hash_url_dict.json'), 'w') as f:
        f.write(json.dumps(hash_url_dict))
    with open(os.path.join(base_dir, 'download_status.json'), 'w') as f:
        f.write(json.dumps(links))

    print(counter)



if __name__ == '__main__':
    download_groups('/mnt/data/CVE')
