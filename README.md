# Colexifier

This repo contains a single Python class that you can use to efficiently query the [CLICS2](https://clics.clld.org/) database if you have a local copy.

# Requirements

You need to have Python and `pandas` installed:

```
pip install pandas
```

If you have the Anaconda distribution of Python, `pandas` is already included.

You need to have installed CLICS2, as described in that project's [repository](https://github.com/clics/clics2).

Once you have installed pyclics and downloaded all the data, you can use the `clics` command line tool to create your local copy of the database. This is an `sqlite` database, which exists as a single file on your machine. It will be created in whichever directory you were in, and by default is called `clics.sqlite`.

# Instructions

This repo contains a simple set of helper functions, to let you query `CLICS2` for colexifications of particular concepts. The easiest way to use the functions is to put the `colexifications.py` file from this repository into the same directory as your `clics.sqlite` file. Then open Python in that directory.

To use the functions, you first need to instantiate a `Colexifier` object, which will connect to the database and provide the functionality.
```python
import colexifier as c

col = c.Colexifier()
```
This assumes that your `clics.sqlite` file is in your current working directory. If it is elsewhere on your computer, you can provide a path:
```python
col = c.Colexifier('where/is/clics.sqlite')
```
You can then use the function `search_with_concept` to search for colexifications of a particular concept. The concept must be in the [Concepticon](https://concepticon.clld.org/) vocabulary.
```python
my_colexifications = col.search_with_concept('sibling')
```
If you know the id number of the Concepticon concept, you can simply use that:
```python
# Sibling is concept '1640' in the Concepticon database
my_colexification = col.search_with_id('1640')
```
If you are unsure whether a concept appears in the Concepticon database, you can check with this function:
```python
sibling_id = col.get_concepticon_id('sibling')
sibling_id
[1] '1640'
```
Both `Colexifier.search_with_concept()` and `Colexifier.search_with_id()` return a Pandas DataFrame, making it easy to sort, analyse and export your results. If you wish to save your results at the time you search for them, simply provide a file path to the optional `out` parameter. The results are stored as a csv file:
```python
embers = col.search_with_concept('embers', out = 'bone_colexifications.csv')
body_part = col.search_with_id('2213', out = 'body_part_colexifications.csv')
```

# Author

* Michael Falk