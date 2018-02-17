import unittest
import re
import pickle
from pprint import pprint
from collections import Counter
import os
import numpy as np
import pandas as pd

class TestAll(unittest.TestCase):

    def test_count(self):
        with open('Kamchatka_wds_by_mor.pickle', 'rb') as f:
            mor = Morphemes(pickle.load(f), 'Kamchatka')
        i = mor.morphemes[('-WEːČ', '-gnr', 'v')]
        # for oi in mor.morpheme_by_speaker_count():
        #     pass
        # print(i)
        self.assertTrue(i in range(1870, 2000))

    def test_dp(self):
        expected = {'AAS': 0.02074776516066683,
                     'AEI': 0.045240396230973666,
                     'AFI': 0.0034126600628171058,
                     'AGK': 0.005707900459048079,
                     'AL': 0.00012080212611741966,
                     'AMG': 0.0024160425223483935,
                     'AS': 0.038294273979222034,
                     'ASA': 0.012442618990094226,
                     'BP': 0.00184223242329065,
                     'DBA': 0.006795119594104856,
                     'EGA': 0.038868084078279776,
                     'EIA': 0.07749456390432471,
                     'EPA': 0.01461705726020778,
                     'GAS': 0.01848272529596521,
                     'GIK': 0.046720222275912056,
                     'INB': 0.005979705242812274,
                     'JET': 0.013831843440444552,
                     'JIP': 0.015190867359265524,
                     'LGT': 0.02298260449383909,
                     'NA': 0.00012080212611741966,
                     'NAT': 0.01854312635902392,
                     'NFI': 0.025459048079246194,
                     'NIG': 0.15716356607876297,
                     'NMK': 0.0190263348634936,
                     'ONI': 0.010328581783039381,
                     'PMB': 0.02044575984537328,
                     'RME': 0.23254409277603286,
                     'RMS': 0.0614278811307079,
                     'TEB': 0.012865426431505194,
                     'VIA': 0.05043488765402271,
                     'rh': 0.00045300797294032375}
        observed = {'AAS': 0.333333333333333,
                     'AEI': 0.0,
                     'AFI': 0.0,
                     'AGK': 0.0,
                     'AL': 0.0,
                     'AMG': 0.0,
                     'AS': 0.0,
                     'ASA': 0.0,
                     'BP': 0.0,
                     'DBA': 0.0,
                     'EGA': 0.66666666666666,
                     'EIA': 0.0,
                     'EPA': 0.0,
                     'GAS': 0.0,
                     'GIK': 0.0,
                     'INB': 0.0,
                     'JET': 0.0,
                     'JIP': 0.0,
                     'LGT': 0.0,
                     'NA': 0.0,
                     'NAT': 0.0,
                     'NFI': 0.0,
                     'NIG': 0.0,
                     'NMK': 0.0,
                     'ONI': 0.0,
                     'PMB': 0.0,
                     'RME': 0.0,
                     'RMS': 0.0,
                     'TEB': 0.0,
                     'VIA': 0.0,
                     'rh': 0.0}
        print('printing dp')
        print(dp(expected, observed))
        self.assertTrue(dp(expected, observed)<0.0001)


class MorphemeError(Exception):
    '''raised if morpheme is empty'''
    def __init__(self, message='Length of lists not equal'):
        super(MorphemeError, self).__init__()
        self.message = message
    def __str__(self):
        return repr(self.message)


class Morphemes():


    def __init__(self, content, corpus):
        self.content = content
        self.corpus = corpus
        self.morphemes = self.morpheme_count()
        if '0' in self.morphemes or 0 in self.morphemes:
            raise MorphemeError('0 morphemes in morpheme_count')
        self.raw_speakers = self.raw_speaker_count()
        self.speakers = self.speaker_count()


    def morpheme_count(self):
        '''returns dict with overall count for morphemes (ignoring speakers)'''
        items = [x[:3] for x in self.content if x[0][0] in '-=']
        return Counter(items)


    def morpheme_by_speaker_count(self):
        '''generates dict morpheme: Counter(by speaker)'''
        for morpheme in self.morphemes:
            count = Counter([x[-1] for x in self.content if x[:3]==morpheme])
            res = {x: count[x]/self.morphemes[morpheme] for x in count}
            # print('printing {}'.format(morpheme))
            # pprint(res)
            # raise LengthError()
            yield (morpheme, res)


    def calculate_dp(self):
        '''well, calculates dp for all morphemes'''
        res = {'morpheme': [], 'count': [], 'dp': []}
        for sp in self.speakers:
            res[sp] = []
        for mor, counts in self.morpheme_by_speaker_count():
            res['morpheme'].append('-'.join(list(map(lambda x: x.strip('-='), mor))))
            res['count'].append(self.morphemes[mor])
            res['dp'].append(dp(self.speakers, counts))
            if not sum(counts.values()) > 0.999:
                print(mor)
                print(self.morphemes[mor])
                pprint(counts)
                print(sum(counts.values()))
                raise MorphemeError('just stopping')
            for sp in self.speakers:
                if sp in counts:
                    res[sp].append(counts[sp])
                else:
                    res[sp].append(0)
        return res


    def raw_speaker_count(self):
        '''returns dict with the number of words every speaker said in a corpus'''
        items = [x[-1] for x in self.content if x[0]=='END']
        return Counter(items)


    def speaker_count(self, totals = {'Kamchatka': 33112, 'Sebjan': 49800}):
        '''returns dict with proportions of every speaker in a corpus'''
        res = {x: self.raw_speakers[x]/totals[self.corpus] for x in self.raw_speakers}
        # pprint(res)
        # print(sum(res.values()))
        return res


def dp(expected, observed):
    # step = {sp: expected[sp]-observed[sp] if sp in observed else expected[sp] for sp in expected}
    deltas = []
    for sp in expected:
        if sp in observed:
            delta = np.abs(expected[sp]-observed[sp])
        else:
            delta = 0
        deltas.append(delta)
    dp = sum(deltas) / 2
    return dp



def main():
    corpora = ['Kamchatka', 'Sebjan']
    for corp in corpora:
        with open('{}_wds_by_mor.pickle'.format(corp), 'rb') as f:
            mor = Morphemes(pickle.load(f), corp)
        res = mor.calculate_dp()
        columns = ['morpheme', 'count', 'dp'] + sorted(list(mor.speakers.keys()))
        pd.DataFrame(res).loc[pd.DataFrame(res)['count']>15].sort_values('dp', ascending=False)[columns].to_excel('{}_dp_new.xlsx'.format(corp))
        print('{} done'.format(corp))
    print('all done')


if __name__ == '__main__':
    # unittest.main()
    main()
