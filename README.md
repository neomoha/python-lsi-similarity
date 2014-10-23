Document (Term) Similarity using Latent Semantic Indexing
======

A small code in python to compute semantic similarity between documents (or items) using Latent Semantic Indexing (LSI)

Dependencies
------

* [numpy](https://pypi.python.org/pypi/numpy)
* [scipy](https://pypi.python.org/pypi/scipy)
* [gensim](https://pypi.python.org/pypi/gensim)

To install them, just type: **pip install -U numpy scipy gensim**

How to use this code
------

* There is an example dataset of artists and tags (crawled from Last.fm back in 2009) included in the compressed file [data.tar.bz2](https://github.com/neomoha/python-lsi-similarity/blob/master/data.tar.bz2).
Just uncompress it and you will be able to run a demo that computes similarity between tags.

* The file [config.py](https://github.com/neomoha/python-lsi-similarity/blob/master/config.py) includes the default configuration to run the demo in [model.py](https://github.com/neomoha/python-lsi-similarity/blob/master/model.py). The two required documents for the model to work are:
  * A dictionary file, *data/lastfm_artists.txt*, which includes the names of the items (artists in this case), one item per line.
  * A corpus file, *data/lastfm_tags_artists.tsv*, which includes a document name (tag) and its list of items (artists) with their corresponding normalized weights
  ```
     document_name[TAB][(item_name1, weight1), (item_name2, weight2), ...]
  ```

* The previous configuration is set up to provide tag similarity. If you want artist similarity instead, you just have to use the files *data/lastfm_tags.txt* and *data/lastfm_artists_tags.tsv*, respectively.

* You can also use your own dataset. However, you must follow the exact format as the previoussly mention sample files.
Hopefully in the future I'll make the code more flexible so that you can use your own format.

* The rest of the configuration options for the demo are already explained in the script [model.py](https://github.com/neomoha/python-lsi-similarity/blob/master/model.py), in the main function below.

* There is however another script called [cleaner.py](https://github.com/neomoha/python-lsi-similarity/blob/master/cleaner.py).
  In the case of tags, it was necessary to write some code to clean the very noisy tag dataset from Last.fm.
  By default the DefaultCleaner will be called while running the demo at model.py. This cleaner actually just checks if the input document name is a string or not.
  In the case of tags, I used TagCleaner to clean the dataset, and thus is also needed to query the dataset. 

Examples
------

### Help

```
$ python model.py -h
```

### Tag similarity

#### Similar tags to a given tag

```
$ python model.py "Italian Rap" -s 10 -c TagCleaner
('rapitaliano', 0.99289674)
('hiphopitaliano', 0.9866116)
('italianhiphop', 0.98450512)
('rapitalian', 0.94187772)
('ithiphop', 0.93498826)
('areacronica', 0.92992383)
('raphardcore', 0.9299171)
('nelvortice', 0.90312099)
('tormento', 0.89701408)
('soulville', 0.89118701)

$ python model.py "calm" -s 10 -n 200 -c TagCleaner
('mellow', 0.87416512)
('soothing', 0.87190253)
('soft', 0.86796957)
('melancholy', 0.85312933)
('gentle', 0.85238552)
('sad', 0.83518672)
('reflective', 0.83046651)
('quiet', 0.83010238)
('calming', 0.82065952)
('intimate', 0.81874591)

$ python model.py "Acid House" -s 5 -n 50 -c TagCleaner
('godfathersofhouseandtechno', 0.92068398)
('italohouse', 0.9116993)
('detroithouse', 0.89956081)
('digipunk', 0.89837003)
('progresivehouse', 0.89674282)

$ python model.py "Acid House" -s 5 -n 100 -c TagCleaner
('godfathersofhouseandtechno', 0.91140896)
('myrootsinelectronicmusic', 0.88002872)
('nuhouse', 0.86712235)
('houseartist', 0.86652893)
('funkyelectro', 0.86088693)

$ python model.py "Acid House" -s 5 -n 200 -c TagCleaner
('godfathersofhouseandtechno', 0.85408849)
('afrofuturism', 0.8189801)
('electronicdancemusic', 0.77227825)
('hiphouse', 0.76878512)
('wbmx', 0.75617921)
```

#### Similarity between two tags

```
$ python model.py "Acid House" -p "House" -c TagCleaner
0.860134568029

$ python model.py "Acid House" -p "Jazz" -c TagCleaner
0.0198018934176

$ python model.py "heavy metal" -p "calm" -c TagCleaner
-0.00130043656911

$ python model.py "classical music" -p "party" -c TagCleaner
0.0144112308305

$ python model.py "dance" -p "party" -c TagCleaner
0.804738605955
```


