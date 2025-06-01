QUESTION_TYPE = {
    "wat": "WH_",
    "wie": "WH_",
    "hoe": "HOW",
    "hoeveel": "HOW",
}

YESNO_STARTERS = {
    "is", "was", "zijn", "waren",
    "heeft", "hebben", "had", "hadden",
    "wordt", "worden", "werd", "werden",
}

GENDER_NOUNS = {"man", "vrouw", "jongen", "meisje"}

# Helper functions
# ------------------------------------------------------------------

def root(doc):
    for t in doc:
        if t.dep_ == "ROOT":
            return t
    return doc[0]

def first_non_space(doc):
    """Return lemma of first non‑space token in doc."""
    for t in doc:
        if not t.is_space:
            return t.lemma_.lower()
    return ""


def noun_chunk_of(token):
    """Return noun‑chunk surrounding token filtering out determines."""
    if token is None:
        return ""
    for chunk in token.doc.noun_chunks:
        if chunk.start <= token.i < chunk.end:
            # Exclude determiners
            filtered = [t.text for t in chunk if t.pos_ != "DET"]
            return " ".join(filtered)
    return token.text


def name_span(token):
    """Return full proper‑name around token using dependency subtree."""
    if token is None:
        return ""
    full_name = [d.text for d in token.subtree if d.pos_ == 'PROPN']
    return " ".join(full_name)

def identity_question(token):
    """Return True if property/root is a noun and head of the nsubj."""
    if token.pos_ == 'NOUN':
        for child in token.children:
            if child.dep_ == 'nsubj':
                return True
    return False


def question_type(question, first):
    """Return the type of question based on the first non-whitespace character"""
    if first in YESNO_STARTERS:
        qtype = "YESNO"
    else:
        qtype = QUESTION_TYPE.get(first, "OTHER")
    return qtype

def is_number(token):
    """Simple function that checks if token is a number or not"""
    try:
        float(token)
        return True
    except ValueError:
        return False
    