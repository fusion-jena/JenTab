# Autocorrect
 
Util Service tries to solve the problem of miss-spelled words. Runs at :5005

## Endpoints

### `POST /correct_cell`


**Parameters**
* `text` ... string value.

### `POST /correct_cell`
**Parameters**
* `texts` ... list of string values.

## How it works?
* Based on the select configuration, set in the [config.py](/config.py), it will try to suggest the autocorrected word for a given string.
* Supported configurations:
    * ENABLE_MODELBASED_CORRECTIONS: tries to predict the autocorrected word based on 1-edit distance algorithm and Word2Vec model
    * ENABLE_OFF_THE_SHELF_CORRECTIONS: outputs the corrected word by **autocorrect** python library

## References 
* [Word2Vec spell checker](https://www.kaggle.com/cpmpml/spell-checker-using-word2vec)
* [autocorrect pylib](https://pypi.org/project/autocorrect/)
