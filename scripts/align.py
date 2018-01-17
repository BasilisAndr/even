import unittest
import re
import pickle
from pprint import pprint
import os

class TestAll(unittest.TestCase):

    def test_align(self):
        self.maxDiff = None
        m_i = ['nulge', '-D', '-E', '-L', '-RI', '-WUn', '-E', '=sI']
        g_i = ['migrate', '-prog', '-ep', '-inch', '-pst', '-poss.1pl.ex', '-ep', '=emph']
        m_o = "nulge   -D    -E  -L    -RI  -WUn         -E  =sI  "
        g_o = "migrate -prog -ep -inch -pst -poss.1pl.ex -ep =emph"
        m2_i = ['ọkaːt', '-DUk(U)', '=kE']
        g2_i = ['river', '-abl', '=emph']
        m2_o = "ọkaːt -DUk(U) =kE  "
        g2_o = "river -abl    =emph"
        i = {'mb': [['umekič', '=eː'], ['nulge', '-D', '-E', '-L', '-RI', '-WUn', '-E', '=sI'], ['ọkaːt', '-DUk(U)', '=kE']],
             'ge': [['very', '=emph'], ['migrate', '-prog', '-ep', '-inch', '-pst', '-poss.1pl.ex', '-ep', '=emph'], ['river', '-abl', '=emph']],
             'tx': ['Umekičeː', 'nulgedʒilliwunesi', 'ọkaːttụkke'],
             'ps': ['adv', 'v', 'n']}
        o = {'tx': "Umekičeː     nulgedʒilliwunesi                                   ọkaːttụkke         ",
             'mb': "umekič =eː   nulge   -D    -E  -L    -RI  -WUn         -E  =sI   ọkaːt -DUk(U) =kE  ",
             'ps': "adv          v                                                   n                  ",
             'ge': "very   =emph migrate -prog -ep -inch -pst -poss.1pl.ex -ep =emph river -abl    =emph"}
        self.assertEqual(align_mg(m2_i, g2_i), (m2_o, g2_o))
        self.assertEqual(align_mg(m_i, g_i), (m_o, g_o))
        self.assertDictEqual(align(i), o)

    def test_morph(self):
        i = 'omen -REkEn    tolin   =eː   ịrkụn -E  -D    -(R)U   ewiː -D    -(R)U   umekič'.split()
        o = [['omen', '-REkEn'], ['tolin', '=eː'], ['ịrkụn', '-E', '-D', '-(R)U'],
             ['ewiː', '-D', '-(R)U'], ['umekič']]
        self.assertEqual(morphs_2_words(i), o)

    # def test_speaker(self):
    #     i = """"""
    #     o = """"""
    #     self.assertEqual(define_speaker(i), o)

    def test_exracted_wds(self):
        dic = extract_pos()
        self.assertTrue(('ịbgọ', 'good') in dic)
        self.assertTrue(('bụg', 'place') in dic)
        self.assertTrue(('bụg', 'earth') in dic)
        self.assertTrue(dic[('bütünnüː', 'entirely.Y')]=='adv')
        self.assertTrue(('čas', 'hour.R') in dic)
        self.assertTrue(('ńaːn', 'again') in dic)


class LengthError(Exception):
    '''raised on pickle-parsing if morpheme/gloss/pos lists
    are not the same length'''
    def __init__(self, message='Length of lists not equal'):
        super(LengthError, self).__init__()
        self.message = message
    def __str__(self):
        return repr(self.message)


def extract_pos():
    with open('dicts/Dictionary_full.txt') as f:
        text = f.read()
    items = text.split('\n\n')
    postags = {}
    for item in items:
        m = re.search('\\\lx ([\w0-9ː\-=().]+)', item)
        gs = re.findall('\\\ge ([\w.]+)', item)
        p = re.search('\\\ps ([\w0-9.]+)', item)
        if m and p:
            for g in gs:
                postags[(m.group(1), g)] = p.group(1)
    with open('postags.pickle', 'wb') as f:
        pickle.dump(postags, f)
    return postags


def morphs_2_words(line):
    '''берёт на вход массив расчленённой строки, возвращает массив слов'''
    word, words = [], []
    for morph in line:
        if morph.strip()[0] in '=-':
            word.append(morph)
        else:
            if len(word) > 0:
                words.append(word)
            word = [morph]
    words.append(word)
    return words


