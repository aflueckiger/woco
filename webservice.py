#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Project: Word Continuum: WoCo Explorer

# http://r2d2.cl.uzh.ch/~pcl3_02/woco/webservice.py?words=testen,morgen

import os
import sys
import cgi
import json
from nltk.corpus import stopwords
import string

# Special import procedure of outsourced module due to webservers inability
# to look for packages in same directory

import importlib
sys.path.append(os.path.dirname(__file__))
import backend
backend = importlib.reload(backend)


languages = {'german': 'de',
             'english': 'en',
             'french': 'fr'}


def application(environ, start_response):
    # Read GET parameters
    params = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

    # Parse various parameters from URL (GET-Method)
    words = params.getfirst('words', default='').split(',')
    filter_stopwords = params.getfirst('stopwords', default='')
    filter_stopwords = True if stopwords == 'true' else False  # convert to boolean type
    lemma = params.getfirst('lemma', default='')
    language = params.getfirst('language', default='')

    # Set language specific stopwords
    if filter_stopwords:
        filterwords = stopwords.words(language)
        filterwords += [char for char in string.punctuation]
    else:
        filterwords = ['']

    # Set language
    language = languages[language]

    # Call functions to count words in corpus
    result = backend.extract_term_relations(words, language, filterwords)

    """
    if lemma == 'true':
        result = backend.lemma_count(words)
    else:
        result = backend.token_count(words)

    # Prepare results from DB for output
    output = ""
    for key, value in result.items():
        output += "'{}' occurs {} times in corpus\n".format(key, value)

    output = output.encode()
    """
    # Parameters
    parameters = {'words': words,
                  'stopwords': stopwords,
                  'lemma': lemma,
                  'language': language}

    # Convert result into JSON
    res_json = json.dumps(result, ensure_ascii=False)

    # Set header and response
    status = "200 OK"
    res_json = res_json.encode()

    response_headers = [("Content-type", "text/plain"),
                        ("Content-Length", str(len(res_json)))]
    start_response(status, response_headers)

    # Return response
    return [res_json]
