import unittest
import re
import pickle
from pprint import pprint
import os


class TestAll(unittest.TestCase):

    # def test_speaker(self):
    #     self.assertEqual(define_speaker({'ELANParticipant': ['40:18']}), 'none')
    #     self.assertEqual(define_speaker({'mb': [['so']], 'ge': [['not']]}), 'none')
    #     self.assertEqual(define_speaker({'ELANParticipant': ['AMD']}), 'AMD')
    #     self.assertEqual(define_speaker({'ELANParticipant': ['']}), 'none')

    def test_meta_speaker(self):
        i = """\ref Recorded on 14 June 2009 in Esso by Natalia Aralova and Brigitte Pakendorf. BP and NA went to visit the Amganovs,
        where we first drank tea, looked at their photo album and asked some questions; only after an hour did we get out the
        recording equipment. NA was in charge of the video, while BP monitored the Marantz recorder. Only EIA and EPA
        were present (in addition to BP and NA); however, somewhere in the middle of the recording a daughter or two plus
        grandkids slipped in and out - but they did not join in the storytelling. Other than that there were hardly any
        surrounding noises. EIA was in a storytelling mood and kept remembering humourous little anecdotes, which he
        recounted with a lot of accompanying gestures. In between he gave Russian summaries/retold it all in Russian - but the
        video files were cut in such a way as to exclude that (except where he switched to Russian in the middle of an Even
        narrative). The individual anecdotes (11 in total, varying in length from 1 minute to 12 minutes) were analysed
        individually, as individual ELAN/Toolbox files. This is the 5th little anecdote.
        \qu Transcribed by BP with Rimma Maksimovna Egorova, who also provided the Russian translation; glossed by BP. Funding by the
        Volkswagen Foundation (DoBeS grant). Speaker abbreviation = EIA, EPA
        \ref Efim Innokent'evich Amganov was born in 1952, i.e. he was 56-57 at the time of the recording. He had a college-level
        education and worked as a driver before going on pension. He passed away in 2012.
        \ref Elena Petrovna Amganova was born in 1952, i.e. she was 56-57 at the time of the recording. She had 8 years of schooling
        and had worked as a milker and then a cleaner. """
        o = ['EIA', 'EPA']
        self.assertEqual(meta_speakers(i), o)
        i = """\ref Recorded 27 June 2009 in Esso by Natalia Aralova and Brigitte Pakendorf. NA and BP went to the house of the
        Amganovs on purpose to ask EPA to narrate a recording; this was already the 5th or 6th visit of NA (who had been
        recording the phonological word list with EPA's husband Efim) at the Amganov's house - so the whole set-up with
        video-camera and taking down the loudly ticking clock etc were quite familiar; on the other hand, EPA was clearly
        getting somewhat fed up with linguists and their incessant wishes to record things.  We talked a bit beforehand in Russian
        about what she could tell, and she told several little anecdotes, some only a few sentences long. We (BP, NA and EPA)
        were the only people in the house, and the recording was done in their kitchen, where we took down the ticking clock
        and switched off the radio, so that it was quiet.
        \qu Transcribed by BP, transcription checked with Elena Nikolaevna Cherkanova, Russian translation by Elena Nikolaevna Cherkanova,
        glossing by BP. Funding by the Volkswagen Foundation (DoBeS grant). Speaker abbreviation = EPA.
        \ref Elena Petrovna Amganova was born in 1952, i.e. she was 56-57 at the time of the recording. She had 8 years of schooling
        and had worked as a milker and then a cleaner. """
        o = ['EPA']
        self.assertEqual(meta_speakers(i), o)

    #
    def test_count(self):
        with open('Sebjan_new.pickle', 'rb') as f:
            corp = pickle.load(f)
        i = Document(corp['Alekseeva_RD_shatun.txt'], 'Alekseeva_RD_shatun.txt').sents[0]
        self.assertEqual(len(i.make_list()), 10)


class SpeakerError(Exception):
    '''raised on pickle-parsing if no speakers found in meta'''
    def __init__(self, message='speaker not found in meta'):
        super(SpeakerError, self).__init__()
        self.message = message
    def __str__(self):
        return repr(self.message)


class Document:

    def __init__(self, doc, fil):
        self.meta = doc['meta']
        self.name = fil
        self.sents = []
        for sent in doc['text']:
            self.sents.append(Sentence(sent, self.name, self.speakers))

    @property
    def speakers(self):
        sp = meta_speakers(self.meta)
        if 'AAS' in sp:
            print(self.name)
        return sp


class Sentence:

    def __init__(self, sent, doc, speakers=None):
        self.sent = sent
        self.doc = doc
        self.doc_speakers = speakers


    @property
    def speaker(self):
        if 'ELANParticipant' in self.sent and len(self.sent['ELANParticipant'])>0:
            possible = self.sent['ELANParticipant'][0]
            if possible in self.doc_speakers:
                return possible
            elif 'mb' in self.sent and ':' not in possible:
                return possible
            elif 'mb' in self.sent:
                return self.doc_speakers[0]
            else:
                return 'none'
        return self.doc_speakers[0]


    def make_list(self):
        needed = ['mb', 'ge', 'ps']
        if all(map(lambda x: x in self.sent, needed)):
            res = []
            for i in range(len(self.sent['mb'])):
                res += [(x, y, self.sent['ps'][i], self.speaker) for x, y in zip(self.sent['mb'][i], self.sent['ge'][i])]
            return res
        return []


def meta_speakers(meta):
    status = ''
    m = re.search('(?:[Ss]peakers?\sabbreviations?\s=\s)(([A-Z]{2,3}[., ]{,2})+)', meta)
    if m:
        speakers = list(map(lambda x: x.strip('., '), m.group(1).split()))
    else:
        speakers = None
        raise SpeakerError('no speakers found in meta')
    return speakers


def handle_corpus(corp):
    all_morphs = []
    for fname in corp:
        doc = Document(corp[fname], fname)
        for sent in doc.sents:
            all_morphs += sent.make_list()
    return all_morphs


def main():
    for corpus in ['Kamchatka', 'Sebjan']:
        with open('{}_new.pickle'.format(corpus), 'rb') as f:
            corp = pickle.load(f)
        corp_morphs = handle_corpus(corp)
        print(set(map(lambda x: x[-1], corp_morphs)))
        # with open('{}_wds_by_mor.pickle'.format(corpus), 'wb') as f:
        #     pickle.load(corp_morphs, f)


if __name__ == '__main__':
    # unittest.main()
    main()
