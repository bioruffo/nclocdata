# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 12:22:08 2022

@author: Roberto
"""

import os
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup
from .helper import format_percent
from .defaults import savedir
from .location import Location

class SearchEngine():
    '''
    Main class for searching and reporting.
    '''
    
    def __init__(self,
                 savedir: str = savedir,
                 # Character-specific modifiers
                 # https://wiki.nexusclash.com/wiki/searching
                 is_demon = False, # Demon classes have a bonus in Stygia
                 rev_has_sod = False, # Revenant with Strength of Darkness
                 rev_has_dw = False, # Revenant with Day Walker
                 el_has_fa = False, # Elementalist with Fire Affinity
                 hc_has_aoe = False, # Holy Champion with Aspect of the Eagle
                 # Buffs
                 encourage = False,
                 divine_resolve = False
                 ):
        
        self.locdict = self._create_locations_dict(savedir)
        
        self.base_mod = 0
        self.stygia_mod = 0
        self.elysium_mod = 0
        self.all_powered = False
        self.memoized_locs = None
        
        assert sum([is_demon, rev_has_sod, hc_has_aoe, el_has_fa]) <= 1
        
        base_mod = 0 # daylight
        
        # general modifiers
        if encourage:
            print("The character is under the influence of Encourage")
            base_mod += encourage
        if hc_has_aoe:
            print("The character is a Holy Champion with Aspect of the Eagle")
            base_mod += 10
            
        stygia_mod = base_mod - 10 # always night, no power
        elysium_mod = base_mod # always daylight, but no power
        
        if rev_has_sod:
            print("The character is a Revenant with SoD; search odds are calculated for nighttime")
            base_mod += 10
            stygia_mod += 20
            if not rev_has_dw:
                elysium_mod -= 10 #always day
            else:
                print("The Revenant has Day Walker and doesn't suffer penalties in Elysium or in daylight")
        
        if is_demon:
            print("The character is a demon and doesn't suffer penalties in Stygia")
            stygia_mod += 15
            
        if el_has_fa or divine_resolve:
            print("The character is always illuminated")
            stygia_mod += 10 # Remove night penalty
            
        self.base_mod = base_mod
        self.stygia_mod = stygia_mod
        self.elysium_mod = elysium_mod
        self.all_powered = (el_has_fa or divine_resolve)
        
        self.memoized_locs = self._memoize()        
        

    def _create_locations_dict(self, savedir: str) -> dict:
        '''
        Return a locations dictionary of the form: {"Location Name": <Location_instance>}
        '''
        
        locdict = dict()
        count = 0
        for item in os.listdir(savedir):
            if item.endswith(".html"):
                with open(os.path.join(savedir, item), "rb") as f:
                    page = BeautifulSoup(f, "html.parser")
                    instance = Location(page)
                    if instance.ok:
                        locdict[instance.name] = instance
                        count += 1
                    else:
                        print("Couldn't scrape any drop data from:", item)
        print("Loaded", count, "locations.")
        return locdict
   

    def _memoize(self):
        # Cordillera has power
        # Purgatorio has power
        # Centrum has power
        # Stygia has no power and is always night
        # Elysium has no power and is always day
        memoized_locs = dict()
        for name, location in self.locdict.items():
            loc = dict()
            memoized_locs[name] = loc
            plane = location.plane
            if plane in ["Elysium", "Stygia"]:
                odds = [self.elysium_mod, self.stygia_mod][plane == "Stygia"]
                if self.all_powered:
                    odds += 10 # There's never power there, so we can always add it
                for orient in ["inside", "outside"]:
                    if orient in location.data:
                        loc[orient] = location.data[orient]["find"] + odds
            elif plane == "General":
                odds = self.base_mod
                if "inside" in location.data:
                    odds += 10 # Considering it powered
                    loc["inside"] = location.data["inside"]["find"] + odds
                else:
                    if self.all_powered:
                        odds += 10 # There's no inside (no power), but we add the bonus when all_powered
                if "outside" in location.data:
                    loc["outside"] = location.data["outside"]["find"] + odds
        return memoized_locs
        
        
    def search_item(self, itemname: str) -> dict:
        '''
        Return a dict in the form {"Location (inside)": findchance_float},
        containing as keys all locations where an item can be found, 
        with the find chances as values (float).
        
        '''
        results = dict()
        found = False
        for name, location in self.locdict.items():
            for orient, odds in self.memoized_locs[name].items():
                if itemname in location.data[orient]["items"]:
                    found = True
                    results["{} ({})".format(name, orient)] = \
                        min(1, odds / 100) * location.data[orient]["items"][itemname] / location.data[orient]["total"]
        if not found:
            print(f"WARNING: Item '{itemname}' not found!")
        return results
        
                
    
    def search_group(self, groupfile: str) -> dict:
        '''
        From a file containing a list of items of interest,
        return a dict in the form {"Location (inside)": findchance_float},
        containing as keys all locations where the items in the list can be found, 
        with the cumulative find chances as values (float).
        
        '''
        items, comments = self._load_search_group(groupfile)
        results = defaultdict(float)
        for item in items:
            new_data = self.search_item(item)
            for position, value in new_data.items():
                results[position] += value
        return results
                


    def search_item_sep(self, itemname: str) -> dict:
        '''
        Return a dict in the form {"Location (inside)": (odds, number, total)},
        containing as keys all locations where an item can be found, 
        and as values the tuple:
            (odds, # adjusted percent chance of finding the item, e.g. 50% = 50
             number, # weight of the find (e.g. in a Forest, a Piece of Wood has find weight 30)
             total) # Total weights for the location

        '''
        results = dict()
        found = False
        for name, location in self.locdict.items():
            for orient, odds in self.memoized_locs[name].items():
                if itemname in location.data[orient]["items"]:
                    found = True
                    results["{} ({})".format(name, orient)] = \
                        (min(1, odds / 100), location.data[orient]["items"][itemname], location.data[orient]["total"])
        if not found:
            print(f"WARNING: Item '{itemname}' not found!")
        return results            
        
    
    def _load_search_group(self, groupfile: str) -> tuple:
        '''
        Load the list of searched items from groupfile.
        Return a tuple containing item names, as dict in the form {"itemname": weight}
        and comments as dict in the form {"itemname": "(comment)"}
        '''
        items = dict()
        comments = dict()
        for line in open(groupfile, "r"):
            data = line.strip().split("\t")
            name = data[0]
            if len(data) > 1:
                weight = int(data[1])
            else:
                weight = 1
            comment = "w {}".format(weight)
            if len(data) > 2:
                comment = comment + ", " + data[2] 
            comment = "({})".format(comment)
            items[name] = weight
            comments[name] = comment
        return items, comments
    

    def find_by_name(self, text: str, toscreen: bool = True) -> set:
        '''
        Return a set of items that contain the text provided.
        
        '''
        items = set()
        for item in self.locdict.values():
            for orient in item.data.values():
                items.update(set([item for item in orient["items"].keys() \
                                 if text in item.lower()])) 
        if toscreen:
            print('\n'.join(item for item in items))
        return items

      
    def build_droptable(self) -> pd.DataFrame:
        '''
        Return a pandas dataframe containing, for each row, a findable object in a location.
        
        '''
        header = ["Location", "i/o", "Item", "Base search %", "Total items", "This item", "Mortal odds", "Mortal find %"]
        lines = []
        for name, location in self.locdict.items():
            for orient, odds in self.memoized_locs[name].items():
                for item in location.data[orient]["items"]:
                    lines.append([name, orient, item, \
                                  location.data[orient]["find"] + 10, \
                                  location.data[orient]["total"], \
                                  location.data[orient]["items"][item], \
                                  odds, \
                                  100 * min(1, odds / 100) * location.data[orient]["items"][item] / location.data[orient]["total"]])
        
        return pd.DataFrame(lines, columns = header)
        
        
    def text_for_wiki(self, data: dict, complete: int, mention: int) -> str:
        """
        Parameters
        ----------
        data : dict
            a dictionary from the output of self.search_item()
        complete : int
            The number of hits that should be returned as completetext
        mention : int
            The number of hits that should be returned as simple listing of names.
        Returns
        -------
        toprint
            a string with location find % that can be inserted into the Wiki page.
        """
        
        if not complete:
            complete = 5
        if not mention:
            mention = 10
        
        toprint = []
        also = []
        etctext = "and others"
        for i, (item, value) in enumerate(sorted(data.items(), key=lambda x:x[1], reverse=True)):
            name = item[:item.index("(")-1]
            if (complete == 0) or (i < complete):
                location = item[item.index("(")+1:-1]
                if location == 'inside':
                    check = 'outside'
                elif location == 'outside':
                    check = 'inside'
                if self.locdict[name].data.get(check, False):
                    location = ' ' + location
                else:
                    location = ''
                toprint.append("\n* [[{}]]{}: {}".format(name, location, format_percent(value)))
            elif i < complete + mention:
                newtext = "[[{}]]".format(name)
                if newtext not in also:
                    also.append("[[{}]]".format(name))
            elif etctext not in also:
                also.append(etctext)
        toprint = "\n'''Main locations:''' \n" + ''.join(toprint) + '\n'
        if len(data) > complete:
            toprint = toprint + "'''Other locations:''' " + ', '.join(also) + '.\n'
        return toprint
    
    