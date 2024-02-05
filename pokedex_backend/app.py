import os
import requests
import psycopg2
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from flask import Flask, request 

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

POKE_API_URL = "https://pokeapi.co/api/v2/pokemon?limit=100&offset=0"
POKE_TOTAL = [] 
POKE_INFO_MAPPED = []

CORS(app)

@app.get("/")
def home():
    return "Hello world"

# Step 1: port pokemon from API 
def get_pokemon(): 
    print("getting all pokemon info")
    r = requests.get(POKE_API_URL)

    r = r.json()
    results = r["results"]
    next_results = r["next"]
    while next_results: 
        for result in results: 
            POKE_TOTAL.append(result)
        r = requests.get(next_results)

        r = r.json()
        results = r["results"]
        next_results = r["next"]
    
    # Get the remaining results 
    for result in results: 
            POKE_TOTAL.append(result)

    print("finished getting all pokemon info")

# Step 2: map data 
def map_pokemon(): 
    count = 0
    for result in POKE_TOTAL: 
        count+=1
        pokemon_info = requests.get(result["url"])
        print("just got info for " + result["name"])

        # name, scientific name, strengths (name and priority), health, types 
        pokemon_info = pokemon_info.json()
        name = pokemon_info["name"]
        scientific_name = pokemon_info["species"]["name"]
        health = pokemon_info["stats"][0]["base_stat"]
        types = pokemon_info["types"][0]["type"]["name"]
        image = pokemon_info["sprites"]["front_default"]

        info_mapped = { 
            "name": name, 
            "scientific_name": scientific_name, 
            "health": health, 
            "types": types,
            "image": image
        }
 
        POKE_INFO_MAPPED.append(info_mapped)
    
    # submit mapped pokemon to internal API 
    return {"count": count, "result": POKE_INFO_MAPPED}, 200 

@app.post("/pokemon/bulk")
def push_pokemon(): 
    return {"message": "success! got your post!", "result": request.json}, 200

@app.get("/pokemon/bulk-no-pagination")
@cross_origin()
def populate_pokemon_no_pagination(): 
    return {"result": POKE_INFO_MAPPED}, 200

if __name__ == "__main__": 
    get_pokemon()
    map_pokemon()
    app.run(port=8000)