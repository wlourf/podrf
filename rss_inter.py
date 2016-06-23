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
print "#", soup.title.text.encode('utf-8'), "\n"

nom, lien  = '', ''

# récupère le lien des pages rss/xml des podcasts

for article in soup.find_all('article'):
    if article.get('class') == [u'rich-section-list-item']:
        for a in article.find_all('a'):
            if a.get('class') == [u'rich-section-list-item-content-title'] :
                nom = a.text.strip() # titre de l'émission
            if a.get('href')[:38] == 'http://radiofrance-podcast.net/podcast' :
                lien =  a.get('href') 
            
    if nom != ""  :
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

        