def postag(mor, gl, postags):
    v_gl = set('-vr -pol.imp -pst -nonfut -impf.ptc -ipf.ptc -pst.ptc -pf.ptc \
            -fut.ptc -nec.ptc -hyp.ptc -ant.cvb -purp.cvb -trm.cvb -cond.cvb \
            -imm.cvb -sim.cvb -neg.cvb -dur.cvb -nmdl.cvb -impf.cvb -mult.cvb'.split())
    n_gl = set('-nr -agnr -acc -acc.3sg -des -dat -ins -com -loc -prop -prol -all.prol \
            -abl -elat -prfl.sg -aln -pred.poss -com'.split())
    adv_gl = '-coll'
    ps = []
    for m, g in zip(mor, gl):
        if v_gl&set(g):
            ps.append('v')
        elif n_gl&set(g):
            ps.append('n')
        elif adv_gl in g:
            ps.append('adv')
        elif (m[0], g[0]) in postags:
            ps.append(postags[(m[0], g[0])])
        else:
            ps.append('?')
    return ps


def add_postags(sent):
    '''adds pos layer if necessary'''
    if 'mb' in sent and 'ge' in sent:
        with open('postags.pickle', 'rb') as f:
            postags = pickle.load(f)
        sent['ps'] = postag(sent['mb'], sent['ge'], postags)
    return sent


def handle_startline(line, res, current_layer):
    '''обрабатывает первую строку нового слоя в предложении'''
    line = line.split()
    layer = line[0].strip('\\')
    parted_layers = ['mb', 'ge', 'ps']
    if not (len(line) == 1): # чтобы не считать пустые строки
        if layer in parted_layers:
            line_content = morphs_2_words(line[1:]) # делим на слова, состоящие из морфем
        elif layer == 'tx':
            line_content = line[1:]
        else:
            line_content = [' '.join(line[1:])] # просто целые строки (комментарии и тп)
            current_layer = layer
        if layer in res and res[layer][0] != '':
            res[layer] += line_content
        else:
            res[layer] = line_content
    return res, current_layer


def lines_2_dict(part):
    '''
    i: кусок текста (предложение) в несколько строк, в каждой строке несколько слоёв, и с другими данными предложения
    o: джейсонина вида {'слой': [сл, о, ва], 'слой': содержимое}
    доп. ограничения: длина всех строк-массивов равна
    '''
    res={}
    lines = [line for line in part.split('\n') if len(line) > 1]
    res['index'] = [lines[0].split('_')[-1]]
    current_layer = '' # для переносов
    for line in lines[1:]:
        if line.startswith('\\'):
            res, current_layer = handle_startline(line, res, current_layer)
        elif current_layer:
            res[current_layer][0] += ' ' + line
    res = add_postags(res)
    return res


def check_len(p_sent, fil):
    '''check that the number of words is the same'''
    parted_layers = ['mb', 'ge', 'ps']
    selected_layers = [key for key in p_sent if key in parted_layers and len(p_sent[key])>1]
    lengths = set([len(p_sent[key]) for key in selected_layers])
    if len(lengths) > 1:
        for l in selected_layers:
            print(len(p_sent[l]))
            pprint(p_sent[l])
        raise LengthError(message=fil)


def check_align(p_sent, fil):
    '''check that morphemes are aligned'''
    parted_layers = ['mb', 'ge', 'ps']
    selected_layers = [key for key in p_sent if key in parted_layers and len(p_sent[key])>1]
    if 'mb' in selected_layers and 'ge' in selected_layers:
        for i in range(len(p_sent['ge'])):
            if len(p_sent['ge'][i]) != len(p_sent['mb'][i]):
                print('што-то слиплось в {}'.format(fil))
                pprint(p_sent)


def handle_sent(sent, fil):
    '''обрабатывает каждое предложение исходного текста
    i: отрывок текста
    o: джейсонина по словам'''
    sent_content = lines_2_dict(sent)
    check_len(sent_content, fil)
    check_align(sent_content, fil)
    return sent_content


def handle_file(text, fil):
    '''берёт текст файла, возвращает джейсонину'''
    file_content, text_content = {}, []
    sents = text.split('\id')
    file_content['meta'] = sents[1] # metainfo at the beginning of the file; not parsed
    for sent in sents[2:]:
        text_content.append(handle_sent(sent, fil))
    file_content['text'] = text_content
    return file_content


