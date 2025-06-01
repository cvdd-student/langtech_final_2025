import time, requests

def query_constructor_wh_how(property, entity):
    query = """
    PREFIX wd:   <http://www.wikidata.org/entity/>
    PREFIX wdt:  <http://www.wikidata.org/prop/direct/>
    SELECT ?answerLabel WHERE {
     wd:""" + entity + ' wdt:' + property + """ ?answer SERVICE wikibase:label {bd:serviceParam
wikibase:language "nl". } }"""
    return query

def query_constructor_yesno(property, entity, value = None):
    head = (
        "PREFIX wd:   <http://www.wikidata.org/entity/>\n"
        "PREFIX wdt:  <http://www.wikidata.org/prop/direct/>\n"
        "ASK {\n"
    )
    if value:                      # exact match
        triple = f"  wd:{entity} wdt:{property} wd:{value} .\n"
    else:                             # only existence needed
        triple = f"  wd:{entity} wdt:{property} ?o .\n"
    tail = "}"
    return head + triple + tail

def run_query(query):
    """
    Handles the running of a query and Returns answers.
    Implemented exponential back-off because I was hitting the rate-limit of the wikidata API
    """
    endpoint = "https://query.wikidata.org/sparql"
    headers  = {"Accept": "application/sparql-results+json"}
    
    MAX_RETRIES = 5  
    INITIAL_BACKOFF_DELAY = 1  
    BACKOFF_FACTOR = 2

    retries = 0
    while retries < MAX_RETRIES:
        try:
            
            time.sleep(1)
            resp = requests.get(endpoint, params={"query": query}, headers=headers, timeout=30)
            time.sleep(1)
            resp.raise_for_status()

            data = resp.json()

            # ASK returns a boolean instead of bindings
            if "boolean" in data:
                answer_bool = data["boolean"]
                if answer_bool:
                    answer = ["ja"]
                else:
                    answer = ["nee"]
                return answer

            answers = [row["answerLabel"]["value"]
                    for row in data["results"]["bindings"]
                    if "answerLabel" in row]

            return answers
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429: # Check for "Too Many Requests" error
                retries += 1
                if retries < MAX_RETRIES:
                    delay = INITIAL_BACKOFF_DELAY * (BACKOFF_FACTOR ** (retries - 1))
                    print(f"DEBUG: Rate limit hit (429). Retrying in {delay} seconds (Attempt {retries}/{MAX_RETRIES})...")
                    time.sleep(delay)
                else:
                    print(f"DEBUG: Max retries ({MAX_RETRIES}) exceeded for query. Skipping.")
                    raise
            else:
                # Re-raise other HTTP errors
                raise


def process_questions(qtype, entity_ids, property_ids, constructor_func, value_ids=None, include_values=False):
    """Constructing queries and testing them for answers for all 3 question types.
    repeat for eveery combination of property (and value for yes/no) until answer is found.

    Returns new dicts with answers added only including questions with sucesfull answers.
    """
    answer_found = None
    if qtype == 'YESNO':
        if include_values: # qualified statement is needed
            for entity_id in entity_ids[:5]:
                for prop_id in property_ids[:5]:
                    for val_id in value_ids[:5]:
                        query = constructor_func(prop_id, entity_id, val_id)
                        answer = run_query(query)
                        ##print(f"answer:{answer}")
                        if answer == ["ja"]:  # keep trying until answer is "ja"
                            answer_found = answer
                            break
                    if answer_found:
                        break
                if answer_found:
                    break
            if not answer_found:  # if all the combination didn't yield a "ja" then set answer_found to "nee"
                    answer_found = ["nee"]
        else: # no qualified statement needed
            for entity_id in entity_ids:
                for prop_id in property_ids:
                    query = constructor_func(prop_id, entity_id)
                    answer = run_query(query)
                    ##print(f"answer:{answer}")
                    if answer == ["ja"]:  # keep trying until answer is "ja"
                        answer_found = answer
                        break
                    if answer_found:
                        break
                if answer_found:
                    break
                if not answer_found:  # if all the combination didn't yield a "ja" then set answer_found to "nee"
                        answer_found = ["nee"]
    else: # For Wie/Wat and Hoe/Hoeveel questions
        for entity_id in entity_ids:
            for prop_id in property_ids:
                query = constructor_func(prop_id, entity_id)
                answer = run_query(query)
                if answer:
                    answer_found = answer
                    break
            if answer_found:
                break
            
    return answer