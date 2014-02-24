import math

# Rough sketch of Iterated Money Weighted Averaging approach documented below. Still needs to be verified:
# http://ideologicalcartography.com/2010/02/15/how-to-construct-an-ideological-map-of-candidates-and-contributors-using-campaign-finance-records/

if __name__ == '__main__':
    donors = [
        {'name': 'Joe', 'donations': [('Feinstein', 500), ('Akaka', 500), ('Schumer', 1000)], 'cfscore': 0},
        {'name': 'Bob', 'donations': [('McCain', 500), ('McConnell', 500)], 'cfscore': 0},
        {'name': 'Tim', 'donations': [('McCain', 500), ('Schumer', 500), ('Akaka', 1000)], 'cfscore': 0},
    ]

    cands = [
        {'name': 'Schumer', 'cfscore': -1},
        {'name': 'McConnell', 'cfscore': 1},
        {'name': 'Feinstein', 'cfscore': -1},
        {'name': 'Akaka', 'cfscore': -1},
        {'name': 'McCain', 'cfscore': 1}
    ]

    i = 0
    while i < 10:
        # Set CF score for donors
        for d in donors:
            score, total = 0.0, 0.0
            for c in d['donations']:
                recipient, amount = c
                candidate = next((item for item in cands if item["name"] == recipient), None)

                score += amount * candidate['cfscore']
                total += amount
            d['cfscore'] = score / total

        # Set CF score for candidates
        for c in cands:
            score, total = 0.0, 0.0
            for d in donors:
                donations = [e[1] for e in d['donations'] if e[0] == c['name']]
                for amount in donations:
                    score += amount * d['cfscore']
                    total += amount
            c['cfscore'] = score / total

        # Normalize candidate scores to mean = 0, SD = 1
        scores = [c['cfscore'] for c in cands]
        mean = sum(scores) / len(scores)
        variance = map(lambda x: (x - mean) ** 2, scores)
        stdev = sum(variance) / len(variance)
        for c in cands:
            c['cfscore'] = (c['cfscore'] - mean) / stdev

        # Repeat until convergence (in this case, arbirarily set at 10 iterations)
        i += 1

    print cands
    print donors