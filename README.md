List of datasets:

## Everything

jsons/Sebjan.json, jsons/Kamchatka.json -- словари формата

```
{
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
}
```

- 49800 S
- 33112 K



## Morphemes

### Raw

jsons/Sebjan_morphemes.json, jsons/Kamchatka_morphemes.json -- raw succession of words like this

```
[('ROOT', 'ROOT', 'ROOT'),    # root
 ('-B', '-med', 'v'),
 ('-DEŋ', '-pst.ptc', 'v'),
 ('-E', '-ep', 'v')
 ('END', 'END', 'END')]     # end of the word
 ```
