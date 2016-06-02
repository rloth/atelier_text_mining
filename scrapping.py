"""
Atelier text mining du 02/06/2016

essentiels Partie 1: récupération des données

mkdir -p work/data/01-originaux
mkdir -p work/meta

(c 2016) R. Loth ISCPIF-CNRS (UPS 3611)
"""
from requests import get
from lxml     import etree
from re       import sub
from json     import dump

# listons les éléments XML qui nous intéressent
rubriques_xpaths = {
    # exemples contenus texte
    'abstract': "/m:mods/m:abstract",
    'title'   : "/m:mods/m:titleInfo/m:title",

    # exemples métadonnées
    'year' : "/m:mods/m:relatedItem/m:part/m:date",
    'vol'  : "/m:mods/m:relatedItem/m:part/m:detail[@type='volume']/m:number",
    'lang' : "/m:mods/m:language/m:languageTerm[@authority='iso639-2b']"
}


url = "https://api.istex.fr/document/?q=host.title:oecologia"

my_web_response = get(url)

n_docs = int(my_web_response.json()['total'])

def loop_results(base_url, n_hits):
    all_hits = []
    # requête toute simple sans pagination
    if n_hits <= 5000:
        my_resp = get(base_url + '&size=%i' % n_hits)
        all_hits = my_resp.json()['hits']

    # requête en plusieurs fois: pagination
    else:
        print("Collecting result hits... ")
        for k in range(0, n_hits, 5000):
            print("==>", k)
            my_url = base_url + '&size=5000' + "&from=%i" % k
            my_resp = get(my_url)
            all_hits += my_resp.json()['hits']
    return all_hits

hits = loop_results(url, 500)


my_ns = {"m":"http://www.loc.gov/mods/v3"}

def scrap_contents(xml_url, xpaths_todo, ns = {}):
    # par exemple get("https://api.istex.fr/document/4D...6/metadata/mods")
    xml_response = get(xml_url)

    # parsons le xml
    xml_tree = etree.fromstring(bytes(xml_response.text, 'utf-8'))

    # a remplir
    contents = {}

    # par ex: "title"
    for rubrique in xpaths_todo:

        # par ex: "/mods/titleInfo/title"
        le_xpath = xpaths_todo[rubrique]

        # une requête xpath
        # "find" => on obtient un bout de xml
        xml_elements = xml_tree.xpath(
                                        le_xpath,
                                        namespaces=ns)

        contents[rubrique] = xml_elements[0].text

    return contents


doc_metadata = {}
for hit in hits:
    id = hit['id']
    url_du_xml = 'https://api.istex.fr/document/'+str(id)+'/metadata/mods'

    # debug
    print(url_du_xml)

    doc_contents = scrap_contents(url_du_xml, rubriques_xpaths, my_ns)

    # ex: 1984-osmotic_potential_an-D9B3F50
    my_id = (
        doc_contents['year'][0:4]
        +'-'+
        sub(r'[^a-z]+',"_", doc_contents['title'].lower())[0:20]
        +'-'+
        id[0:7]
        )

    out_text = open("work/data/01-originaux/%s.txt" % my_id, "w")
    print(doc_contents["title"], file=out_text)
    print(doc_contents["abstract"], file=out_text)
    out_text.close()

    doc_metadata[my_id] = {}
    doc_metadata[my_id]['title'] = doc_contents['title']
    doc_metadata[my_id]['year']  = doc_contents['year']
    doc_metadata[my_id]['vol']   = doc_contents['vol']
    doc_metadata[my_id]['lang']  = doc_contents['lang']

meta_fic = open("work/meta/test.json", "w")
dump(doc_metadata, meta_fic, indent=2, sort_keys=True)
meta_fic.close()
