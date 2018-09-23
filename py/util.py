# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 22:46:16 2018

@author: Zhen
"""

from requests import get
from requests.exceptions import RequestException
from contextlib import closing

def simple_get(url):
    """
    Attempts to get the content at url by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            content_type = resp.headers['Content-Type'].lower()
            if resp.status_code == 200 \
            and content_type is not None \
            and content_type.find('html') > -1:
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
