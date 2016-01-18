#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
affiche tous les liens rss des podcasts de FIP
"""

import urllib2, argparse

try:
    from bs4 import BeautifulSoup
except:
    print 'Installer python-bs4 (BeautifulSoup)'
    exit (1)

url = 'http://www.fipradio.fr/emissions'

#parse command line
parser = argparse.ArgumentParser(description='Récupère les liens RSS de FIP', 
    epilog = "Utiliser une redirection pour enregistrer les données :\n" \
    "rss_fip.py > fichier.txt",
    formatter_class = argparse.RawTextHelpFormatter)
parser.add_argument('-f', dest='FORMAT', action='store_true', help = "sortie formatée")
args = parser.parse_args()

#lecture + parse  page des podcats
f = urllib2.urlopen(url)
html_doc = f.read()
f.close()
soup = BeautifulSoup(html_doc, 'html.parser')

#affichage
print "#", unicode(soup.title.text).encode('utf-8'), "\n"

noms, liens= [], []

for h in soup.find_all('h1'):
    if h.get('class') == [u'title']:
        noms.append(h.text)

for a in soup.find_all('a'):
    if a.text == 'podcaster via rss':
        liens.append(a.get('href'))

for idx in range(len(noms)):
    nom, lien = noms[idx], liens[idx]
#    print  unicode(nom).encode('utf-8') , ";", lien
 
    if nom != '':
        if args.FORMAT :
            if lien != '':
                emission = unicode(nom.upper()).encode('utf-8')
                emission = emission.replace('/', '-')
                emission = emission.replace('’', '\'')
                print "[" + emission + "]"
                print "url =" , lien, "\n"
        else:
            print  unicode(nom).encode('utf-8') , ";", lien
        nom, lien  = '', ''

    print         
