# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 14:08:11 2022

@author: Roberto
"""

import pyperclip
import re

def print_search_results(data: dict, num: int) -> None:
    """
    Print to screen all locations where an item or a list of items can be found.
    Parameters
    ----------
    data : dict
        a dictionary from the output of SearchEngine.search_item() or SearchEngine.search_group()
    num : int
        The number of hits to be returned as completetext

    """
    if not num:
        num = 20
        
    if len(data) == 0:
        return
    
    print()
    
    testval = list(data.values())[0]
    if type(testval) == float:
        for i, (item, value) in enumerate(sorted(data.items(), \
                key=lambda x:x[1], reverse=True)):
            if (num == 0) or (i < num):
                print("{} {:.1%} 1:{:.1f}".format(item, value, 1/value))  
    elif type(testval) == tuple:
        for i, (item, value) in enumerate(sorted(data.items(), \
                key=lambda x:x[1][0] * x[1][1] / x[1][2], reverse=True)):
            if (num == 0) or (i < num):
                print("{} {}/{}".format(item, value[1], value[2]))
    else:
        print("Unknown data type. Data should be a search result from SearchEngine.")
            


def clipboardwiki(search_engine, complete: int, mention: int) -> None:
    '''
    Usage:
    Copy the string i.e. == Batch of Mushrooms ==
    and the function will retrieve the text from the clipboard, 
    perform a search for it in the search engine,
    and paste the resulting search odds into the clipboard.
    You can then type CTRL-V to paste the formatted text into the wiki.
    
    '''
    
    if not complete:
        complete = 3
    if not mention:
        mention = 5
        
    string = pyperclip.paste()
    string = string.strip("= \n")
    print("Looking for:", string)
    text = search_engine.text_for_wiki(search_engine.search_item(string), complete=complete, mention=mention)
    print(text)
    pyperclip.copy(text)
    


def wikitext(search_engine, original: str, complete: int, mention: int, insertafter: str = "'''Weight") -> None:
    '''
    From a plaintext file containing the Wikipedia entry, create and save
    a new file ("wikitext_out.txt") with added find information.
    
    '''
    savename = "wikitext_out.txt"
    
    print("Saving to:", savename)
    if not complete:
        complete = 5
    if not mention:
        mention = 5
    if original == '':
        original = "wikitext.txt"
    with open(original, "r") as f:
        data = f.readlines()
    lastcomp = False
    with open(savename, "w") as f:
        for line in data:
            f.write(line)
            if line.startswith("=="):
                lastcomp = re.search("== ?([\S ]*?) ?==", line)[1]
            elif line.startswith(insertafter):
                text = search_engine.text_for_wiki(\
                        search_engine.search_item(lastcomp), complete=complete, mention=mention)
                lastcomp = False
                f.write(text)
                