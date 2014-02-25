'''
Say you've got a list of Congressional voting records and you want to see how similar
members are to each other. A simple approach to the problem might look something like 
this (in pseudocode):

for member in members:
    for other_member in members:
        calculate_similarity(member, other_member)

In other words, you could use loops. Nested loops, at that.

Problem is, loops are slow. A more effective approach -- and one that becomes necessary
when working with large datasets -- is by recasting the problem into linear algebra and
using vectorized operations.

Numpy and Scipy are great tools for this, and it's a good rule to keep in mind whenever
you're performing expensive operations on lists. You can see some performance metrics in
this excellent post here: http://docs.scipy.org/doc/numpy/user/whatisnumpy.html

This script uses a vectorized approach to quickly produce a pairwise similarity matrix of
lawmakers' roll call votes, given an input *.ord matrix file from Poole, McCarty and Lewis:
http://www.voteview.com/dwnl.htm
'''
import numpy, string
from scipy.spatial.distance import cdist
 
########## HELPERS ##########
 
class LookerUpper(object):
    '''
    Helper class to look up pairwise similarity scores by member, given an input name and
    similarity matrix.
    '''
    def __init__(self, names, matrix):
        self.names = names
        self.matrix = matrix
 
    def lookup(self, name):
        for i, j in enumerate(self.matrix[self.names.index(name)]):
            yield '%s: %s' % (self.names[i], j)
 
    def lookup_pair(self, name1, name2):
        name1_idx = self.names.index(name1)
        name2_idx = self.names.index(name2)
        return '%s -> %s: %s' % (name1, name2, self.matrix[name1_idx, name2_idx])
 
def cleansplit(str):
    '''
    Split fixed-width input file. Sigh.
    '''
    return map(string.strip, [str[:12], str[12:20], str[:20:25], str[25:36], str[36:]])
 
########## MAIN ##########
 
if __name__ == '__main__':
    with open('data/hou112kh.ord', 'rU') as infile:
        rows = [cleansplit(a) for a in infile.readlines()] # Parse fixed-width .ord input file
        names = [r[3] for r in rows] # r[3] is the name code
 
    # Build a numpy matrix from all the vote data in the input file.
    data = numpy.matrix([[i for i in list(r[4])] for r in rows])
 
    # Calculate vectorized pairwise similarity between all senators using Jaccard distance,
    # which is just a measure of what percentage of each lawmaker's votes lined up with another's.
    # Subtracting from 1.0 just turns the measure into a similarity score rather than a distance.
    # Notice how we're doing this in one line, not using loops.
    similarities = 1.0 - cdist(data, data, 'jaccard')
 
    # Print some similarities, given a lookup name
    looker_upper = LookerUpper(names, similarities)
    for i in looker_upper.lookup('CANTOR'):
        print i
 
    # And here's a lookup of two names
    print looker_upper.lookup_pair('DELBENE', 'CANTOR')