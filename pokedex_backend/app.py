"""
To do: 
# Add error handling

# I know APIs should be named after the specific resources (nouns) and not verbs. 
# But should it be singular or plural?

# Look into specific response codes. How to be as specific as possible? 

# How to handle large API call with all of the pokemon from pokeapi that I need to get? 

# Close database connection 

# What other fields go into a POST request header? in a response header and body? 

2 ways to break up the large call and mapping 
either you break it up by getting a bit of data each time, and doing the mapping there 
or you break it up by getting all the data in one go and then do the mapping. 
it's like the difference between breadth and depth of work. how much ur doing and what ur doing? 
- use filtering!!! 

# how to make the code resilient to changes over time from the API? 
- make preset definitions
- make things not mandatory? 
- etc? 

-- 
Voice your concern about it when you review it with them later, explaining server side sorting and pagination would be better. ( Would it though ? )

I helped a friend with this before and the data is tiny. It's 1000 small JSON objects. Request it, cache it, paginate it on the client, then show the first page and get the images for the pokemon then.

I wouldn't be surprised if they're doing this to test your async knowledge, so they're expecting delays

You could also go above and beyond, add a service worker so it caches all the data and have your web page run offline. ( Probably need to add a default Pokémon image or download all the images)
--

-- query database at buildtime 
-- cache it locally? 
-- loading indicator (async function)
-- show random pokemon fact in loading? 
-- weakness of the api doesnt allow server-side filtering, so have to do it on the frontend. 
a. can mitigate this with ui, ux, and optimizations (lazy load, pagination, loading screen)

Important methods: 
1. get_json() - get JSON from user input (in POST request)
2. json() - convert API response to JSON 

Steps: 
1. Query data from the Pokemon API, get the necessary fields (which match our internal definition) 
2. Post data to our internal bulk APIs
"""

import os
import requests
import psycopg2
import requests_cache
import time
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
@app.get("/pokemon/map_pokemon")
def map_pokemon(): 
    count = 0
    # name, scientific name, strengths (name and priority), health, types 
    for result in POKE_TOTAL: 
        count+=1
        pokemon_info = requests.get(result["url"])
        print("just got info for " + result["name"])

        pokemon_info = pokemon_info.json()
        name = pokemon_info["name"]
        scientific_name = pokemon_info["species"]["name"]
        
        health = pokemon_info["stats"][0]["base_stat"]
        
        # need to do strengths and types 
        types = pokemon_info["types"][0]["type"]["name"]
        image = pokemon_info["sprites"]["front_default"]

        info_mapped = { 
            "name": name, 
            "scientific_name": scientific_name, 
            "health": health, 
            "types": types,
            "image": image
        }
 
        print("adding info for" + result["name"])
        POKE_INFO_MAPPED.append(info_mapped)
    
    # submit mapped pokemon to internal API 
    return {"count": count, "result": POKE_INFO_MAPPED}, 200 

@app.post("/pokemon/bulk")
def push_pokemon(): 
    return {"message": "sucsscess! got your post!", "result": request.json}, 200

@app.get("/pokemon/bulk-no-pagination")
@cross_origin()
def populate_pokemon_no_pagination(): 
    return {"result": POKE_INFO_MAPPED}, 200

if __name__ == "__main__": 
    get_pokemon()
    map_pokemon()
    app.run(port=8000)