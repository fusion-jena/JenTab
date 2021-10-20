# Wikidata Proxy Service

This service provides the proxy to Wikidata KG (Lookup API + Sparql Endpoint)

## Quick Setup 

* ```hypercorn main:app -c python:asgi_config.py```


## Endpoints
| Type  | Name                                          | Type | Data   (type)                                  | Description |
|---|-----------------                              |------|-----------                                     |----------------|
|Lookup| `look_for`        | POST | text (string)            | looks up the Wikidata lookup API for a single query element given by "**text**"|
|Lookup| `look_for_lst`    | POST | texts (list of strings)  | hits the Wikidata lookup API given a list of queries "**texts**" |
|Endpoint| `get_type_for`                                | POST | `text` (string)                                | retrieve all classes for the entity given by  "**text**" |
|Endpoint| `get_type_for_lst`                            | POST | `texts` (list of strings)                      | retrieve all classed for the entities given by "**texts**" |
|Endpoint| `get_subclasses_for`                          | POST | `wikiclass` (string)                           | retrieve subclasses for the entity given by "**wikiclass**" |
|Endpoint| `get_parents_for`                             | POST | `wikiclass` (string)                           | retrieve superclasses for the entity given by "**wikiclass**" |
|Endpoint| `get_connection_for`                          | POST | `subWikiId` (string) & `objWikiId` (string)    | retrieve properties (direct and parents) between the given subj and obj |
|Endpoint| `get_connection_for_lst`                      | POST | `subWikiId` (string) & `objWikiId` (string)    | retrieve properties (direct and parents) between the given subj and obj |
|Endpoint| `get_{literals-objects-properties}_for`       | POST | `text` (string)                                | retrieve {literal|object|all} properties for for the entity given by "**text**"; generic version |
|Endpoint| `get_{literals-objects-properties}_for_lst`   | POST | `texts` (list of strings)                      | retrieve {literal|object|all} properties for for the entities given by "**texts**"; generic version |
|Endpoint| `get_{literals-objects-properties}_{topranked|full}_for`       | POST | `text` (string)               | retrieve {top-ranked|all} {literal|object|all} properties for for the entity given by "**text**" |
|Endpoint| `get_{literals-objects-properties}_{topranked|full}_for_lst`   | POST | `texts` (list of strings)     | retrieve {top-ranked|all} {literal|object|all} properties for for the entities given by "**texts**" |
|Endpoint| `get_strings_for`                             | POST | `text` (string)                                | retrieve string properties for for the entity given by "**text**" |
|Endpoint| `get_strings_for_lst`                         | POST | `texts` (list of strings)                      | retrieve string properties for for the entities given by "**texts**" |


Term(s) has to be provided form-encoded using above parameters.

### Lookup Output format

```json
{
  "[term]": [{
    "label": "Label of the entitiy",
    "uri":   "URI of the respective entity"
  }, ...
  ]
}
```


### Endpoint Output format

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
