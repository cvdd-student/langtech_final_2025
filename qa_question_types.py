import json
import os

import spacy
import requests
import time

def question_waar(parsed_question, url):
    parsed_property = ""
    found_id = ""
    for chunk in parsed_question:
        if chunk.pos_ == "VERB":
            parsed_property = chunk.text
            # In het geval van woonplaats, die wbsearch blijkbaar heel moeilijk vindt,
            # geef het juiste woord gewoon.
            if chunk.lemma_ == "wonen":
                parsed_property = "woonplaats"

    if parsed_property == "":
        print("CRITICAL ERROR")
        return None

    params = {'action':'wbsearchentities', 
              'language':'nl',
              'uselang':'nl',
              'format':'json',
              'type':'property'}
    params['search'] = parsed_property
    json = requests.get(url,params).json()

    if json['search'] == []:
        print("NO PROPERTIES FOUND")
        return None
    
    for item in json['search']:
        if "plaats" in item['description']:
            found_id = item['id']
        elif "waar " in item['description']:
            found_id = item['id']

    if found_id == "":
        print("ERROR: WAAR DID NOT FIND ANY PROPERTY IDS")
        return None

    return [found_id]


def question_hoeveel(parsed_question, url):
    parsed_property = ""
    found_id = ""
    for chunk in parsed_question:
        if chunk.pos_ == "NOUN":
            parsed_property = chunk.lemma_

    if parsed_property == "":
        print("ERROR: HOEVEEL DID NOT FIND ANY PROPERTIES")
        return None
    
    params = {'action':'wbsearchentities', 
              'language':'nl',
              'uselang':'nl',
              'format':'json',
              'type':'property'}
    params['search'] = parsed_property
    json = requests.get(url,params).json()
    
    if json['search'] == []:
        print("ERROR: HOEVEEL DID NOT FIND ANY PROPERTY IDS")
        return None

    list_possible_ids = []
    for item in json['search']:
        list_possible_ids.append(item['id'])

    return list_possible_ids


def question_wie_wat(parsed_question, url):
    for chunk in parsed_question.noun_chunks:
        if chunk.root.dep_ == "nsubj":
            parsed_property = chunk.root.head.text
            if chunk.root.head.text.lower() == "wie" or chunk.root.head.text.lower() == "wat":
                parsed_property = chunk.root.text
    params = {'action':'wbsearchentities', 
              'language':'nl',
              'uselang':'nl',
              'format':'json',
              'type':'property'}
    try:
        params['search'] = parsed_property
    except UnboundLocalError:
        print("ERROR: WIE/WAT DID NOT FIND ANY PROPERTY IDS")
        return None
    json = requests.get(url,params).json()
    list_possible_properties = []
    for item in json['search']:
        list_possible_properties.append(item['id'])
    
    return list_possible_properties