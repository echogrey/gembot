# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 23:06:46 2017

@author: eric
"""

import json
from multiprocessing import Pool
import requests
from requests.exceptions import RequestException
import re

def get_one_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
        
def parse_one_page(html):
    pattern = re.compile('<tr><td class="frst">.*?Destination.*?</td><td class="frst1">(.*?)</td></tr><tr><td class="frst">'
                        +'.*?University Name.*?</td><td class="frst1">(.*?)</td></tr><tr><td class="frst">'
                        +'.*?Programme Type.*?</td><td class="frst1">(.*?)</td></tr><tr><td class="frst">'
                        +'.*?Programme Category.*?</td><td class="frst1">(.*?)</td></tr><tr><td class="frst">'
                        +'.*?Number of AUs.*?</td><td class="frst1">(.*?)</td></tr><tr><td class="frst">'
                        +'.*?Type of AUs.*?</td><td class="frst1">(.*?)</td></tr><tr><td class="frst">'
                        +'.*?Programme Cost.*?</td><td class="frst1">(.*?)</td></tr><tr><td class="frst">'
                        +'.*?Type of Financial Aid Available.*?</td><td class="frst1"><font size="2" color="#000000">(.*?)</font></td></tr><tr><td colspan="2" style="font-size: 13px;">', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'Destination':  item[0],
            'University Name':  item[1],
            'Programme Type':   item[2],
            'Programme Category':   item[3],  
            'Number of AUs':    item[4],
            'Type of AUs':  item[5],
            'Programme Cost':   item[6],
            'Type of Financial Aid Available':  item[7]           
        }        
        
def write_to_file(content):
    with open('result.txt', 'a') as f:
        f.write(json.dumps(content)+'\n')
        f.close
        
        
def main(destination):
    url = 'http://global.ntu.edu.sg/GMP/gemdiscoverer/Pages/FacetSearchResult.aspx?Destination='+str(destination)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
    
if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i for i in ['Austria','Brunei','Canada','China','Costa%20Rica','Croatia','Denmark','France','Germany','Hong Kong','India','Indonesia','Israel','Italy','Japan','Korea','Malaysia','Mexico','Norway','Peru','Philippines','Russia','South%20Africa','Spain','Sweden','Taiwan','Thailand','Turkey','Uruguay','United%20Kingdom','United%20States%20of%20America','Uruguay','Vietnam']])
    pool.close()
    pool.join()
