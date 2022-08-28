# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 13:17:19 2022

@author: Roberto
"""

import re

class Location():
    def __init__(self, bspage):
        self.page = bspage
        self.name = self.page.h1.text
        self.plane = "General" # "General", "Stygia", "Elysium"
        self.data = dict() # "inside", "outside"
        self.hide = None
        self.parse_data()
        
    def parse_data(self):
        try:
            # Determine the plane
            tables = self.page.find_all("table")
            if "Stygia Locations" in [a.text for a in self.page.find_all("a")]:
                self.plane = "Stygia"
            elif "Elysium Locations" in [a.text for a in self.page.find_all("a")]:
                self.plane = "Elysium"
            # Get the main tables
            self.find_pc_table = None
            self.outside_table = None
            self.inside_table = None
            for table in tables:
                ths = table.find_all("th")
                for th in ths:
                    if th.text.startswith("Outside"):
                        self.find_pc_table = table
                    elif table.caption:
                        if table.caption.text.startswith("Items found outside"):
                            self.outside_table = table
                        if table.caption.text.startswith("Items found inside"):
                            self.inside_table = table  
            # Get the base find % and hide %
            out_in = [False, False]
            for tr in self.find_pc_table.find_all("tr"):
                if "Outside\n\nInside" in tr.text:
                    order = "N"
                elif "Inside\n\nOutside" in tr.text:
                    order = "R"
                if "Find" in tr.text:
                    search = re.search('Find.+?\n\n(\d+?|N\/A)\s+?(\d+?|N\/A)\n', tr.text)
                    if search[1] != "N/A": 
                        out_in[order!="N"] = int(search[1])
                    if search[2] != "N/A":
                        out_in[order=="N"] = int(search[2])
                if "Hide" in tr.text:
                    search = re.search('Hide.+?\n\n(\d+?|N\/A)\s+?(\d+?|N\/A)\n', tr.text)
                    hide_text = search[(order=='N') + 1]
                    if hide_text != 'N/A':
                        self.hide = int(hide_text) # We only care about hiding inside
                    else:
                        self.hide = False
                if any(out_in) and self.hide is not None:
                    break
                
                
            # Get the inside and outside tables
            for orient, table in ("outside", self.outside_table), ("inside", self.inside_table):
                if table is not None:
                    self.data[orient] = dict()
                    items = re.findall("\n([\S ]+?)\n(\d+?)\n", table.text)
                    self.data[orient]["items"] = dict([(x[0], int(x[1])) for x in items])
                    self.data[orient]["total"] = sum(self.data[orient]["items"].values())
                    self.data[orient]["find"] = out_in[orient=="inside"]
            self.ok = True
        except:
            self.ok = False
            pass
                        
    def __repr__(self):
        return '<Location_"{}">'.format(self.name)