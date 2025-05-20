def get_property_ids(str_question):
    extra_mode = 0 # 0 = none, 1 = count
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
        return
    match parse[qword_index].lemma_:
        case "waar":
            property_id = question_waar(parse)
        case "hoeveel":
            property_id = question_hoeveel(parse)
            extra_mode = 1
        case "wie":
            property_id = question_wie_wat(parse)
        case "wat":
            property_id = question_wie_wat(parse)

    return property_id, extra_mode


def question_waar(parsed_question):
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
        return

    params = {'action':'wbsearchentities', 
              'language':'nl',
              'uselang':'nl',
              'format':'json',
              'type':'property'}
    params['search'] = parsed_property
    json = requests.get(url,params).json()

    if json['search'] == []:
        print("NO PROPERTIES FOUND")
        return
    
    for item in json['search']:
        if "plaats" in item['description']:
            found_id = item['id']
        elif "waar " in item['description']:
            found_id = item['id']

    if found_id == "":
        print("NO ID FOUND OOPS")
        return

    return [found_id]


def question_hoeveel(parsed_question):
    parsed_property = ""
    found_id = ""
    for chunk in parsed_question:
        if chunk.pos_ == "NOUN":
            parsed_property = chunk.lemma_

    if parsed_property == "":
        print("CRITICAL ERROR")
        return
    
    params = {'action':'wbsearchentities', 
              'language':'nl',
              'uselang':'nl',
              'format':'json',
              'type':'property'}
    params['search'] = parsed_property
    json = requests.get(url,params).json()
    
    if json['search'] == []:
        print("NO PROPERTIES FOUND")
        return

    list_possible_ids = []
    for item in json['search']:
        list_possible_ids.append(item['id'])

    return list_possible_ids


def question_wie_wat(parsed_question):
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
    params['search'] = parsed_property
    json = requests.get(url,params).json()
    list_possible_properties = []
    for item in json['search']:
        list_possible_properties.append(item['id'])
    
    return list_possible_properties