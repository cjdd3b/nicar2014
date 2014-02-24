'''
This demo uses the Naive Bayes classifier that comes with Python's Natural
Language Toolkit to replicate a task we did at the Center for Investigative
Reporting, which separated drug-related from non-drug-related press releases
put out by the U.S. Drug Enforcement Administration. Because we trained a 
classifier to do this task accurately, we saved ourselves the trouble of having
to read through thousands of press releases by hand.

The file naivebayes.py, included in this directory, is not used here. I just included
it so you can see a well-documented example of how the algorithm works. NLTK's version
comes with a few bells and whistles that makes it more useful for our purposes.
'''
import nltk
from nltk.corpus import stopwords

def get_features(words):
    """
    Define features that the classifier should pay attention to, in this case boolean
    variables corresponding to each word in the headline. This feature extractor forms
    what's known as a bag-of-words representation of each headline (omitting stopwords like
    the, and, or, etc.) so that our classifier can tell whether the presence of certain words
    is any more or less predictive of a press release title relating to drug trafficking.
    """
    features = {}
    for word in [i for i in words.split() if i not in stopwords.words('english')]:
        features['contains_%s' % word.lower()] = True
    return features
    
if __name__ == '__main__':
    # The data we'll be using to train the classifier. Basically a list of headlines with a
    # YES/NO label attached, to identify whether the headline in question came from a drug-related
    # press release. Note that because we're using so little training data, it's not going to
    # generalize well and will only really work for this example.
    training_data = [line.split('|') for line in open('data/training.txt').readlines()

    # Eventually we're going to classify this
    toclassify = 'Five Columbia Residents among 10 Defendants Indicted for Conspiracy to Distribute a Ton of Marijuana'

    # Create the actual training set by running each of the input data items through our
    # feature extracting function above.
    train_set = [(get_features(n), g) for (n, g) in training_data]

    # Import and create the classifier, then train it using the training set we created above
    from nltk import NaiveBayesClassifier
    classifier = NaiveBayesClassifier.train(train_set)

    # Now classify the headline above
    print classifier.classify(get_features(toclassify))