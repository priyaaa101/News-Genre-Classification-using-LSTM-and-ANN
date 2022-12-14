import flask
import re
import nltk
import enchant
import pickle as pkl
import tensorflow.keras as ks


app = flask.Flask(__name__)

def tokenize(text):
    text_list = text.split(' ')
    return text_list

def separate_compound_words(text):
    contractions = {"ain't": "are not", "aren't": "are not", "can't": "cannot", "can't've": "cannot have", "'cause": "because", "could've": "could have", "couldn't": "could not", "couldn't've": "could not have", "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hadn't've": "had not have", "hasn't": "has not", "haven't": "have not", "he'd": "he would", "he'd've": "he would have", "he'll": "he will", "he'll've": "he will have", "he's": "he is", "here's": "here is", "how'd": "how did", "how'd'y": "how do you", "how'll": "how will", "how's": "ow is", "i'd": "I would", "i'd've": "I would have", "i'll": "I will", "i'll've": "I will have", "i'm": "I am", "i've": "I have", "isn't": "is not", "it'd": "it would", "it'd've": "it would have", "it'll": "it will", "it'll've": "it will have", "it's": "it is", "let's": "let us", "ma'am": "madam", "mayn't": "may not", "might've": "might have", "mightn't": "might not", "mightn't've": "might not have", "must've": "must have", "mustn't": "must not", "mustn't've": "must not have", "needn't": "need not", "needn't've": "need not have", "o'clock": "of the clock", "oughtn't": "ought not", "oughtn't've": "ought not have", "shan't": "shall not", "sha'n't": "shall not", "shan't've": "shall not have", "she'd": "she would", "she'd've": "she would have", "she'll": "she will", "she'll've": "she will have", "she's": "she is", "should've": "should have", "shouldn't": "should not", "shouldn't've": "should not have", "so've": "so have", "so's": "so is", "that'd": "that would", "that'd've": "that would have", "that's": "that is", "'em": "them", "there'd": "there would", "there'd've": "there would have", "there's": "there is", "they'd": "they would", "they'd've": "they would have", "they'll": "they will", "they'll've": "they will have", "they're": "they are", "they've": "they have", "to've": "to have", 'u.s.': 'united states', 'u.s.a.': 'united states of america', "wasn't": "was not", "we'd": "we would", "we'd've": "we would have", "we'll": "we will", "we'll've": "we will have", "we're": "we are", "we've": "we have", "weren't": "were not", "what'll": "what will", "what'll've": "what will have", "what're": "what are", "what's": "what is", "what've": "what have", "when's": "when is", "when've": "when have", "where'd": "where did", "where's": "where is", "where've": "where have", "who'll": "who will", "who'll've": "who will have", "who's": "who is", "who've": "who have", "why's": "why is", "why've": "why have", "will've": "will have", "won't": "will not", "won't've": "will not have", "would've": "would have", "wouldn't": "would not", "wouldn't've": "would not have", "y'all": "you all", "y'all'd": "you all would", "y'all'd've": "you all would have", "y'all're": "you all are", "y'all've": "you all have", "you'd": "you would", "you'd've": "you would have", "you'll": "you will", "you'll've": "you will have", "you're": "you are", "you've": "you have", 'yrs': 'years', 'yrsold': 'years old', '&': ' and '}
    text_list = tokenize(text)
    text = ''
    for index, i in enumerate(text_list):
        if i in contractions:
            text_list[index] = contractions[i]
        text = text + ' ' + text_list[index]
    return text

def remove_punctuations(text):
    text = re.sub(r'[^\w\s]', ' ', text, re.UNICODE)
    return text

def lemmatize(text):
    text_list = tokenize(text)
    nltk.download('wordnet')
    lemmatizer = nltk.stem.WordNetLemmatizer()
    text = ''
    for index, i in enumerate(text_list):
        text_list[index] = lemmatizer.lemmatize(i)
        text = text + ' ' + text_list[index]
    return text

def remove_stopwords(text):
    nltk.download('stopwords')
    sw = nltk.corpus.stopwords.words('english')
    text_list = tokenize(text)
    text = ''
    for i in text_list:
        if i not in sw:
            text = text + ' ' + i
    return text

def keep_sensical_words(text):
    eng_dict = enchant.Dict("en_US")
    text_list = tokenize(text)
    for i in text_list:
        if i == '' or not eng_dict.check(i):
            text_list.remove(i)
    text = ''
    for i in text_list:
        text = text + ' ' + i
    return text

@app.route('/', methods=['POST', 'GET'])
def predict():
    if flask.request.method == 'POST':
        headline = flask.request.form['headline']
        headline = headline.lower()
        headline = separate_compound_words(headline)
        headline = remove_punctuations(headline)
        headline = lemmatize(headline)
        headline = remove_stopwords(headline)
        headline = keep_sensical_words(headline)

        desc = flask.request.form['desc']
        desc = desc.lower()
        desc = separate_compound_words(desc)
        desc = remove_punctuations(desc)
        desc = lemmatize(desc)
        desc = remove_stopwords(desc)
        desc = keep_sensical_words(desc)

        inp = headline + ' ' + desc
        max_sequence_length = 250
        with open('tokenizer.pickle', 'rb') as handle:
            tokenizer = pkl.load(handle)
        inp = tokenizer.texts_to_sequences(inp)
        inp = ks.preprocessing.sequence.pad_sequences(inp, maxlen=max_sequence_length)
        cat = ['ARTS & CULTURE', 'BLACK VOICES', 'BUSINESS', 'COLLEGE', 'COMEDY', 'CRIME', 'DIVORCE', 'EDUCATION', 'ENTERTAINMENT', 'ENVIRONMENT', 'FIFTY', 'FOOD & DRINK', 'GOOD NEWS', 'HEALTHY LIVING', 'HOME & LIVING', 'IMPACT', 'LATINO VOICES', 'MEDIA', 'MONEY', 'PARENTING', 'POLITICS', 'QUEER VOICES', 'RELIGION', 'SCIENCE', 'SPORTS', 'STYLE & BEAUTY', 'TECH', 'TRAVEL', 'WEDDINGS', 'WEIRD NEWS', 'WELLNESS', 'WOMEN', 'WORLD']
        lr = 0.001
        model = ks.models.load_model('model.hdf5')
        model.compile(loss='categorical_crossentropy', optimizer=ks.optimizers.RMSprop(learning_rate=lr), metrics = [ks.metrics.CategoricalAccuracy(), ks.metrics.TopKCategoricalAccuracy(k=3)])
        pred = model.predict(inp)
        print(pred[0])
        max1 = 0
        ind1 = None
        for ind, i in enumerate(pred[0]):
            if i > max1:
                max1 = i
                ind1 = ind
        max2 = 0
        ind2 = None
        for ind, i in enumerate(pred[0]):
            if i > max2 and ind != ind1:
                max2 = i
                ind2 = ind
        max3 = 0
        ind3 = None
        for ind, i in enumerate(pred[0]):
            if i > max3 and ind != ind1 and ind != ind2:
                max3 = i
                ind3 = ind
        return flask.render_template('index.html', pred1=cat[ind1], p1=max1 * 100, pred2=cat[ind2], p2=max2 * 100, pred3=cat[ind3], p3=max3 * 100)
    return flask.render_template('index.html', pred1='', p1='', pred2='', p2='', pred3='', p3='')


if __name__ == '__main__':
    app.run(debug=True)
