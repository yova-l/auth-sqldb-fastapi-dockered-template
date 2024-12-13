# FastAPI - Auth - Postgresql - Docker

<h3><strong>Avaliable endpoints:</strong></h3>
<ul>
<li> <strong>/authreq/{pageid}</strong> (Requiries token auth)</li>
<li> <strong>/token</strong></li>
<li> <strong>/noauthreq (Doesn't require token)</strong></li>
</ul>

## Usage
1) Set the corresponding enviroment variables in the .env file:
```bash
secret_key="84daa0256a3289b0fb23693bg1f6034d44396675749244721b2b20e896e11672"
algorithm="HS256" 
```

2) For now, it is assumed that the DB was set correctly

3) Configure the database.ini file with all the necessary information to connect with the db.
```ini
[postgresql]
host=localhost
port=5431
database=notn_users
user=postgres
password=YOURPASSWORD123456postgresuser
```
4) Add your endpoints and adapt the code to your needs (app directory).

5) (OPT for local testing) Install py dependencies and create an enviroment
```bash
[postgresql]
python -m venv env
source env/bin/activate
pip install -r requirements.txt
fastapi dev ./app/main.py
```

6) Once everything has been set up simply use `docker compose up` to have your container up and running.
Or check this resource for more options: https://github.com/yova-l/fastAPI-docker-template

## Resources that helped developed this API:
* https://www.youtube.com/watch?v=5GxQ1rLTwaU Auth
* https://www.youtube.com/watch?v=Hs9Fh1fr5s8 Extra

Consumer app example included.