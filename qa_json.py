import json
import os

import spacy
import requests
import time

import qa_question_types as qu


def get_property_ids(str_question, nlp):
    url = 'https://www.wikidata.org/w/api.php'
    parse = nlp(str_question)
    property_id = ""
    
    qword_index = -1
    enum_index = 0
    
    for chunk in parse:
        if chunk.pos_ == "ADV":
            qword_index = enum_index
        elif chunk.pos_ == "NUM" and qword_index == -1:
            qword_index = enum_index
        elif "wie" in chunk.lemma_ or "wat" in chunk.lemma_:
            qword_index = enum_index
        enum_index += 1
    
    if qword_index == -1:
        return None
    
    match parse[qword_index].lemma_:
        case "waar":
            property_id = qu.question_waar(parse, url)
        case "hoeveel":
            property_id = qu.question_hoeveel(parse, url)
            extra_mode = 1
        case "wie":
            property_id = qu.question_wie_wat(parse, url)
        case "wat":
            property_id = qu.question_wie_wat(parse, url)
    
    if property_id == "":
        return None
    
    return property_id


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
        print("KEYERROR (no named entity):", str_question)
        person_id = None
    except IndexError:
        print("ERROR: NO ID FOUND WHILE THERE WAS A NAMED ENTITY:", parsed_entity)
        person_id = None
    
    return person_id


def determine_answer(qa_question, nlp):
    print(qa_question)
    person_id = get_named_entity(qa_question, nlp)
    list_property_ids = get_property_ids(qa_question, nlp)
    print("IDS", person_id, list_property_ids)
    print()


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