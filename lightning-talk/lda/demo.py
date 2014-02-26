'''
Latent Dirichlet Allocation is a tool for automatically finding key topics in large
sets of documents. It can be useful for separating documents into buckets to guide 
research, exploring the general themes over a document set, or for identifying
segments of documents that for whatever reason stand out.

LDA conveys topics as lists of related words, leaving it to the user to decide what
those topics actually mean. You can see an example of it applied to Sarah Palin's 
leaked e-mails here: http://blog.echen.me/2011/06/27/topic-modeling-the-sarah-palin-emails/

The math behind the algorithm is complicated, but Edwin Chen does a great job of 
breaking it down here: http://blog.echen.me/2011/08/22/introduction-to-latent-dirichlet-allocation/

In this example, we'll use LDA to look at a very small subset of sections from the
Credit Card Act of 2009, which we'll see contains at least one segment that doesn't 
relate at all to credit cards.
'''
import string, re, glob
import gensim

########## HELPERS ##########

PUNCTUATION = re.compile('([%s]|[0-9]|\n)' % re.escape(string.punctuation))

def clean_text(txt):
    '''
    Helper function to do some basic cleaning on the text. Removing punctuation,
    stripping whitespace and lowercasing.
    '''
    return PUNCTUATION.sub('', txt.lower().strip())

########## MAIN ##########

if __name__ == '__main__':
    # Open up some raw documents and read their text into a list. In this case, the raw docs
    # correspond to a few select (and dirty) sections of the Credit Card Act of 2009, which you
    # can see here: https://www.govtrack.us/congress/bills/111/hr627/text
    documents = [clean_text(open(f, 'r').read()) for f in glob.iglob('data/*.txt')]

    # A little basic cleanup with an abbreviated stopword list
    stoplist = set('for is with a on shall such an any not by or that of the and to in'.split())
    texts = [[word for word in clean_text(document).split() if word not in stoplist] for document in documents]

    # Use gensim to prep the data into a dictionary and corpus
    dictionary = gensim.corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    # Simple LDA pass, looking for 2 topics over 10 iterations. These are parameters you'll likely want to
    # tweak if you use this on your own data. The number of topics in particular.
    lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=2, passes=10)

    # Looping through the words that characterize the two topics we created, we'll see one that seems to
    # contain a lot of credit card-related words, which makes sense for a bill like this, and another that
    # contains words related to national parks and the Second Amendment, which seem a bit out of place. If
    # we wanted to, we could walk back through the documents, assign them topics based on the weights given
    # to each topic's words, and classify them on a topical basis in order to see the section that doesn't belong.
    for topic in lda.show_topics():
        print topic