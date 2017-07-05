import datetime
from sklearn.externals import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from textstat.textstat import *
from ml import nlp
import numpy as np
import pandas as pd

#generates tfidf weighted ngram feature as a matrix and the vocabulary
def get_ngram_tfidf(ngram_vectorizer: TfidfVectorizer, tweets, out_folder, flag):
    joblib.dump(ngram_vectorizer, out_folder + '/'+flag+'_ngram_tfidf.pkl')
    print("\tgenerating n-gram vectors, {}".format(datetime.datetime.now()))
    tfidf = ngram_vectorizer.fit_transform(tweets).toarray()
    print("\t\t complete, dim={}, {}".format(tfidf.shape,datetime.datetime.now()))
    vocab = {v: i for i, v in enumerate(ngram_vectorizer.get_feature_names())}
    idf_vals = ngram_vectorizer.idf_
    idf_dict = {i: idf_vals[i] for i in vocab.values()}  # keys are indices; values are IDF scores
    #todo: output vocabulary index
    return tfidf, vocab


#generates tfidf weighted PoS of ngrams as a feature matrix and the vocabulary
def get_ngram_pos_tfidf(pos_vectorizer:TfidfVectorizer, tweets, out_folder, flag):
    print("\tcreating pos tags, {}".format(datetime.datetime.now()))
    tweet_tags = nlp.get_pos_tags(tweets)
    print("\tgenerating pos tag vectors, {}".format(datetime.datetime.now()))
    pos = pos_vectorizer.fit_transform(pd.Series(tweet_tags)).toarray()
    joblib.dump(pos_vectorizer, out_folder + '/'+flag+'_pos.pkl')
    print("\t\tcompleted, dim={}, {}".format(pos.shape,datetime.datetime.now()))
    pos_vocab = {v: i for i, v in enumerate(pos_vectorizer.get_feature_names())}
    #todo: output vocabulary index
    return pos, pos_vocab

#todo: return a hashtag matrix indicating the presence of particular hashtags in tweets. input is the list of all tweets
#DictVectorizer should be used, see http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.DictVectorizer.html#sklearn.feature_extraction.DictVectorizer
def get_hashtags_in_tweets(dict_vectorizer: DictVectorizer, tweets, out_folder, flag):
    pass


#todo: return matrix containing a number indicating the extent to which CAPs are used in the tweets
#see 'other_features_' that processes a single tweet, and 'get_oth_features' that calls the former to process all tweets
def get_capitalizations(tweets, cleaned_tweets):
    pass

#todo: return matrix containing a number indicating the extent to which misspellings are found in the tweets
#see 'other_features_' that processes a single tweet, and 'get_oth_features' that calls the former to process all tweets
def get_misspellings(tweets, cleaned_tweets):
    pass


#todo: return matrix containing a number indicating the extent to which special chars are found in the tweets
#see 'other_features_' that processes a single tweet, and 'get_oth_features' that calls the former to process all tweets
def get_specialchars(tweets, cleaned_tweets):
    pass


#todo: return matrix containing a number indicating the extent to which special punctuations are found in the tweets
#see 'other_features_' that processes a single tweet, and 'get_oth_features' that calls the former to process all tweets
def get_specialpunct(tweets, cleaned_tweets):
    pass


#todo: this should encode 'we vs them' patterns in tweets but this is the most complicated..
def get_dependency_feature(tweets, cleaned_tweets):
    pass



def other_features_(tweet, cleaned_tweet):
    """This function takes a string and returns a list of features.
    These include Sentiment scores, Text and Readability scores,
    as well as Twitter specific features.

    This is modified to only include those features in the final
    model."""

    sentiment = nlp.sentiment_analyzer.polarity_scores(tweet)

    words = cleaned_tweet #Get text only

    syllables = textstat.syllable_count(words) #count syllables in words
    num_chars = sum(len(w) for w in words) #num chars in words
    num_chars_total = len(tweet)
    num_terms = len(tweet.split())
    num_words = len(words.split())
    avg_syl = round(float((syllables+0.001))/float(num_words+0.001),4)
    num_unique_terms = len(set(words.split()))

    ###Modified FK grade, where avg words per sentence is just num words/1
    FKRA = round(float(0.39 * float(num_words)/1.0) + float(11.8 * avg_syl) - 15.59,1)
    ##Modified FRE score, where sentence fixed to 1
    FRE = round(206.835 - 1.015*(float(num_words)/1.0) - (84.6*float(avg_syl)),2)

    twitter_objs = count_twitter_objs(tweet) #Count #, @, and http://
    features = [FKRA, FRE, syllables, num_chars, num_chars_total, num_terms, num_words,
                num_unique_terms, sentiment['compound'],
                twitter_objs[2], twitter_objs[1],]
    #features = pandas.DataFrame(features)
    return features



def count_twitter_objs(text_string):
    """
    Accepts a text string and replaces:
    1) urls with URLHERE
    2) lots of whitespace with one instance
    3) mentions with MENTIONHERE
    4) hashtags with HASHTAGHERE

    This allows us to get standardized counts of urls and mentions
    Without caring about specific people mentioned.

    Returns counts of urls, mentions, and hashtags.
    """
    space_pattern = '\s+'
    giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
                       '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    mention_regex = '@[\w\-]+'
    hashtag_regex = '#[\w\-]+'
    parsed_text = re.sub(space_pattern, ' ', text_string)
    parsed_text = re.sub(giant_url_regex, 'URLHERE', parsed_text)
    parsed_text = re.sub(mention_regex, 'MENTIONHERE', parsed_text)
    #parsed_text = re.sub('#', '', parsed_text) #replace the tag leave the word
    parsed_text = re.sub(hashtag_regex, 'HASHTAGHERE', parsed_text)
    return (parsed_text.count('URLHERE'), parsed_text.count('MENTIONHERE'), parsed_text.count('HASHTAGHERE'))


def get_oth_features(tweets, cleaned_tweets):
    """Takes a list of tweets, generates features for
    each tweet, and returns a numpy array of tweet x features"""
    feats=[]
    count=0
    for t, tc in zip(tweets, cleaned_tweets):
        feats.append(other_features_(t, tc))
        count+=1
        # if count%100==0:
        #     print("\t {}".format(count))
    other_features_names = ["FKRA", "FRE","num_syllables", "avg_syl_per_word", "num_chars", "num_chars_total", \
                        "num_terms", "num_words", "num_unique_words", "vader neg","vader pos","vader neu", "vader compound", \
                        "num_hashtags", "num_mentions", "num_urls", "is_retweet"]

    return np.array(feats), other_features_names
