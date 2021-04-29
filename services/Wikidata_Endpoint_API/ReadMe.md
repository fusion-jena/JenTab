# Wikidata Endpoint Service

This service provides the proxy to Wikidata's SPARQL endpoint.

## Quick Setup 

* ```hypercorn main:app -c python:asgi_config.py```

## Endpoints

| Name                                          | Type | Data   (type)                                  | Description |
|-----------------                              |------|-----------                                     |----------------|
| `get_type_for`                                | POST | `text` (string)                                | retrieve all classes for the entity given by  "**text**" |
| `get_type_for_lst`                            | POST | `texts` (list of strings)                      | retrieve all classed for the entities given by "**texts**" |
| `get_subclasses_for`                          | POST | `wikiclass` (string)                           | retrieve subclasses for the entity given by "**wikiclass**" |
| `get_parents_for`                             | POST | `wikiclass` (string)                           | retrieve superclasses for the entity given by "**wikiclass**" |
| `get_connection_for`                          | POST | `subWikiId` (string) & `objWikiId` (string)    | retrieve properties (direct and parents) between the given subj and obj |
| `get_connection_for_lst`                      | POST | `subWikiId` (string) & `objWikiId` (string)    | retrieve properties (direct and parents) between the given subj and obj |
| `get_{literals|objects|properties}_for`       | POST | `text` (string)                                | retrieve {literal|object|all} properties for for the entity given by "**text**"; generic version |
| `get_{literals|objects|properties}_for_lst`   | POST | `texts` (list of strings)                      | retrieve {literal|object|all} properties for for the entities given by "**texts**"; generic version |
| `get_{literals|objects|properties}_{topranked|full}_for`       | POST | `text` (string)               | retrieve {top-ranked|all} {literal|object|all} properties for for the entity given by "**text**" |
| `get_{literals|objects|properties}_{topranked|full}_for_lst`   | POST | `texts` (list of strings)     | retrieve {top-ranked|all} {literal|object|all} properties for for the entities given by "**texts**" |
| `get_strings_for`                             | POST | `text` (string)                                | retrieve string properties for for the entity given by "**text**" |
| `get_strings_for_lst`                         | POST | `texts` (list of strings)                      | retrieve string properties for for the entities given by "**texts**" |


Term(s) has to be provided form-encoded using above parameters.

### Output format

* Provided input entities are used as keys in a dictionary.
* Value is an array of results.

```json
{
  "[entity]": [ ... ]
}
```

Structure of entries varies by query:

**type**

```json
{ "class": "https://www.wikidata.org/wiki/Q123", "classLabel": "some label" }
```

**subclass**

```json
{ "subclass": "https://www.wikidata.org/wiki/Q123", "subclassLabel": "some label" }
```

**parents**

```json
{ "superclass": "https://www.wikidata.org/wiki/Q123", "superclassLabel": "some label" }
```

**connections**
```json
{
    "Q188370,Q37836": [
        {
            "pParent": "http://www.wikidata.org/entity/P361",
            "pParentLabel": "part of"
        }, { ... }
    ]
}
```

**literals / objects / strings / properties**
```json
{
    "Q188": [
        {
          "datatype": "langString",
          "prop": "http://schema.org/description",
          "value": "westgermanische Sprache",
          "wikitype": "Monolingualtext"
        }, {
          "datatype": "IRI",
          "prop": "http://www.wikidata.org/prop/direct/P17",
          "value": "http://www.wikidata.org/entity/Q38",
          "wikitype": "WikibaseItem"
        }, {
          "datatype": "langString",
          "prop": "http://www.w3.org/2000/01/rdf-schema#label",
          "value": "German",
          "wikitype": "Monolingualtext"
        }, { ... }
    ]
}
```

## Configuration

Environment variables for configuration (can also be set via docker-compose.yml):

| Name                  | Default | Description                                                                |
|-----------------------|---------|----------------------------------------------------------------------------|
| MAX_PARALLEL_REQUESTS | 5       | maximum number of parallel requests. Used to prevent IP-bans from Wikidata |
| DEFAULT_DELAY         | 10      | default delay upon HTTP error (429, 500, ...); in seconds                  |
| MAX_RETRIES           | 5       | maximum number of retries upon HTTP errors                                 |
| CACHE_DISABLED        | False   | disabled caching of Wikidata responses                                     |
