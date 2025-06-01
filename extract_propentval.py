import utils as ut



#  Wat / Wie helpers
# ------------------------------------------------------------------

def extract_wh_property_token(doc):
    # Property noun is nsubj governed by Wat/Wie
    for tok in doc:
        if tok.dep_ == "nsubj" and tok.head.lemma_.lower() in ("wat", "wie"):
            return tok
    # Property noun itself is sentence ROOT
    for tok in doc:
        if tok.dep_ == "ROOT" and tok.pos_ == "NOUN":
            return tok
    return None


def extract_wh_entity(doc, prop_tok):
    """Return entity."""
    if prop_tok is None:
        return ""

    ent_token = None

    # entity as head of nmod dep_ tag attached to property
    for child in prop_tok.children:
        if child.dep_ == "nmod":
            for t in child.subtree:
                if t.pos_ == "PROPN":
                    ent_token = t
                    break
        if ent_token is not None:
            break

    # appositive / flat name inside same subtree (e.g. Rapper Boef)
    if ent_token is None:
        for t in prop_tok.subtree:
            if t.pos_ == "PROPN":
                ent_token = t
                break

    # Fall-back that just select the first PROPN in the sentence.
    if ent_token is None:
        for t in doc:
            if t.pos_ == "PROPN":
                ent_token = t
                break

    return ut.name_span(ent_token)


#  Hoe / Hoeveel helpers
# ------------------------------------------------------------------


def extract_how_property_token(doc):
    r = ut.root(doc)

    # predicate adjective is the root  (e.g. Hoe lang)
    if r.pos_ == "ADJ":
        return r

    # adjectival complement of a verbal root (e.g. Hoe oud was ... geworden?)
    for child in r.children:
        if child.pos_ == "ADJ" and child.dep_ in ("xcomp", "acomp"):
            return child

    # noun that is the subject of the clause
    for tok in r.subtree:
        if tok.dep_ == "nsubj" and tok.pos_ == "NOUN":
            return tok        # hits “liedjes”, “kabinetten”, “leden”

    # object / oblique noun (goals, kinderen, medailles, …)
    for tok in r.subtree:
        if tok.dep_ in ("obj", "obl") and tok.pos_ == "NOUN":
            return tok

    # fallback
    return r


def extract_how_entity(doc, prop_tok=None):
    r = ut.root(doc)

    # direct subject of the root
    for child in r.children:
        if child.dep_ == "nsubj":
            return ut.name_span(child)

    # subject on AUX children
    for aux in (c for c in r.children if c.pos_ == "AUX"):
        for ch in aux.children:
            if ch.dep_ == "nsubj":
                return ut.name_span(ch)

    # subject on deeper AUX
    for aux in (t for t in r.subtree if t.pos_ == "AUX"):
        for ch in aux.children:
            if ch.dep_ == "nsubj":
                return ut.name_span(ch)

    # entity in nmod/obl attached to the property token
    if prop_tok is not None:
        for child in prop_tok.children:
            if child.dep_ in ("nmod", "obl"):
                for t in child.subtree:
                    if t.pos_ == "PROPN":
                        return ut.name_span(t)

    return ""



# Yes/No helpers
# ------------------------------------------------------------------

def extract_yesno_property_token(doc):
    r = ut.root(doc)
    # copular: root is noun/adj property is that head
    if r.pos_ in ("NOUN", "ADJ", "Verb"):
        return r
    # otherwise take the main verb (root)
    return r


def extract_yesno_entity(doc):
    r = ut.root(doc)
    # look for any nsubj*/nsubj:pass in the clause
    for tok in r.subtree:
        if tok.dep_.startswith("nsubj"):
            return ut.name_span(tok)
    return ""


