#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
affiche tous les liens rss des podcasts de France Culture
"""

import urllib2, argparse

try:
    from bs4 import BeautifulSoup
except:
    print 'Installer python-bs4 (BeautifulSoup)'
    exit (1)

url='http://www.franceculture.fr/emissions'


def parse_command_line():

    #parse command line
    parser = argparse.ArgumentParser(description='Récupère les liens RSS' \
        ' de France Culture', 
        epilog = "Utiliser une redirection pour enregistrer les données :\n" \
        "rss_culture.py > fichier.txt",
        formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('-f', dest='FORMAT', action='store_true', 
                        help = "sortie formatée")
    args = parser.parse_args()
    return args



def get_urls(format=False, filter=""):

    nom, lien  = '', ''
    display = filter.strip() == ""
    filters = []


    #lecture + parse  page des podcats
    f = urllib2.urlopen(url)
    html_doc = f.read()
    f.close()
    soup = BeautifulSoup(html_doc, 'html.parser')

    #affichage
    if display :
        print "#", soup.title.text.encode('utf-8'), "\n"

    for div in soup.find_all('div'):
        if div.get('class') == [u'bloc-concept',u'concept']:
            #print (div.encode('utf8'))
            for h2 in div.find_all('h2'):
                if h2.get('class') ==  [u'title', u'name'] :
                    nom = h2.text.strip()

            for a in div.find_all('a'):
                if a.get('class') == [u'podcast'] :
                    lien =  a.get('href')

        if nom != '':
            if display :
                if format :
                    if lien != '':
                        emission = unicode(nom.upper()).encode('utf-8')
                        emission = emission.replace('/', '-')
                        emission = emission.replace('’', '\'')
                        print "[" + emission + "]"
                        print "url =" , lien, "\n"
                else:
                    print  unicode(nom).encode('utf-8') , ";", lien

            if filter.strip() != "" and nom.lower().find(filter.lower()) > -1:
                filters.append([nom, lien])

            nom, lien  = '', ''

    return filters
        
if __name__ == "__main__":
    args = parse_command_line()
    get_urls(format = args.FORMAT)
