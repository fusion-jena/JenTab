# Autocorrect
 
Util Service tries to solve the problem of miss-spelled words based on the enabled modes in the [/config.py](/config.py). Runs at :5005

## Endpoints

### `POST /correct_cell`


**Parameters**
* `text` ... string value.

### `POST /correct_cell_lst`
**Parameters**
* `texts` ... list of string values.

## Configurations
* ENABLE_MODELBASED_CORRECTIONS: (**recommended**) 
    * tries to predict the autocorrected word based on 1-edit distance algorithm and Word2Vec model
    * Download [GoogleNews-vectors-negative300.bin](https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz)
    * Unzip
    * Locate under: [/assets/autocorrect/GoogleNews-vectors-negative300.bin](/assets/autocorrect/GoogleNews-vectors-negative300.bin)
* ENABLE_OFF_THE_SHELF_CORRECTIONS: (default) outputs the corrected word by **autocorrect** python library

## References 
* [Word2Vec spell checker](https://www.kaggle.com/cpmpml/spell-checker-using-word2vec)
* [autocorrect pylib](https://pypi.org/project/autocorrect/)
