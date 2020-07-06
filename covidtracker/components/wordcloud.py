import re
from collections import Counter
from random import choice

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from ..settings import THREESIXTY_COLOURS

def wordcloud(words, func='bigrams'):

    words = words.loc[words['func']==func, 'ngram'].value_counts()

    if not len(words):
        return None
    maxcount = words.max()
    scaling = 36 / maxcount
    
    spans = []
    colour = None
    for k, w in enumerate(words.head(30).iteritems()):
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
    
    