def extract_yesno_value(doc, prop_tok):
    """Return the object/location/date phrase that acts as qualifier and value_type (entity or property)"""
    value_type = 'entity' # Need this to determine if I need to use prop_id_finder or ent_id_finder # hmm maybe entity is the better choice in general
    if prop_tok is None:
        return "", value_type
    # direct obj
    for child in prop_tok.children:
        if child.dep_ == "obj":
            if child.pos_ in ("PROPN","NOUN"):
                value_type = 'entity'
            return ut.noun_chunk_of(child), value_type
    # prepositional modifier (obl/nmod) holding a date/place etc.
    full_phrase = []
    for child in prop_tok.children:
        if child.dep_ in ("obl", "nmod"):
            # return the whole phrase text and value_type
            for d in child.subtree:
                if d.pos_ not in ('ADP', 'DET'):
                    full_phrase.append(d.text)
                    if d.pos_ in ('PROPN','NOUN'): # e.g. Amsterdam
                        value_type = 'entity'
            return " ".join(full_phrase), value_type
    return "", value_type

def which_extractor(doc):
    ent_list = []
    prop_list = []

    # turns entities object into a mutable list of strings
    for ent in doc.ents:
        ent_list.append(str(ent))

    # removes adjectives from entities list
    for word in doc:
        if word.pos_ in 'ADJ' and str(word) in str(doc.ents):
            ent_list.remove(str(word))

    # sets sentence object as property
    for word in doc:
        if word.dep_ == "obj":
            prop_list.append(str(word))

    # sets 'nsubj' as property if no sentence object was found
    if prop_list == []:
        for word in doc:
            if "nsubj" in word.dep_:
                prop_list.append(str(word))

    # removes year and the word 'Nederland' from entity list
    # adds year to val_list
    for word in ent_list:
        if word.isnumeric():
            ent_list.remove(word)
            year_list.append(word)
        elif word == 'Nederland':
            ent_list.remove(word)

    for word in doc:
        if str(word) == 'geboren':
            prop_list[0] = 'geboorteplaats'
        elif str(word) in 'overleden, gestorven, vermoord':
            prop_list[0] = 'sterfdatum'

    if prop_list == [] and ent_list == []:
        return "", ""
    elif prop_list == [] and ent_list != []:
        return "", ent_list[0]
    elif prop_list != [] and ent_list == []:
        return prop_list[0], ""
    else:
        return prop_list[0], ent_list[0]


#  Wrapper function
# ------------------------------------------------------------------

def parse_question(doc):
    value_type = None
    first = ut.first_non_space(doc)

    qtype = ut.question_type(doc, first)
    #print(qtype)

    if qtype == "WH_":
        prop_tok = extract_wh_property_token(doc)
        entity_text = extract_wh_entity(doc, prop_tok).strip()
        property_text = ut.noun_chunk_of(prop_tok).strip()
        value_text = ""

    elif qtype == "HOW":
        prop_tok = extract_how_property_token(doc)
        entity_text = extract_how_entity(doc, prop_tok).strip()
        property_text = ut.noun_chunk_of(prop_tok).strip()
        value_text = ""
        if property_text == "lang":  # Wiki label API doesn't list correct property id
            property_text = "hoogte"

    elif qtype == "WHICH":
        property_text, entity_text = which_extractor(doc)
        value_text = ""

    elif qtype == "YESNO":
        prop_tok = extract_yesno_property_token(doc)
        entity_text = extract_yesno_entity(doc).strip()
        property_text = ut.noun_chunk_of(prop_tok).strip()
        value_text, value_type = extract_yesno_value(doc, prop_tok)
        value_text = value_text.strip()

        # To handle a specific type of yes/no question: identity questions
        if ut.identity_question(prop_tok) and first == "zijn":
            value_text = property_text
            #  Converting some common mismatches between api and actual text
            if value_text == "vrouw":
                value_text = "vrouwelijk"
            if prop_tok.text in ut.GENDER_NOUNS:
                property_text = "geslacht"
            elif prop_tok.text.startswith("vege"):
                property_text = "lifestyle"
            elif property_text == "lang":
                property_text = "hoogte"
            elif property_text == "echte naam":
                property_text == "geboortenaam"
            else:
                property_text = "beroep"
    else:
        return {"qtype": qtype, "value_type": None, "property": None, "entity": None, "value": None}
    if value_type is None:  # value_type is only set for yes/no questions so need to set it the default otherwise value_type is not defnined.
        value_type = "property"
    return {"qtype": qtype, "value_type": value_type, "property": property_text, "entity": entity_text, "value": value_text}
