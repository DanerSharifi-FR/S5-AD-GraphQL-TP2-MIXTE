# UE-AD-A1-REST

Pour la première partie ne vous souciez pas des fichiers Docker, cela sera abordé par la suite en séance 4.


## Mise en place

python3 -m venv .venv

source .venv/bin/activate

pip3 install -r requirements.txt

bash start.sh

docker compose build
python3 import_json_into_mongo.py
docker compose up <nom-conteneur> 