def define_speaker(sent):
    '''возвращает спикера предложения'''
    if 'ELANParticipant' in sent:
        speaker = sent['ELANParticipant'][0]
    else:
        try:
            speaker = re.search('Speaker\sabbreviation = (...)', content[doc]['meta']).group(1).strip(',.?')
        except:
            speaker = 'none'
    if len(speaker) == 0 or ':' in speaker:
        speaker = 'none'
    return speaker


def make_readable(corp):
    '''переводит текст корпусов в удобомашиночитаемую джейсонину'''
    folder = 'Corpus_Text_{}_postagged'.format(corp)
    corpus_dict = {}
    for fil in os.listdir(folder):
        if not fil.endswith('.txt'):
            continue
        with open(os.path.join(folder, fil), 'r') as f:
            text = f.read()
        corpus_dict[fil] = handle_file(text, fil)
    with open('{}_new.pickle'.format(corp), 'wb') as f:
        pickle.dump(corpus_dict, f)
    return corpus_dict


def align_mg(morph, gloss):
    for l in range(len(morph)):
        try:
            a, b = len(morph[l]), len(gloss[l])
        except:
            pprint(morph)
            pprint(gloss)
            raise LengthError()
        if a>b:
            gloss[l] = gloss[l] + ' ' * (a-b)
        else:
            morph[l] = morph[l] + ' ' * (b-a)
    return ' '.join(morph), ' '.join(gloss)


def align(sent):
    for i in range(len(sent['ps'])):
        sent['mb'][i], sent['ge'][i] = align_mg(sent['mb'][i], sent['ge'][i])
        try:
            maxx = max([len(sent['mb'][i]), len(sent['tx'][i])])
        except:
            print(i)
            pprint(sent)
            raise LengthError()
        for layer in ['ps', 'tx', 'mb', 'ge']:
            try:
                sent[layer][i] = sent[layer][i] + ' ' * (maxx-len(sent[layer][i]))
            except:
                pprint(sent[layer])
                print(sent['mb'])
                print(sent['ge'])
                print(sent['tx'])
                raise LengthError()
    for layer in ['ps', 'tx', 'mb', 'ge']:
        sent[layer] = ' '.join(sent[layer])
    return sent


def handle_sent_tw(sent, path):
    sent = add_postags(sent)
    error = check_len(sent, path)
    if error:
        print(sent)
    sent = align(sent)
    return sent


def write_doc(text, path, parted_layers = ['tx', 'mb', 'ps', 'ge']):
    print(path)
    sentline = {}
    with open(path, 'w') as f:
        for line in text:
            if line[1:3] in parted_layers:
                if len(line)>4:
                    if line[1:3] == 'tx':
                        sentline[line[1:3]] = line[4:].split()
                    else:
                        sentline[line[1:3]] = morphs_2_words(line[4:].split())
                else:
                    f.write(line)
            else:
                if sentline:
                    if set(sentline.keys())==set(parted_layers):
                        sentline = handle_sent_tw(sentline, path)
                    for l in parted_layers:
                        if l in sentline:
                            if isinstance(sentline[l], list):
                                if isinstance(sentline[l][0], list):
                                    pprint(sentline)
                                    raise LengthError()
                                f.write("\\{} {}\n".format(l, ' '.join(sentline[l])))
                            else:
                                f.write("\\{} {}\n".format(l, sentline[l]))
                    sentline = {}
                f.write(line)


def write_corpus(corpus):
    folder = 'Corpus_Text_{}_postagged'.format(corpus)
    if not os.path.exists('{}/'.format(corpus)):
        os.mkdir(corpus)
    for fil in os.listdir(folder):
        if not fil.endswith('.txt'):
            continue
        path_from = os.path.join('Corpus_Text_{}_postagged'.format(corpus), fil)
        path_to = os.path.join(corpus, fil)
        with open(path_from) as f:
            text = f.readlines()
        if os.path.exists(path_to):
            with open(path_to) as f:
                text2 = f.readlines()
            if len(text) != len(text2):
                # continue
                print(path_from)
                print(len(text), len(text2))
        # write_doc(text, path_to)
    # raise LengthError()


def main():
    corpora = ['Sebjan']
    for corp in corpora:
        print('handling {}...'.format(corp))
        # make_readable(corp)
        print('pickle done, writing...')
        write_corpus(corp)
        print('{} done'.format(corp))
    print('all done')


if __name__ == '__main__':
    # unittest.main()
    main()
