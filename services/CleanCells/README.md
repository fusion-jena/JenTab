# CleanCells
 
* Util Service tries to clean and fix cell values. 
* Runs at: 5001

## Endpoints

### `POST /fix_cell_lst`


**Parameters**
* `cells` ... list of string values.

### `POST /specific_clean_cell_lst`
**Parameters**
* `cells` ... list of string values.
* `coltype` ... primitive column type (string). Supported types are:
    * OBJECT
    * DATE
    * QUANTITY

## How it works?
* The first API `fix_cell_lst` tries to handle missing values 
    * i.e., `NaN` and `?` or `-` ... etc.
    * The most important values are kept.
* The second API `specific_clean_cell_lst` tries to normalize the given cells, thus extracts the useful values from a given string
    * i.e., DATE:
        * 2011-11-29 November 29 => 2011-11-29
    * i.e., QUANTITY:
        * 1,025 m (3,363 ft) => 1025
    * Normalized values are easier to match with knowledge graph values.

## Configuration

| Name                  | Default | Description                                                                |
|-----------------------|---------|----------------------------------------------------------------------------|
| normalization | 'NFKC'       | fix text for you (ftfy) parameter. This covered a lot of helpful fixes at once, such as expanding ligatures and replacing “fullwidth” characters with their standard form. |

* Consider change this NFKC to NFC in the [latest release](https://ftfy.readthedocs.io/en/latest/)