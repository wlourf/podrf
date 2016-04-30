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

def parse_command_line():
    #parse command line
    parser = argparse.ArgumentParser(description='Récupère les liens RSS de FIP', 
        epilog = "Utiliser une redirection pour enregistrer les données :\n" \
        "rss_fip.py > fichier.txt",
        formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('-f', dest='FORMAT', action='store_true', help = "sortie formatée")
    return parser.parse_args()

def get_urls(format = False, display=True):
    #lecture + parse  page des podcats
    f = urllib2.urlopen(url)
    html_doc = f.read()
    f.close()
    soup = BeautifulSoup(html_doc, 'html.parser')

    #affichage
    if display :
        print "#", unicode(soup.title.text).encode('utf-8'), "\n"

    noms, liens= [], []
    listing = []

    for h in soup.find_all('h1'):
        if h.get('class') == [u'title']:
            noms.append(h.text)

    for a in soup.find_all('a'):
        if a.text == 'podcaster via rss':
            liens.append(a.get('href'))

    for idx in range(len(noms)):
        if idx < len(liens): #si dernières émissions sans liens

            nom, lien = noms[idx], liens[idx]

            if nom != '':
                if format :
                    if lien != '':
                        emission = unicode(nom.upper()).encode('utf-8')
                        emission = emission.replace('/', '-')
                        emission = emission.replace('’', '\'')
                        if display :
                            print "[" + emission + "]"
                            print "url =" , lien, "\n"
                else:
                    if display:
                        print  unicode(nom).encode('utf-8') , ";", lien
                listing.append([nom,lien])
                nom, lien  = '', ''

    if display:
        print
    else:
        return listing


if __name__ == "__main__":
    args = parse_command_line()
    get_urls(format = args.FORMAT)
else:
    print ('not main')
