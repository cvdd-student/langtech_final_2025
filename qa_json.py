import json
import spacy
from utils import is_number
import extract_propentval as epev
from wbsearch import ent_id_finder, prop_id_finder
import query as qy


def main():
    nlp = spacy.load("nl_core_news_lg")
    
    # Load JSON
    filepath = "data/all-questions.json"
    with open(filepath, "r", encoding='utf-8') as file:
        data = json.load(file)
        
    list_out = []
    iter_id = 0
        
    for item in data:
        iter_id += 1
        item_export = dict()
        qa_question = item["string"]
        print(qa_question)
        doc = nlp(qa_question)
        q_info = epev.parse_question(doc) # a dict with question type, value type, entity, property and value
        print(q_info)
        
        if q_info['entity'] and q_info['property']:
            entity_id_matches = [r['id'] for r in ent_id_finder(q_info['entity'])]
            property_id_matches = [r['id'] for r in prop_id_finder(q_info['property'])]
        else:
            entity_id_matches = []
            property_id_matches = []
        
        # branching logic needed to distinghuis between value properties (e.g. politicus) and value entities (e.g. Amsterdam)
        if q_info['value_type'] == "property":  # properties
            value_id_matches = [r['id'] for r in prop_id_finder(q_info['value'])]
        elif q_info['value_type'] == "entity":  # entities
            value_id_matches = [r['id'] for r in ent_id_finder(q_info['value'])]
        else:
            value_id_matches = []
            
        print(entity_id_matches)
        print(property_id_matches)
        print(value_id_matches)

        if entity_id_matches and property_id_matches: # no point runing queries when no entitiy or property id's are found
            # branching logic for queries
            if q_info['qtype'] == 'WH_' or q_info['qtype'] == 'WHICH':
                list_answers = qy.process_questions(q_info['qtype'], entity_id_matches, property_id_matches, qy.query_constructor_wh_how, include_values=False)
            elif q_info['qtype'] == 'HOW':
                list_answers = qy.process_questions(q_info['qtype'], entity_id_matches, property_id_matches, qy.query_constructor_wh_how, include_values=False)
                if (
                    "hoeveel" in qa_question.lower()
                    and isinstance(list_answers, list)
                    and list_answers
                    and not is_number(list_answers[0])  # sometimes the property on wikidata straight up lists the amount so we dont need to count
                    ): #  convert list of answers to number
                    list_answers = [str(len(list_answers))]
            elif q_info['qtype'] == 'YESNO':
                if value_id_matches:
                    list_answers = qy.process_questions(q_info['qtype'], entity_id_matches, property_id_matches, qy.query_constructor_yesno, value_id_matches, include_values=True)
                else:
                    list_answers = qy.process_questions(q_info['qtype'], entity_id_matches, property_id_matches, qy.query_constructor_yesno, include_values=False)
            else:
                list_answers = []
        else:
            list_answers = []
            
        print(list_answers)
        
        # Formatting logic for output json    
        item_export["id"] = iter_id
        item_export["question"] = item["string"]
        if list_answers != [] and list_answers != None:
            item_export["answer"] = ",".join(list_answers)
        else:
            item_export["answer"] = None
        item_export["score"] = 0
        
        list_out.append(item_export)
        iter_id += 1

    # Export file
    json_out = json.dumps(list_out, indent=4)
    with open("output.json", "w", encoding='utf-8') as file:
        file.write(json_out)
        
if __name__ == "__main__":
    main()
            
        
