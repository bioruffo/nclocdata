# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 11:16:24 2022

@author: Roberto

Save locally a group of wikipedia pages.
Starting from the landing page, e.g. https://wiki.nexusclash.com/wiki/Category:Current_Locations,
the script goes over all the pages in the category, and then downloads each page individually.

"""

import requests
from bs4 import BeautifulSoup
import os
import time
from .helper import sanitize
from .defaults import prefix, url, savedir


def get_all_files(prefix: str = prefix,
        url: str = url,
        savedir: str = savedir,
        verbose: bool = True):
    '''
    Call sub-functions to retrieve all location files and save them to savedir.
    '''
    
    if savedir not in os.listdir():
        os.mkdir(savedir)
    locations = _get_refs(prefix, url, verbose)
    if verbose:
        print("Got {} location addresses".format(len(locations)))
    _download_refs(locations, prefix, savedir, verbose)


def _get_refs(prefix: str, url: str, verbose: bool) -> list:
    '''
    Build a list of webpages for later downloading.
    '''
             
    all_refs = None
    counter = 0
    while True:
        counter += 1
        if verbose:
            print(counter)
        req = requests.get(prefix+url)
        soup = BeautifulSoup(req.content, 'html.parser')
        locdiv = soup.find("div", attrs={"id": "mw-pages"})
        refs = locdiv.find_all("a")
        if all_refs == None:
            all_refs = refs
        else:
            all_refs.extend(refs)
        if refs[0].text == 'next page':
            url = refs[0]['href']
        else:
            break

    locations = [ref for ref in all_refs if ref["href"].startswith("/wiki")]
    
    return locations


def _download_refs(locations: list, prefix: str, savedir: str, \
                   verbose: bool) -> None:
    '''
    Download a list of webpages.
    '''

    counter = 0
    for loc in locations:
        url = loc['href']
        req = requests.get(prefix+url)
        open(os.path.join(savedir, sanitize(url)), "wb").write(req.content)
        counter += 1
        if verbose:
            print(counter, loc.text)
        time.sleep(2)
