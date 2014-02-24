'''
The concept of iterative algorithms is used in a lot of places, from projects
like this to optimization for machine learning. An iterative approach to a problem
allows an algorithm to generate progressively better solutions until either the
solutions become optimal (or close to it) -- a state known as convergence -- or the
iteration is stopped for another reason, such as to save time and computing resources.
You can read more about the concept here: vhttp://en.wikipedia.org/wiki/Iterative_method 

This particular algorithm was developed by Adam Bonica, political science professor at
Stanford University. Known as Iterated Money-Weighted Averaging, it uses campaign
contribution data to assign ideological scores to both political candidates and donors.
Applied to a large set of data, this allows us to ask questions like "Who were the most
conservative donors to President Obama?"

You can read more about the algorithm here:
http://ideologicalcartography.com/2010/02/15/how-to-construct-an-ideological-map-of-candidates-and-contributors-using-campaign-finance-records/

There are many models for inferring ideological positions of lawmakers, but they
require examining voting records, meaning they can only be used for sitting members, not
candidates. However, because it relies only on campaign contribution data, IMWA is able to 
infer the ideologies of candidates that have never served in office.
'''
import math
from pprint import pprint

if __name__ == '__main__':

    # A few donors, along with their contributions. At the beginning of the algorithm, all of their "cfscore"
    # attributes (their ideological scores) are set to 0.
    donors = [
        {'name': 'Joe', 'donations': [('Feinstein', 500), ('Akaka', 500), ('Schumer', 1000)], 'cfscore': 0},
        {'name': 'Bob', 'donations': [('McCain', 500), ('McConnell', 500)], 'cfscore': 0},
        {'name': 'Tim', 'donations': [('McCain', 500), ('Schumer', 500), ('Akaka', 1000)], 'cfscore': 0},
    ]

    # A toy list of candidates. To begin, all Republicans have their ideological score set to 1 and Democrats
    # are set to -1. Eventually they will converge at more nuanced positions.
    cands = [
        {'name': 'Schumer', 'cfscore': -1},
        {'name': 'McConnell', 'cfscore': 1},
        {'name': 'Feinstein', 'cfscore': -1},
        {'name': 'Akaka', 'cfscore': -1},
        {'name': 'McCain', 'cfscore': 1}
    ]

    # In this case, we're just going cut off the algorithm after 10 iterations, rather than waiting for
    # perfect convergence. The variable i is just a counter.
    i = 0
    while i < 10:

        # Set CF score for donors. Scores are just derived from money-weighted averages of the amount
        # given to a candidate times the ideological score of that candidate, which changes with each
        # iteration
        for d in donors:
            score, total = 0.0, 0.0
            for c in d['donations']:
                recipient, amount = c
                candidate = next((item for item in cands if item["name"] == recipient), None)

                score += amount * candidate['cfscore']
                total += amount
            d['cfscore'] = score / total

        # Now set the CF score for candidates. These are derived from the average weighted ideological
        # score of each candidate's contributor, summed and averaged.
        for c in cands:
            score, total = 0.0, 0.0
            for d in donors:
                donations = [e[1] for e in d['donations'] if e[0] == c['name']]
                for amount in donations:
                    score += amount * d['cfscore']
                    total += amount
            c['cfscore'] = score / total

        # Now we normalize candidate scores to mean = 0, standard deviation = 1
        scores = [c['cfscore'] for c in cands]
        mean = sum(scores) / len(scores)
        variance = map(lambda x: (x - mean) ** 2, scores)
        stdev = sum(variance) / len(variance)
        for c in cands:
            c['cfscore'] = (c['cfscore'] - mean) / stdev

        # Repeat until convergence (in this case, arbirarily set at 10 iterations)
        i += 1

    # Print out the results. Negative numbers lean Democratic, positive lean Republican
    print 'Candidates'
    map(lambda c: pprint('%s: %s' % (c['name'], c['cfscore'])), cands)

    print 'Donors'
    map(lambda d: pprint('%s: %s' % (d['name'], d['cfscore'])), donors)