"""
Atelier text mining du 02/06/2016

essentiels Partie 2: traitement texte eng => groupes nominaux

(c) R. Loth ISCPIF-CNRS (UPS 3611)
"""

from re   import sub,search
from glob import glob
from nltk import sent_tokenize
from nltk import word_tokenize
# from nltk import pos_tag
from nltk.tag.perceptron    import PerceptronTagger
from nltk import RegexpParser

from json import load, dump

from datetime import datetime

tagr = PerceptronTagger()


doc_metas = {}
with open('work/meta/test.json') as metas:
    doc_metas = load(metas)

doc_paths = glob("work/corpus/01-originaux/*")

# total par terme
term_totals = {}

# nombre de docs ayant le terme par terme
term_ndocs = {}

# nombre de tokens dans le terme
term_ntoks = {}


# timers
timer_read = 0
timer_sents = 0
timer_pos = 0
timer_match = 0
timer_loop = 0
timer_write = 0

# ex: "work/corpus/01-originaux/1992-carbon_isotope_compo-A8E6B4D.txt"
for (i, doc_path) in enumerate(doc_paths):

    # décomptes par termes par doc
    index = {}

    # ex: "1992-carbon_isotope_compo-A8E6B4D"
    doc_name = sub(r'(.*/)|(\.txt)','',doc_path)
    print(doc_name, i)

    if doc_metas[doc_name]['lang'] != "eng":
        continue

    t0 = datetime.now()
    # lecture/analyse LIGNES
    textlines = []
    with open(doc_path, 'r') as fic:
        textlines = fic.read().split('\n')
    # fic.close()


    t1 = datetime.now()


    # # lecture/analyse PHRASES
    sents = []
    for textli in textlines:
        sents += sent_tokenize(textli)
    del textlines

    t2 = datetime.now()
    # # lecture/analyse MOTS + CATS
    pos_sents=[]
    for s in sents:
        tok_sent = []
        wtoks = word_tokenize(s)

        # A
        pos_sents.append(tagr.tag(wtoks))

        # B
        # for w in wtoks:
        #     tok_sent += pos_tag(w)
        # pos_sents.append(tok_sent)

    del sents

    t3 = datetime.now()

    # pos_sents=
    # [[('In', 'IN'),
    #   ('the', 'DT'),
    #   ('land', 'NN'),
    #   ('of', 'IN'),
    #   ('submarines', 'NNS'),
    #   ('.', '.')],
    #    .... ]

    matcheur = RegexpParser(
    """
    truc:
            {<JJ.*>*<NN.*>+(<P|IN> <JJ.*>*<NN.*>+)*}
    """
    )

    # # lecture/analyse expressions correspondant à notre recherche
    recog_trees = []
    for s in pos_sents:
        reconnu = matcheur.parse(s)
        recog_trees.append(reconnu)
    del pos_sents

    t4 = datetime.now()
    # [('We', 'PRP'), ('all', 'DT'), ('live', 'VBP'), ('in', 'IN'), ('a', 'DT'), ('yellow', 'JJ'), ('submarine', 'NN'), ('.', '.')]
    # (S
    #   We/PRP
    #   all/DT
    #   live/VBP
    #   in/IN
    #   a/DT
    #   (truc yellow/JJ submarine/NN)
    #   ./.)


    # filtrage,
    # retour à une unité str
    # comme clé dans le décompte
    term_count = {}
    for s in recog_trees:
        for subtree in s.subtrees():
            if len(subtree) < 8 and subtree.label() == "truc":
                # ex: [('opportunistic', 'JJ'), ('species', 'NNS')]
                term_pos_seq = subtree.leaves()

                # ici stemming et nettoyage -------------------
                term_seq = [couple[0] for couple in term_pos_seq]

                # unité str
                term_str = ' '.join(term_seq)

                if len(term_str) < 5:
                    continue

                # !!
                if search(r'[^a-z -]', term_str):
                    continue

                # ----------------------------------------------

                # add to doc counts
                if term_str in index:
                    #============================
                    index[term_str] +=1
                    #============================

                    # fyi -+
                    term_totals[term_str] +=1
                    # -----+
                else:
                    #=============================
                    index[term_str] = 1
                    #=============================

                    # fyi -+
                    if term_str in term_totals:
                        term_totals[term_str] += 1
                        term_ndocs[term_str] += 1
                    else:
                        term_totals[term_str] = 1
                        term_ndocs[term_str] = 1
                        term_ntoks[term_str] = len(term_pos_seq)
                    # -----+
    del recog_trees

    t5 = datetime.now()

    # write indexed doc
    out_doc = open("work/corpus/02-indexed/%s.idx" % doc_name, 'w')
    for term,count in index.items():
        print("%s\t%i" % (term, count), file=out_doc)
    out_doc.close()


    t6 = datetime.now()

    timer_read += (t1-t0).total_seconds()
    timer_sents += (t2-t1).total_seconds()
    timer_pos += (t3-t2).total_seconds()
    timer_match += (t4-t3).total_seconds()
    timer_loop += (t5-t4).total_seconds()
    timer_write += (t6-t5).total_seconds()

    # can signal top terms at end of doc

print("timer_read:",timer_read)
print("timer_pos:",timer_pos)
print("timer_match:",timer_match)
print("timer_loop:",timer_loop)
print("timer_write:",timer_write)


# write dictionnary + term stats
out_dic_csv = open("work/dict.tsv", 'w')

for term, tot in term_totals.items():
    nd = term_ndocs[term]
    size = term_ntoks[term]

    # filtre
    if tot > 3:
        print("%s\t%i\t%i\t%i" % (term, tot, nd, size), file=out_dic_csv)

out_dic_csv.close()


term_meta = {}
# idem json
for term, tot in term_totals.items():
    nd = term_ndocs[term]
    size = term_ntoks[term]
    if tot > 3:
        term_meta[term] = {'f':tot, 'nd':nd, 'size':size}

json_fic = open("work/dict.json", "w")
dump(term_meta, json_fic, indent=2, sort_keys=True)
json_fic.close()
