import json
import os

import spacy
import requests
import time

def get_named_entity(str_question, nlp):
    url = 'https://www.wikidata.org/w/api.php'
    parse = nlp(str_question)
    parsed_entity = ""
    for ent in parse.ents :
        parsed_entity = ent.text # This is bad, but we only assume 1 person in the question right now.
    
    # String cleanup
    if parsed_entity[-2:] == "'s":
        parsed_entity = parsed_entity[:-2]
    
    params = {'action':'wbsearchentities', 
              'language':'nl',
              'uselang':'nl',
              'format':'json'}
    params['search'] = parsed_entity
    json = requests.get(url,params).json()
    try:
        person_id = json['search'][0]['id']
    except KeyError:
        print("KEYERROR:", str_question)
        person_id = None
    except IndexError:
        print("ERROR: NO ID FOUND WHILE THERE WAS A NAMED ENTITY:", parsed_entity)
        person_id = None
    
    return person_id


def determine_answer(qa_question, nlp):
    # print(qa_question)
    person_id = get_named_entity(qa_question, nlp)
    # print(person_id)


def main():
    # Load dependencies
    nlp = spacy.load("nl_core_news_lg") # this loads the (large) model for analysing Dutch text
    url = 'https://www.wikidata.org/w/api.php'

    # Load JSON
    filepath = "data/all-questions.json"
    with open(filepath, "r") as file:
        data = json.load(file)
    
    # Loop over all the questions in the file
    for item in data:
        qa_question = item["string"]
        qa_true = item["answer"][0]["string"]
        determine_answer(qa_question, nlp)


if __name__ == "__main__":
    main()