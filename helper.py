# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 12:25:08 2022

@author: Roberto

Helper functions

"""

def sanitize(url):
    '''
    Remove all Windows restricted characters from a url.
    '''
    for item in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        url = url.replace(item, "_")
    if url.startswith("_wiki_"):
        url = url[6:]
    url = url+".html"
    return url


def format_percent(flnum: float) -> str:
    '''
    Return a string representing a percent number, removing .0 if necessary.
    '''
    string = "{:.1%}".format(flnum)
    if string.endswith(".0%"):
        string = string[:-3]+"%"
    return string

