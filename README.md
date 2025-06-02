# langtech_final_2025

A Question Answering system that processes Dutch questions, queries Wikidata, and returns answers.

## Features

* Parses natural language questions in Dutch.
* Identifies entities, properties and optionally values within questions.
* Constructs SPARQL queries for Wikidata.
* Retrieves and presents answers.
* Includes an interactive mode for user queries and a batch processing mode for JSON datasets.

## Main Scripts

* `qa_interactive.py`: Runs the system in interactive mode.
* `qa_json.py`: Processes questions from a JSON file (`data/all-questions.json`) and outputs results to `output.json`.

## Setup

Requires Python and SpaCy with the `nl_core_news_lg` model.