"""
Atelier text mining du 02/06/2016

essentiels Partie 3: freq des groupes extraits => matrice => clustering

(c) R. Loth ISCPIF-CNRS (UPS 3611)
"""

from re   import sub
from json import load
from glob import glob
import numpy as np


term_ref = open("work/dict.json")

term_infos = load(term_ref)

term_ref.close()

# critère de filtrage ??

mini_term_infos = {}
for term in term_infos
    

# récupération des infos "colonnes" *.idx
doc_paths = glob("work/corpus/02-indexed/*")

index = {}

doc_names = []

for doc_path in doc_paths[0:30]:
    # ex: "1992-carbon_isotope_compo-A8E6B4D"
    doc_name = sub(r'(.*/)|(\.idx)','',doc_path)

    # occurrences par doc
    with open(doc_path, 'r') as fic:
        index[doc_name] = {}
        for line in fic.readlines():
            (term, occs) = line.rstrip().split('\t')

            if term in term_infos:
                index[doc_name][term] = int(occs)



# index => matrice

m = []

term_list = sorted([key for key in term_infos.keys()])
doc_list = sorted([key for key in index.keys()])


for doc in doc_list:
    col = []
    for term in term_list:
        if term in index[doc]:
            col.append(index[doc][term])
        else:
            col.append(0)
    m.append(col)

# for term in term_list:
#     v = [term,]
#     for doc in doc_list:
#         if term in index[doc]:
#             v.append(index[doc][term])
#         else:
#             v.append(0)
#     # vecteur du terme
#     m.append(v)

matrice = np.array(m)

# print(m)

print(matrice.shape)

from sklearn.cluster import KMeans

solution = KMeans(n_clusters=5).fit_predict(matrice)


# array([0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#       0, 0, 0, 0, 0, 0, 0], dtype=int32)

# prediction pour la liste des termes
