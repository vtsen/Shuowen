# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 22:25:59 2018

@author: Zhen
"""

import os
import os.path as path

from zi import Zi
from chain import SoundDerivationChain as SDC


if __name__ == "__main__":
    '''
    A simple preliminary research on sound derivation of Chinese characters
    based on Shuowen-Jiezi
    '''    
    root_path = path.dirname(path.dirname(path.realpath(__file__)))
    data_path = path.join(root_path, "data")
    zi_list = []  
    
    # Read from file
    for filename in os.listdir(data_path):
        zi_path = path.join(data_path, filename, filename)
        z = Zi(zi_path)
        z.guess_sheng()
        zi_list.append(z)
    zi_list.append(Zi(None))
    print(len(zi_list), "zi read from file.")

    # Build derivation chains
    shuowen_sdc = SDC()
    shuowen_sdc.build_chains_from_zi_list(zi_list)
        
    # Print longest chains
    shuowen_sdc.print_top_chains(10, verbose=True)
    shuowen_sdc.print_top_chains(50)
    shuowen_sdc.print_chain(1000, verbose=True)
    shuowen_sdc.print_chain(3619, verbose=True)
#    shuowen_sdc.print_chain(10000, verbose=True)

    # Estimate Xingsheng ratio
    num_xingsheng = sum([1 for z in zi_list if z.sheng[0] > Zi.SHENG_THRESHOLD])
    print(num_xingsheng, num_xingsheng / float(len(zi_list)))
    