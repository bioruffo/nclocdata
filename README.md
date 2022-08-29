# nclocdata
Scrape and use Nexus Clash location data.

## Dependencies
* pandas
* bs4
* pyperclip

## Basic usage:

### To download all the current location webpages (prerequisite for all other operations):

`python -m nclocdata -d`

### To get drop rates for a specific item, in the most fruitful 10 locations:

`python -m nclocdata -s "Item Name" -c 10`

### To get the cumulative drop rates of a group of items, best 10 locations:

`python -m nclocdata -f <itemsfile> -c 10`

### To enrich a wiki page with drop rates (3 neatly listed records, 5 one-line mentions):

`python -m nclocdata -w <wikifile> -c 3 -m 5`

Where "wikifile" is a plain text file in wiki format.
By default, drop rates will be added immediately after the "Weight:" line.

### To output a .tsv drop rates table for all locations and items:

`python -m nclocdata -t`

### To locate any item name matching a certain word:

`python -m nclocdata -l word`
