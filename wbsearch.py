import time, requests

def ent_id_finder(entity: str):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action":  "wbsearchentities",
        "language":"nl",
        "uselang":"nl",
        "format": "json",
        "search": entity,
        "type":   "item",
        "limit":  15
    }
    time.sleep(1)
    response = requests.get(url, params=params)
    time.sleep(1)
    response.raise_for_status()
    data = response.json()

    results = data.get("search", [])

    if results:
        #print("Entity id:")
        for r in results:
            desc = r.get("description", "")
            #print(f"{r['id']}\t{r['label']}\t{desc}")
        # return results[0]['id']
        return results
    else:
        #print("No entity id found")
        return []

def prop_id_finder(property):
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action':'wbsearchentities',
            'language':'nl',
            'uselang':'nl',
            "search": property,
            'type':'property',
            'format':'json'}
    time.sleep(1)
    response = requests.get(url, params=params)
    time.sleep(1)
    response.raise_for_status()
    data = response.json()

    results = data.get("search", [])

    if results:
        #print("property id:")
        for r in results:
            desc = r.get("description", "")
            #print(f"{r['id']}\t{r['label']}\t{desc}")
        #return results[0]['id']
        return results
    else:
        #print("No property id found")
        return []