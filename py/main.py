# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 22:25:59 2018

@author: Zhen
"""

import os
import os.path as path
import argparse

from zi import Zi
from chain import SoundDerivationChain as SDC
from data_fetch import SimpleDataScrapper, FullInfoDataScrapper


def str2bool(v):
    '''
    Facilitate reading boolean arguments represented as string
    '''
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        
        
if __name__ == "__main__":
    '''
    A simple preliminary research on sound derivation of Chinese characters
    based on Shuowen-Jiezi
    '''    
    root_path = path.dirname(path.dirname(path.realpath(__file__)))
    data_path = path.join(root_path, "data")
    zi_list = []
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Shuowen structure project")
    parser.add_argument("--need_refetch", dest="need_refetch", type=str2bool,
                        default=False,
                        help="True if need to refetch data from website")
    parser.add_argument("--scrapper_type", dest="scrapper_type", type=str,
                        default="Simple",
                        help="Type of scrapper")    
    args = parser.parse_args()
    
    print("\nParameters:")
    for attr, value in args.__dict__.items():
        print("\t{}={}".format(attr.upper(), value))
    
    # Refetch data from website if required
    if args.need_refetch:
        if args.scrapper_type.lower() == "simple":
            scrapper = SimpleDataScrapper()
        elif args.scrapper_type.lower() == "full":
            scrapper = FullInfoDataScrapper()
        else:
            print("Only 'simple' and 'full' supported. Using simple in default.")
            scrapper = SimpleDataScrapper()
        scrapper.set_data_path(data_path)
        scrapper.get_data()
    
    # Read from file
    for filename in os.listdir(data_path):
        zi_path = path.join(data_path, filename, filename)
        z = Zi(zi_path)
        z.guess_sheng()
        zi_list.append(z)
    zi_list.append(Zi(None))
    print('\n\n', len(zi_list), "entries read from file.\n----\n")

    # Build derivation chains
    shuowen_sdc = SDC()
    shuowen_sdc.build_chains_from_zi_list(zi_list)
    print('\n\n', len(shuowen_sdc.chains), "chains found.\n----\n")
        
    # Print longest chains
    shuowen_sdc.print_top_chains(3, verbose=True)
    shuowen_sdc.print_top_chains(10)
    shuowen_sdc.print_chain(1000, verbose=True)
    shuowen_sdc.print_chain(3619, verbose=True)
#    shuowen_sdc.print_chain(10000, verbose=True)

    # Estimate Xingsheng ratio
    num_xingsheng = sum([1 for z in zi_list if z.sheng[0] > Zi.SHENG_THRESHOLD])
    print("{0} out of {1} entries are Xingsheng, {2:.2%}".format(num_xingsheng,
          len(zi_list),
          num_xingsheng / float(len(zi_list))))
    
    #TODO: use networkx to plot DAG
    