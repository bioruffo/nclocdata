# -*- coding: utf-8 -*-
"""
Created on Sun Jul 17 07:37:35 2022

@author: Roberto

Nexus Clash
Get search % of an item or a list of items

"""

import argparse

from .download import get_all_files
from .searchengine import SearchEngine
from .out import print_search_results, clipboardwiki, wikitext
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape and use Nexus Clash location data")
    parser.add_argument("-d", action='store_true', help="Download Wiki pages about current locations")
    parser.add_argument("-s", type=str, help="Search for an item")
    parser.add_argument("-f", type=str, help="Search from an item file")
    parser.add_argument("-w", type=str, help="Add drop rate info to a wiki page")
    parser.add_argument("-t", type=str, help="Build drop table")
    parser.add_argument("-c", type=int, help="Number of complete records to return")
    parser.add_argument("-m", type=int, help="Number of mentioned records to return")
    parser.add_argument("-l", type=str, help="Locate any items containing this word")
    args = parser.parse_args()
    
    if args.d:
        print("Getting remote data...")
        get_all_files()
    elif args.s:
        print_search_results(data=SearchEngine().search_item(args.s), num=args.c)
    elif args.f:
        print_search_results(data=SearchEngine().search_group(args.f), num=args.c)
    elif args.w:
        wikitext(SearchEngine(), original=args.w, complete=args.c, mention=args.m)
    elif args.t:
        SearchEngine().build_droptable()
    elif args.l:
        SearchEngine().find_by_name(text=args.l, toscreen=True)
        
                    
                    
                  
    
    
    
