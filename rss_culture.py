#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
affiche tous les liens rss des podcasts de France Culture
"""

import urllib2, argparse, os


try:
    from bs4 import BeautifulSoup
except:
    print 'Installer python-bs4 (BeautifulSoup)'
    exit (1)
            

url='http://www.franceculture.fr/podcasts/titre'
racine='http://www.franceculture.fr'

#parse command line
parser = argparse.ArgumentParser(description='Récupère les liens RSS de France Culture',
    epilog = "Utiliser une redirection pour enregistrer les données :\n" \
    "rss_culture.py > fichier.txt" ,
    formatter_class = argparse.RawTextHelpFormatter)
parser.add_argument('-f', dest='FORMAT', action='store_true', help = "sortie formatée")
args = parser.parse_args()

#lecture + parse  page des émissions
f = urllib2.urlopen(url)
html_doc = f.read()
f.close()
soup = BeautifulSoup(html_doc, 'html.parser')

#affichage
print "#", unicode(soup.title.text).encode('utf-8'), "\n"

nom, lien  = '', ''


def get_rss(page):
    """
    récupère le lien rss des podcasts
    """
    f = urllib2.urlopen(page)
    emission_doc= f.read()
    f.close()
    soup2 = BeautifulSoup(emission_doc, 'html.parser')

    #récupère le lien de la page rss/xml des podcats
    for l in soup2.find_all('link'):
        if l.get('rel') == [u'alternate']:
            return l.get('href')
    
    return ''
    

for a in soup.find_all('a'):
    page, emission = '', ''

    #récupère la page de l'émission et le titre de l'émission
    if a.has_attr('href') :
        if a.get('href')[:9] == '/podcast/' :
            if a.text != '' :
                page, emission =  racine + a.get('href'), a.text.strip()


    if page !='':
        #récupère le lien des pages rss/xml des podcasts
        lien_rss = get_rss(page)
        if args.FORMAT and lien_rss != '':
            emission = unicode(emission.upper()).encode('utf-8')
            emission = emission.replace('/','-')
            emission = emission.replace('’', '\'')                        
            print "[" + emission + "]"
            print "url =", lien_rss, "\n"
        else:
            print unicode(emission).encode('utf-8') , ';', lien_rss
        

        
