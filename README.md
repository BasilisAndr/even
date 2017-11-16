List of datasets:

## Everything

Sebjan.pickle, Kamchatka.pickle -- словари формата

`{
    doc:{    # in a dict, named
        meta:[meta],    # metainfo at the head
        text:[
            {        # sentence (in a list, numbered)
                layer:[
                    morphs    # for mb, ge, ps
                    ],
                layer:''    # e.g. translation
            }
        ]
    }
}`

49800 S
33112 K

## Converbs

converbs.pickle -- таблица с конвербами + логлайк


## Morphemes

### Raw

Sebjan_morphemes.pickle, Kamchatka_morphemes.pickle -- raw succession of words like this

` ('ROOT', 'ROOT', 'ROOT'),    # root
 ('-B', '-med', 'v'),
 ('-DEŋ', '-pst.ptc', 'v'),
 ('-E', '-ep', 'v')
 ('END', 'END', 'END')]     # end of the word`

### Single morphemes
 
Sebjan_morphemes_only.pickle, Kamchatka_morphemes_only.pickle -- pd of morphemes with counts only

morpheme_counts.pickle -- pd of morphemes with counts only by two corp together

total_morphemes.pickle -- таблица с морфемами + логлайк

total_morphemes_grouped.pickle -- same but grouped

 
 ### Pairs
 
 Sebjan_pairs_dict.pickle, Kamchatka_pairs_dict.pickle -- dicts of (morph): {morph_after: N}
 
 pairs.pickle -- pd with pairs and count only
 
 pairs_by_ll.pickle -- pd with pairs and all the stats
 

