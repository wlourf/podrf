#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
affiche tous les liens rss des podcasts de France Inter 
"""

import urllib2, argparse

try:
    from bs4 import BeautifulSoup
except:
    print 'Installer python-bs4 (BeautifulSoup)'
    exit (1)

url='http://www.franceinter.fr/podcasts'

#parse command line
parser = argparse.ArgumentParser(description='Récupère les liens RSS de France Inter', 
    epilog = "Utiliser une redirection pour enregistrer les données :\n" \
    "rss_inter.py > fichier.txt",
    formatter_class = argparse.RawTextHelpFormatter)
parser.add_argument('-f', dest='FORMAT', action='store_true', help = "sortie formatée")
args = parser.parse_args()

#lecture + parse  page des podcats
f = urllib2.urlopen(url)
html_doc = f.read()
f.close()
soup = BeautifulSoup(html_doc, 'html.parser')

#affichage
print "#", soup.title.text, "\n"

nom, lien  = '', ''

for a in soup.find_all('a'):

    #récupère le lien des pages rss/xml des podcasts
    if a.get('class') == [u'podrss'] :
        lien = a.get('href')
       
    #récupère le titre de l'émission
    if a.get('href')[:10] == '/emission-' :
        if a.text != u'' and a.get('class') != [u'visuel']:
            nom = a.text.strip()
            
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

        
