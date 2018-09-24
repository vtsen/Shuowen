# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 15:54:27 2018

@author: Zhen
"""

import os
import os.path as path
import time
import requests
from numpy import random as rd
from util import simple_get
from bs4 import BeautifulSoup

class DataScrapper(object):
    '''
    Scrap Shuowen data from website
    '''
    def __init__(self,
                 url_prefix="http://www.shuowen.org/view/",
                 indices=list(range(1, 9834))):
        root_path = path.dirname(path.dirname(path.realpath(__file__)))
        self.data_path = path.join(root_path, "data")
        self.url_prefix = url_prefix
        self.minimum_wait_time_sec = 1.0
        self.max_extra_wait_time_sec = 1.0
        self.indices = indices     # indices from source website
        
    def set_data_path(self, data_path):
        self.data_path = data_path
        
    def set_wait_time(self, minimum_wait_time_sec, max_extra_wait_time_sec):
        '''
        Set up wait time to be min_time + Unif(0, max_extra_time)
        Keep it not too low so that server will not be overloaded
        '''
        self.minimum_wait_time_sec = minimum_wait_time_sec
        self.max_extra_wait_time_sec = max_extra_wait_time_sec
        
    def get_data(self, indices=None):
        '''
        Fetch data from url specified by indices
        '''
        MAX_SUPPRESS = 1000
        if indices is None:
            indices = self.indices
        omitted = []
        for i in rd.permutation(indices):
            try:
                data_path = path.join(self.data_path, str(i))
                if path.exists(data_path):
                    omitted.append(i)
                    if len(omitted) >= MAX_SUPPRESS:
                        print("Omitted", len(omitted), "existing entries...")
                        omitted = []
                    continue
                if len(omitted) > 0:
                    print("Omitted", len(omitted), "existing entries...")
                os.makedirs(data_path)
                html = BeautifulSoup(simple_get(self.url_prefix + str(i)),
                                         "html.parser")
                self.extract_and_save(html, data_path, i)
                self.wait()
            except:
                continue
                
    def extract_and_save(self, html, data_path, idx):
        raise NotImplementedError
        
    def wait(self):
        time.sleep(self.minimum_wait_time_sec \
                   + rd.rand()*self.max_extra_wait_time_sec)


class SimpleDataScrapper(DataScrapper):
    '''
    A simple scrapper that only stores minimum information for analysis
    This allows the dataset to be reasonably small. All characters from
    shuowen.org can be described using these minimum features within 1M.
    
    Caveat: This is a dumb method! Correctness depends on website structure
    as of 2018/09/23.
    '''
    def extract_and_save(self, html, data_path, idx):
        info = html.select('div')[8].select('div')[2]
        juan = info.select('div')[1].select('a')[0].text
        bu = info.select('div')[1].select('a')[1].text
        pinyin = info.select('div')[2].select('a')[0].text
        fanqie = info.select('div')[2].text.split('|')[-1].strip()
        zi = info.select('div')[3].select('span')[0].text
        meaning = info.select('div')[3].select('div')[1].text.strip()
        
        print([juan, bu, zi, pinyin, fanqie, meaning])
        
        with open(path.join(data_path, str(idx)), 'w',
                      encoding="utf8") as f:
            f.write('\n'.join([juan, bu, zi, pinyin, fanqie, meaning]))
            
        
class FullInfoDataScrapper(SimpleDataScrapper):
    '''
    Save all website info and image of the character, on top of the minimal
    dataset in SimpleDataScrapper
    '''
    def extract_and_save(self, html, data_path, idx):
        # First save minimal data too
        SimpleDataScrapper.extract_and_save(self, html, data_path, idx)
        
        # Save all information on website
        with open(path.join(data_path, str(idx) + '_all'), 'w',
                      encoding="utf8") as f:
            f.write(str(html))
        self.wait()
        
        # Save image of Zhuanshu
        img_url = html.select('div')[8].select('div')[0].find_all('img')[0]['src']
        f = open(path.join(data_path, img_url.split('/')[-1]), 'wb')
        f.write(requests.get(img_url).content)
        f.close()