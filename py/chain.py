# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 17:13:50 2018

@author: Zhen
"""

from zi import Zi

class Chain(object):
    '''
    Abstract class to handle derivation chains of Chinese characters
    '''    
    def __init__(self):
        self.chains = []     # List of derivation chains        
        
    def _print_one_chain(self, chain, verbose=False):
        '''
        Print derivative chain in a human-readable fashion
        '''
        if len(chain) == 0:
            print("Empty chain")
            return
        if verbose:
            print(chain[0])
            for i in range(1, len(chain)):
                print('   '*i, "->", chain[i])
        else:
            print(" -> ".join([z.zi + '(' + z.pinyin + ')' for z in chain]))
            
    def print_top_chains(self, top_n=5, verbose=False):
        '''
        Print first n chains in chain list
        '''
        for chain in self.chains[:top_n]:
            self._print_one_chain(chain, verbose=verbose)
            
    def print_chain(self, idx, verbose=False):
        '''
        Print first n chains in chain list
        '''
        assert 0 <= idx < len(self.chains), \
            "Index out of range: %d, %d chains found" % (idx, len(self.chains))
        self._print_one_chain(self.chains[idx], verbose=verbose)
        
        

class SoundDerivationChain(Chain):
    '''
    Derived from abstract Chain class
    Representing chain of Zi based on sound derivation relationship
    '''        
    def build_chains_from_zi_list(self, zi_list):
        '''
        Take a list of Zi, build and return a list of shengpang-based derivative
        chain by Depth First Search
        '''
        # Build dict, make warning if there is any duplicates
        zi_dict = dict()
        for z in zi_list:
            if z.zi in zi_dict.keys():
                print("Duplicates! ", z, zi_dict[z.zi])
            zi_dict[z.zi] = z
        print(len(zi_dict))
    
        # Add edges
        for z in zi_list:
            if z.sheng[0] >= Zi.SHENG_THRESHOLD:
                if z.sheng[1] in zi_dict.keys():
                    zi_dict[z.sheng[1]].add_sheng_deriv(z)
                else:
                    zi_dict['Uninitialized'].add_sheng_deriv(z)
                    
        # Start DFS from each root and save derivation chains
        def DFS(current_zi, prefix=[]):
            new_prefix = prefix[:] + [current_zi]
            if current_zi in prefix:
                print("Loop exists!!")
                self.chains.append(new_prefix)
                self.print_one_chain(new_prefix, verbose=True)
            if not current_zi.has_sheng_deriv():        # Leaf node
                self.chains.append(new_prefix)
            else:
                for deriv_zi in current_zi.sheng_derivatives:
                    DFS(deriv_zi, new_prefix)
    
        for z in zi_list:
            if z.sheng[0] >= Zi.SHENG_THRESHOLD:        # Has shengpang, not root
                continue
            DFS(z, prefix=[])           # Do DFS for each root in the forest
            
        # Sort by chain length
        self.chains.sort(key=lambda x: len(x), reverse=True)
        return self.chains

