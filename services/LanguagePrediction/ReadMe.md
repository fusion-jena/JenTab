# Language Prediction

* Predicts a language for a given text or list of texts using fasttext library

## Quick Setup

* Linux: ```gunicorn --config ./gunicorn.py --preload wsgi:app```
* Windows: 
	* ```python main.py```	
	
## Endpoints

| Name                                          | Type | Data   (type)                                  | Description |
|-----------------                              |------|-----------                                     |----------------|
| `get_language`                                | POST | `text` (string)                                | predicts the language for the entity given by  "**text**" |
| `get_language_lst`                            | POST | `texts` (list of strings)                      | predicts the language for the entities given by "**texts**" |
