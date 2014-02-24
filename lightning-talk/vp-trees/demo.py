'''
Vantage point trees are data structures that, among other things, make it easy to
search for strings that are similar to a given input string.

For this example, we'll index dozens of different spellings of Pacific Gas & Electric
Co., a large and politically active utility based in California, as they were reported
last cycle in federal campaign finance data. A VP tree can help us clean up and
standardize them.

VP Trees have a couple advantages over existing tools like SQL Server fuzzy matching
and programming libraries like FuzzyWuzzy (https://github.com/seatgeek/fuzzywuzzy).
For one, they are extremely scalable. A Python implementation can built once and 
serialized into a pickle that can be queried quickly in subsequent programs. They 
can also be based on any number of string similarity metrics, so long as they
satisfy certain mathematical constraints (http://en.wikipedia.org/wiki/Metric_space).

In practical terms, that mean we can use conventional measures like Levenshtein distance
or Hamming distance, or slightly more unconventional (but more useful) measures such as
shingled Jaccard similarity, which is what this example is based upon. More documentation
on that metric can be found in the similarity.py file in this directory.
'''

from vptree import VPTree
from similarity import jaccard

if __name__ == '__main__':
    # Pull in a bunch of variants of PG&E's spelling, along with a few
    # non PG&E company names for kicks.
    with open('data/input.txt', 'r') as infile:
        words = list(set([n.strip() for n in infile.readlines()]))

    # Build the tree using Jaccard similarity as the metric. First argument
    # is just a list of words.
    print "Building ..."
    tree = VPTree(words, jaccard)

    # Query the tree, using the most commonly occurring version of the
    # company spelling in the data and retrieve a bunch of similar
    # variants, which we could use to standardize. In this case, we're
    # getting all variants with Jaccard distance up to 0.8, but that
    # parameter needs to be tuned based on the structure of the tree, so
    # feel free to experiment if you index your own stuff.
    print tree.search('PACIFIC GAS & ELEC', 0.8)