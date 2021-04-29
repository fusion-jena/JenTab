# Supported Primitive Types

## Quick Setup

* Linux: ```gunicorn --config ./gunicorn.py --preload wsgi:app```
* Windows: 
	* ```python -m spacy download en``` (once)
	* ```python main.py```	

This is a list of all supported primitive types by TypePrediction Service. We support 20 different types by using a combination between rule-based approach or regular expressions and [spaCy model](https://github.com/explosion/spaCy). A list of the supported named entities by spaCy is found [here](https://spacy.io/api/annotation#named-entities)

## OBJECT
* This type represents the entities that will have entity mentions in the corresponding knowledge graph.
* Baseline_Approach uses this type to generate cell mappings automatically without looking at the given `targets`.

## OTHER
* Lengthy description cells are classified as OTHER, we can say long Object values are others.

## DECIMAL
* It covers both INT and FLOAT in the form of numbers i.e., `38` and `40.5`.

## NUMERAL
* Looks for words that represents a number i.e., `eighty eight`.

## ORDINAL
* Another number handler, it capture ranking format like `1st` and `23rd`.

## PHONE
* Captures a range of phone numbers i.e., `+49 176 1234 5678` and `+1 (650) 123-4567`.

## BOOL
* Looks for 3 cases of boolean values `(yes & no)`, `(true & false)` and `(right & wrong)`.

## URL
* A standard URL format.

## EMAIl
* A standard e-mail format.

## VOLUME
* A combination between decimal and volume unit i.e., `1 cubic metre`
* Maps to **Quantity** in Wikidata Supported types

## DISTANCE
* A combination between decimal and distance unit i.e., `18Km` and `50 mm`
* Maps to **Quantity** in Wikidata Supported types

## TEMPRATURE
* A combination between decimal and temprature unit i.e., `18 Kelvin`
* Maps to **Quantity** in Wikidata Supported types

## MONEY
* spaCy type
* Monetary values, including unit.
* Maps to **Quantity** in Wikidata Supported types

## QUANTITY
* Represents digital file size i.e., `2 MB`
* Maps to **Quantity** in Wikidata Supported types

## DURATION
*  A combination between decimal and time duration unit i.e., `1 min` and `2 days`

## LOCATION
* Represents the Geo location i.e., `+90.0, -127.554334`
* Validates the range of longtitue and latitude 
* Maps to **Globe coordinate** in Wikidata Supported types

## PERCENT
* spaCy type
* Percentage, including `%`.

## TIME
* spaCy type
* Maps to **Time** in Wikidata Supported types

## DATE
* Capture standard format for dates and also fuzzy dates like (today morning)
* Maps to **Time** in Wikidata Supported types

