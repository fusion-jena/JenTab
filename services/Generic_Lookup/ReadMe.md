# Generic Lookup Service

Provides access to a prepopulated cache for label to candidate mappings.

## Endpoints

| Name            | Type | Data   (type)              | Description |
|-----------------|------|-----------                 |----------------|
| look_for        | POST | needle (string)            | looks up in the cache for a single query element given by "**needle**"|
| look_for_lst    | POST | needles (list of strings)  | hits the Wikidata lookup API given a list of queries "**needles**" |


Term(s) has to be provided form-encoded using the parameter `text`.

**Output format**

* Provided input terms are used as keys in a dictionary.
* Each term might have multiple mappings

```json
{
  "[term]": [{
    "label": "Label of the entitiy",
    "uri":   "URI of the respective entity"
  }, ...
  ]
}
```

## Configuration

