import unittest
import re
import pickle
from pprint import pprint
from collections import Counter
import os

class TestAll(unittest.TestCase):

    def test_count(self):
        i = ''
        o = ''
        self.assertEqual(i, o)


class Morphemes():


    def __init__(self, content):
        self.content = content


    def morpheme_count(self):
        '''returns overall count for morphemes (ignoring speakers)'''
        items = [x[:3] for x in self.content if x[0][0] in '-=']
        return Counter(items)


    def speaker_count(self):
        '''returns dict with number of words every speaker says in a corpus'''
        items = [x[-1] for x in self.content if x[0]=='END']
        return Counter(items)


def main():
    corpora = ['Kamchatka', 'Sebjan']
    for corp in corpora:
        # with open('{}_wds_by_mor.pickle'.format(corpus), 'rb') as f:
        #     morphemes = pickle.load(f)
        pass
    print('all done')


if __name__ == '__main__':
    unittest.main()
    # main()
