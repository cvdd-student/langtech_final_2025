import spacy

import qa_json as qa


def main():
    # Load dependencies
    nlp = spacy.load("nl_core_news_lg") # this loads the (large) model for analysing Dutch text
    
    # Loop flag
    flag_exit = False
    
    # While loop to keep querying
    while flag_exit is False:
        qa_question = input("Give the question. ")
        if qa_question == "":
            flag_exit = True
        else:
            list_answers = qa.determine_answer(qa_question, nlp)
            print(list_answers)
    
if __name__ == "__main__":
    main()