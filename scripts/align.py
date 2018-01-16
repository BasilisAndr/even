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
            ps += 'v'
        elif n_gl&set(g):
            ps += 'n'
        elif adv_gl in g:
            ps += 'adv'
        elif (m[0], g[0]) in postags:
            ps += postags[(m, g)]
        else:
            ps += '?'
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
    parted_layers = ['tx', 'mb', 'ge', 'ps']
    if not (len(line) == 1): # чтобы не считать пустые строки
        if layer in parted_layers:
            line_content = morphs_2_words(line[1:]) # делим на слова, состоящие из морфем
        else:
            line_content = [' '.join(line[1:])] # просто целые строки (комментарии и тп)
            current_layer = layer
        if layer in res and res[layer][0] != '':
            res[layer] += line_content
        else:
            res[layer] = line_content
    return res, current_layer


def lines_2_dict(part, parted_layers=['tx', 'mb', 'ge'], res={}):
    '''
    i: кусок текста (предложение) в несколько строк, в каждой строке несколько слоёв, и с другими данными предложения
    o: джейсонина вида {'слой': [сл, о, ва], 'слой': содержимое}
    доп. ограничения: длина всех строк-массивов равна
    '''
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
        print('Error in {}, here:'.format(fil))
        print(lengths)
        for l in selected_layers:
            print(len(p_sent[l]))
            pprint(p_sent[l])
    return lengths


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


def handle_file(text):
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
        corpus_dict[fil] = handle_file(text)
    with open('{}_new.pickle'.format(corp), 'wb') as f:
        pickle.dump(corpus_dict, f)
    return corpus_dict


def align_mg(morph, gloss):
    for l in range(len(morph)):
        a, b = len(morph[l]), len(gloss[l])
        if a>b:
            gloss[l] = gloss[l] + ' ' * (a-b)
        else:
            morph[l] = morph[l] + ' ' * (b-a)
    return ' '.join(morph), ' '.join(gloss)


def align(sent):
    for i in range(len(sent['ps'])):
        sent['mb'][i], sent['ge'][i] = align_mg(sent['mb'][i], sent['ge'][i])
        maxx = max([len(sent['mb'][i]), len(sent['tx'][i])])
        for layer in ['ps', 'tx', 'mb', 'ge']:
            sent[layer][i] = sent[layer][i] + ' ' * (maxx-len(sent[layer][i]))
    for layer in ['ps', 'tx', 'mb', 'ge']:
        sent[layer] = ' '.join(sent[layer])
    return sent


# def cut_long_lines(sent):


def write_doc(doc, path, order=['id','tx','mb','ps','ge','ft','ELANBegin','ELANEnd','ELANParticipant','ev','ru']):
    for sent in doc:
        sent = align(sent)
    with open(path, 'w') as f:
        for l in order:
            if l in sent:
                f.write('\\{} {}'.format(l, sent[l]))
        rest = set(sent.keys())-set(order)
        for r in rest:
            f.write('\\{} {}'.format(r, sent[r]))


def write_corpus(corpus):
    if not os.path.exists('{}/'.format(corpus)):
        os.mkdir(corpus)
    with open("{}_new.pickle", 'rb') as f:
        corp = pickle.load(f)
    for doc in corp:
        path = os.path.join(corpus, doc)
        write_doc(corp[doc], path)


def main():
    corpora = ['Kamchatka', 'Sebjan']
    for corp in corpora:
        make_readable(corp)
        write_corpus(corp)


if __name__ == '__main__':
    unittest.main()
    main()
