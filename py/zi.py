# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 22:25:59 2018

@author: Zhen
"""

import re

punctuation = ",，。；“” "

class Zi(object):
    '''
    Data structure for a Chinese character, focusing on sound derivation
    '''
    SHENG_THRESHOLD = 0.45
    
    def __init__(self, filename):
        if filename is None:        # Empty constructor
            self.juan = 'Uninitialized'
            self.bu = 'Uninitialized'
            self.zi = 'Uninitialized'
            self.pinyin = 'Uninitialized'
            self.fanqie = 'Uninitialized'
            self.meaning = 'Uninitialized'
            self.sheng = (0, ' ', 'Uninitialized')
        else:
            with open(filename, 'r', encoding="utf8") as f:
                lines = [line.strip() for line in f]
            self.juan = lines[0]
            self.bu = lines[1]
            self.zi = lines[2]
            self.pinyin = lines[3]
            self.fanqie = lines[4]
            self.meaning = ' '.join(lines[5:])
            self.sheng = (0, ' ', 'Uninitialized')  # (possibility of Xingsheng,
                                                    #  shengpang, notes)
        self.sheng_derivatives = []             # list of Zi
        
    def guess_sheng(self):
        '''
        Guess and return the shengpang of zi
        '''
        THRESHOLD = 0.5
        if '聲' not in self.meaning:
            self.sheng = (0, ' ', 'Not Xingsheng')
        else:
            sheng_idx = [m.start() for m in re.finditer('聲', self.meaning)]
            possibilities = [self.get_sheng_from_index(sheng_idx[0], 0,
                                                       self.meaning)]
            for i in range(1, len(sheng_idx)):
                possibilities.append(self.get_sheng_from_index(sheng_idx[i],
                                                               sheng_idx[i-1],
                                                               self.meaning))
            possibilities.sort(key=lambda s: s[0], reverse=True)
            if 0 < possibilities[0][0] < THRESHOLD:
                print("Tricky case for", self.zi, 
                      possibilities[0][2], self.meaning)
            elif len(possibilities) >= 2 and possibilities[1][0] >= THRESHOLD:
                print("Tricky case for", self.zi,
                      "Too many Sheng!", self.meaning, possibilities)
            self.sheng = possibilities[0]
        return self.sheng
              
    def get_sheng_from_index(self, idx, prev_idx, meaning):
        '''
        Return (possibility, shengpang, notes) representing how an index of 
        sheng is possible to indicate the sheng of zi;
        The result is specifically for each one occurance of "聲" in an entry,
        not for the zi itself.
        '''
        SHENG_PUNCT_NORMAL = 2
        SPECIAL_SHENG_PUNCT_NORMAL = 3
        LAST_CONG_NORMAL = 3
        LAST_CONG_THRESHOLD = 10
        
        # 音 聲也。生於心，有節於外，謂之音。
        if idx < max(LAST_CONG_NORMAL, SPECIAL_SHENG_PUNCT_NORMAL):
            return (0, ' ', 'Not Xingsheng')
        
        # 宮商角徵羽，聲；
        # 鶴 鳴九臯，聲聞于天
        elif meaning[idx-1] in punctuation:
            return (0, ' ', 'Not Xingsheng')
        
        elif meaning[idx-1] in ['省', '亦']:
            # 涕流皃。从水，𢿱省聲
            if meaning[idx-SPECIAL_SHENG_PUNCT_NORMAL] in punctuation:
                return (1, meaning[idx-SPECIAL_SHENG_PUNCT_NORMAL+1],
                        meaning[(idx-1):(idx+1)])
            # 步處也。从辵亦聲
            # 木參交以枝炊䉛者也。从木省聲。
            # False positive: 筋之本也。从筋，从夗省聲。
            elif meaning[idx-LAST_CONG_NORMAL] == '从':
                return (0.8, meaning[idx-1], '聲')
            else:
                # 从車从行。一曰衍省聲。
                # 𠔁 分也。从重八。八，別也。亦聲。
#                print("Tricky case 1:", self.zi, self.meaning, 
#                      idx, meaning[(idx-SPECIAL_SHENG_PUNCT_NORMAL):(idx+1)])
                return (0.4, meaning[idx-2], 'Probably Xingsheng')
            
        # 䇂，惡聲也。
        # 鳥獸來食聲也。
        elif idx < len(meaning) - 1 and meaning[idx+1] == '也':
            return (0.1, meaning[idx-1], 'Probably NOT Xingsheng')
        
        elif meaning[idx-SHENG_PUNCT_NORMAL] in punctuation:
            # 惑也。从子、止、匕，矢聲。
            # 急戾也。从弦省，少聲。
            # False positive: 潺湲，水聲。从水爰聲。
            if idx == len(meaning)-1 or meaning[idx+1] in punctuation:
                return (0.7, meaning[idx-1], '聲')
            # 䚡理自外，可以知中，義之方也；其聲舒揚，尃以遠聞，智之方也；
            else:
#                print("Tricky case 2:", self.zi, self.meaning, 
#                          idx, meaning[max(0, idx-LAST_CONG_THRESHOLD):(idx+1)])
                return (0.2, meaning[idx-1], 'Probably NOT Xingsheng')
            
        elif '从' in meaning[prev_idx:idx]:
            # 从金复聲。
            if meaning[idx-LAST_CONG_NORMAL] == '从':
                return (1, meaning[idx-1], '聲')   
            # 加也。从言，从曾聲。
            elif meaning[idx-LAST_CONG_NORMAL+1] == '从':
                return (1, meaning[idx-1], '聲')
            else:
                for cong_idx in range(LAST_CONG_NORMAL, (LAST_CONG_THRESHOLD+1)):
                    # 从韋，取其帀也；倝聲
                    # 从木；入，象形；䀠聲
                    if idx >= cong_idx and meaning[idx-cong_idx] == '从' \
                    and any([x in punctuation for x in meaning[(idx-cong_idx):idx]]):
                        # 䪢 墜也。从韭，次、𠂔皆聲。
                        if '皆' in meaning[(idx-cong_idx):idx]:
                            return (0.5, meaning[idx-2], '聲')
                        elif '也' in meaning[(idx-cong_idx):idx]:
                            return (0.7, meaning[idx-1], '聲')
                        else:
                            return (0.6, meaning[idx-1], '聲')
                # 牟 牛鳴也。从牛，象其聲气从口出。
#                print("Tricky case 3:", self.zi, self.meaning, 
#                          idx, meaning[max(0, idx-LAST_CONG_THRESHOLD):(idx+1)])
                return (0.2, meaning[idx-1], 'Probably NOT Xingsheng')
            
        else:
            # 猩 猩猩，犬吠聲。
            # 𠷓 聲也。从只甹聲。讀若聲。
#            print("Tricky case 4:", self.zi, self.meaning, 
#                      idx, meaning[(idx-3):(idx+1)])
            return (0, ' ', 'Not Xingsheng')
        
    def __str__(self):
        return ','.join([self.zi, self.juan, self.bu, self.pinyin,
                         self.sheng[1] + self.sheng[2],
                         "   释义:" + self.meaning[:15] + "..."])
    
    def __repr__(self):
        return self.__str__()
    
    def add_sheng_deriv(self, deriv):
        self.sheng_derivatives.append(deriv)
        
    def has_sheng_deriv(self):
        return len(self.sheng_derivatives) > 0
