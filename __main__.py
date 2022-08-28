# -*- coding: utf-8 -*-
"""
Created on Sun Jul 17 07:37:35 2022

@author: Roberto

Nexus Clash
Get search % of an item or a list of items

"""

from .download import get_all_files
from .searchengine import SearchEngine
from .out import print_search_results, clipboardwiki, wikitext

  
    
    
if __name__ == '__main__':

    # print("Getting remote data...")
    # get_all_files()
    
    print("Creating the search engine...")
    search_engine = SearchEngine() 
    
    print()
    searchfile = "config/fruit.txt"
    print(searchfile)
    test = search_engine.search_group(searchfile)
    #test = search_engine.search_item("Spear")
    print_search_results(test)
    
   
    # wikitext()
    
    # df = search_engine.build_droptable()
    # df.to_csv("Item_search_chances.tsv", sep="\t")

    
                    
                    
                  
    
    
    