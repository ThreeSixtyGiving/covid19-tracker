import re
from collections import Counter
from random import choice

import dash
import dash_core_components as dcc
import dash_html_components as html

from ..settings import THREESIXTY_COLOURS

def wordcloud(data, chart_type="amount", show_grantmakers=True):

    def clean_string(s):
        s = s.lower()
        s = re.sub('[\']+', '', s).strip()
        s = re.sub('[^0-9a-zA-Z]+', ' ', s).strip()
        return s.split()

    def bigrams(text):
        return [w for w in text if w not in STOPWORDS]

    words = []
    for g in data["grants"]:
        words.extend(bigrams(clean_string(g["title"]) + clean_string(g["description"])))
    words = Counter(words)

    if not words:
        return None
    maxcount = words.most_common(1)[0][1]
    scaling = 36 / maxcount
    
    spans = []
    colour = None
    for k, w in enumerate(words.most_common(30)):
        word, wordcount = w
        colour = choice([c for c in THREESIXTY_COLOURS if c != colour])
        spans.append(html.Span(
            children=word,
            style={
                'fontSize': max(wordcount * scaling, 16),
                'color': colour,
                'marginRight': '20px',
                'display': 'inline-block',
            }
        ))
        # spans.append(' ')
    
    return html.Div(
        className="base-card base-card--yellow",
        children=[
            html.Div(className="base-card__content", children=[
                html.Header(className="base-card__header", children=[
                    html.H3(className="base-card__heading", children="Commonly used words"),
                ]),
                html.P(className="align-left", children=spans),
            ]),
        ],
    )
    
    
STOPWORDS = [
    'i',
    'me',
    'my',
    'myself',
    'we',
    'our',
    'ours',
    'ourselves',
    'you',
    "you're",
    "you've",
    "you'll",
    "you'd",
    'your',
    'yours',
    'yourself',
    'yourselves',
    'he',
    'him',
    'his',
    'himself',
    'she',
    "she's",
    'her',
    'hers',
    'herself',
    'it',
    "it's",
    'its',
    'itself',
    'they',
    'them',
    'their',
    'theirs',
    'themselves',
    'what',
    'which',
    'who',
    'whom',
    'this',
    'that',
    "that'll",
    'these',
    'those',
    'am',
    'is',
    'are',
    'was',
    'were',
    'be',
    'been',
    'being',
    'have',
    'has',
    'had',
    'having',
    'do',
    'does',
    'did',
    'doing',
    'a',
    'an',
    'the',
    'and',
    'but',
    'if',
    'or',
    'because',
    'as',
    'until',
    'while',
    'of',
    'at',
    'by',
    'for',
    'with',
    'about',
    'against',
    'between',
    'into',
    'through',
    'during',
    'before',
    'after',
    'above',
    'below',
    'to',
    'from',
    'up',
    'down',
    'in',
    'out',
    'on',
    'off',
    'over',
    'under',
    'again',
    'further',
    'then',
    'once',
    'here',
    'there',
    'when',
    'where',
    'why',
    'how',
    'all',
    'any',
    'both',
    'each',
    'few',
    'more',
    'most',
    'other',
    'some',
    'such',
    'no',
    'nor',
    'not',
    'only',
    'own',
    'same',
    'so',
    'than',
    'too',
    'very',
    's',
    't',
    'can',
    'will',
    'just',
    'don',
    "don't",
    'should',
    "should've",
    'now',
    'd',
    'll',
    'm',
    'o',
    're',
    've',
    'y',
    'ain',
    'aren',
    "aren't",
    'couldn',
    "couldn't",
    'didn',
    "didn't",
    'doesn',
    "doesn't",
    'hadn',
    "hadn't",
    'hasn',
    "hasn't",
    'haven',
    "haven't",
    'isn',
    "isn't",
    'ma',
    'mightn',
    "mightn't",
    'mustn',
    "mustn't",
    'needn',
    "needn't",
    'shan',
    "shan't",
    'shouldn',
    "shouldn't",
    'wasn',
    "wasn't",
    'weren',
    "weren't",
    'won',
    "won't",
    'wouldn',
    "wouldn't"
    'toward',
    'towards',
    'work',
    'works',
    'help',
    'continue',
    'works',
    'provide',

    # covid-specific words
    'covid19',
    '19',
    'covid',
    'people',
    'grant',
    'during',
    'pandemic',    
    'coronavirus',
]
