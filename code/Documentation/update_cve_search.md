# How setup CVE search in docker

## Installation and setup

To get started `docker compose` and `git` tools are required.

First step is to clone this repo [CVE-Search-Docker](https://github.com/cve-search/CVE-Search-Docker). Here is the https link `https://github.com/cve-search/CVE-Search-Docker.git`

Most of setup here is done in [docker-compose.yml](https://github.com/cve-search/CVE-Search-Docker/blob/master/docker-compose.yml). Because previous search web page was on port 5000, I modified service cve_search by changing exposed port from `443:5000` to `5000:5000`. There are more settings here, but I left them as is.

To launch this use `docker compose up -d` where `-d` is used to launch in detach mode, so it will continue running after ssh session ends.

**The web page works on https with self signed sertificate, so trust the sertificate, it won't work with http** here is link, but change the ip `https://127.0.0.1:5000/`

## Repopulation

This one was a bit tricky, firstly you need connect to container and set env variable `WORKER_SIZE` to 1, because with too many download workers and connections, system will end them, distupting download.

To connect use

```bash
docker exec -it 86bc21ad1a21 /bin/bash
```

replace id with proper one, to get it you can use

```bash
docker ps | grep cve_search
```

Image name is `cve_search` without anything in the end, id column should be the first one

Then, after you connected to container, set env variable

```bash
env WORKER_SIZE=1
```

Next, according to [this documetation](https://cve-search.github.io/cve-search/database/database.html#repopulating-the-database) to drop and re-populate all the databases use

```bash
./sbin/db_updater.py -v -f
```

This will take a lot of time, and search will be unusable, so be careful here

After it'd done, you can just disconnect and db should be with new CVEs
