# -*- coding: utf-8 -*-

# Copyright (c) <2014>, <Mohamed Sordo>
# Email: mohamed ^dot^ sordo ^at^ gmail ^dot^ com
# Website: http://msordo.weebly.com
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.


import types

class DefaultCleaner:
    def __init__(self):
        pass
    
    def is_string(self, item):
        return type(item) == types.StringType
    
    def clean(self, item):
        if not self.is_string(item):
            return None
        return item

class LowerCaseCleaner(DefaultCleaner):
    def clean(self, item):
        if not self.is_string(item):
            return None
        return item.lower()
    
class TagCleaner(DefaultCleaner):
    def clean(self, tag, blacklist=[]):
        if not self.is_string(tag):
            return None
        #input: tag
        #output clean tag or None (tag removed)
        tag = tag.lower()
        if tag in blacklist :
            return ''
    
        #Some special cases
        if len(tag) == 1:
            return ''
        if tag.find('better than') != -1 :
            return ''
    
        #If tag contain this word, then remove tag
        for word in ['seen live', 'TODO'] :
            if tag.find(word) != -1 :
                return ''
    
        #Clean special chars
        tag = tag.replace("-s", 's')
        tag = tag.replace("'", '')
        tag = tag.replace("´", '')
        tag = tag.replace(":", '')
        tag = tag.replace("&", ' and ')
        tag = tag.replace('amazing', '')
        tag = tag.replace('awesome', '')
        tag = tag.replace('i kind of like', '')
    
        #Plural => Singular
        tag = tag.replace('artists', 'artist')
        tag = tag.replace('albums', 'album')
        tag = tag.replace('ballads', 'ballad')
        tag = tag.replace('bandas', 'banda')
        tag = tag.replace('guitars', 'guitar')
        tag = tag.replace('guitarists', 'guitarist')
    
        #Misspellings
        tag = tag.replace('alternaive', 'alternative')
        tag = tag.replace('alternaitve', 'alternative')
    
        #Opinions about artists and bands...
        for word in ['artist', 'band'] :
            if tag.find(word + ' to') == 0 :
                return ''
            if tag.find(word + ' who') == 0 :
                return ''
            if tag.find(word + ' with') == 0 :
                return ''
        #Personal opinions
        for word in ['i like', 'i own', 'i have', ' ive ', ' i ve ', 'i want', 'i should', 'i bet ', 'i am ', 'i really ', 'i adore ', 'i do ', 'i dunno ', 'i feel ', 'i found ', 'i get ', 'i got ', 'i fuckin', 'i need ', 'i can', 'i could ', 'i did','i dig ', 'i discov', 'i had ', 'i hate', 'i love', 'i luv ', 'i hope ', 'i just ', 'i know ', 'i  knew', 'i listen ', 'i ll ', 'i made ', 'i miss ', 'i must ', 'i never ', 'i noticed ', 'i play', 'i prefer '] :
            if tag.find(word) != -1 :
                return ''
    
        # ' ', '  ', '-', , '--', '_', '~' => '_'
        tag = tag.replace(' - ', '-')
        tag = tag.replace('---', '')
        tag = tag.replace('--', '-')
        tag = tag.replace('- ', '-')
        tag = tag.replace('  ', '')
        for char in [' ', '-', '~'] :
            tag = tag.replace(char, '_')
            #tag = tag.replace(char, '')
    
        tag = tag.replace('_', '') #returns hiphop not hip_hop
        if len(tag) == 1 :
            return ''
    
        return tag