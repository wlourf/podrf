#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
Télécharge, renomme, convertit, tague les podcasts issus de 
France Inter ou France Culture
Necessite les paquets 
avconc pour les conversions
et 
python-eyed3 pour le taggage

"""
#emission  = nom de l'émission, quelque soit la date
#podcast   = émission pour un jour donné

import os, ConfigParser,argparse, urllib2, time, csv
import xml.etree.ElementTree as ET
import shutil, subprocess

try:
    import eyeD3
except:
    print 'Installer python-eyed3'
    exit(1)
    



PROG    = "podrf"
VERSION = "0.1"
DESCRIPTION = "Télécharge, renomme, convertit, tague les podcasts issus de pages *.xml,\n" \
              "utiliser les scripts rss_inter.py et rss_culture.py pour récupérer les\n" \
              "pages xml de France Inter et France Culture."




def process_command_line():
    """
    récupère les paramètres passés au programme
    vérifie si chaque émission à une url
    """
    parser = argparse.ArgumentParser(prog=PROG, description = DESCRIPTION,  
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('FILE_CONFIG', type = str , help='fichier de configaration, défaut = ~/.podcasts.cfg' , 
        nargs='?', default =  os.path.join(os.getenv("HOME"), ".podcasts.cfg") )
    parser.add_argument('-n', dest = "NOMBRE", type = int , 
        help='nombres de podcasts à charger pour chaque émission'   )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)

    args = parser.parse_args()
    args.NOMBRE    = args.NOMBRE or None
    return args




def parse_config_file(config_file):
    """
    vérifie présence et validité du fichier de config
    necessité d'une section ['paramètres']
    """
    if not os.path.isfile(config_file):
        print 'Erreur fichier de configuration :', config_file
        exit (1)
    dict = {}
    config = ConfigParser.RawConfigParser(dict)
    config.read(config_file)
    arrSections = config.sections()

    if not 'paramètres' in arrSections:
        print 'Section \'paramètres\' manquante dans ', config_file
        exit(1)

    arrSections.remove('paramètres')

    params = {}
    if config.has_option('paramètres', 'dossier'):
        params['save_dir']  = config.get('paramètres', 'dossier')
    else:
        print 'Paramètre \'dossier\' non défini.'
        exit (1)
        
    if config.has_option('paramètres', 'catalogue'):
        params['catalogue'] = config.get('paramètres', 'catalogue')
    else:
        print 'Paramètre \'catalogue\' non défini.'
        exit (1)


    #vérifie si chaque émission à une url
    #et met chaque émission dans un dictionnaire
    arrEmissions =[]
    for s in arrSections:
        if not config.has_option(s, 'url') : #.lower() not in config[s] :
            print "Manque url sur émission " , s
            exit(1)
        arrEmissions.append({'nom' :s})    
        for v in [ "url", "bitrate", "channels", "artist", "album", "genre"]:
            if config.has_option(s, v):
                arrEmissions[len(arrEmissions)-1][v] = config.get(s,v)
                
    return  params, arrEmissions



def check_params(params):
    """
    vérifie présence dossiers enreg et catalogue
    et retourne le catalogue dans un tableau
    """
    if not os.path.isdir( params['save_dir']):
        try:
            os.makedirs( params['save_dir'])
            print 'Création du dossier ', params['save_dir']
        except:
            print 'Impossible de créer le dossier ' + params['save_dir']
            exit (1)

    if not os.path.isfile( params['catalogue'] ):
        print 'Le fichier %s sera créé' % params['catalogue'] 
        arrCatalogue = []
    else :
        f = open(params['catalogue'])
        reader = csv.reader(f, delimiter=";")
        arrCatalogue = list(reader)
        f.close()

    return arrCatalogue





def lecture_rss(emission, arrCatalogue, nombre):
    """
    lit le flux rss de l'émission et retourne les infos
    dans un tableau
    """
    code, url = emission['nom'], emission['url'] 
    rss = urllib2.urlopen(url)
    print "-" * 30
    print "\n%s : %s \n" % (code , url )
    
    tree = ET.parse(rss)
    root = tree.getroot()
    idx = 1
    
    arrPodcasts = []
    
    index = 1
    #création catalogue avec dl True or False
    for item in root.findall('./channel/item'): #pas de dernier /
        podcast = {  \
              'title'  : unicode(item.find('title').text).encode('utf-8').strip() , \
              'date'   : item.find('pubDate').text ,  \
              'guid'   : item.find('guid').text , \
              'length' : item.find('enclosure').get('length')
              }
              
        #converions date au format AAAAMMJJ
        #descr['date'][:-6] remove offset UTC, %z fonctionne pas avec strptime
        outDate = time.strptime(podcast['date'][:-6], "%a, %d %b %Y %H:%M:%S")
        outDate = time.strftime( "%Y%m%d", outDate)
        podcast['year'] = time.strftime( "%Y")
        podcast['date'] = outDate
        
        arrPodcasts.append(podcast)

        racine  = code + '-' + podcast['date']

        #vérifie si fichier déjà téléchargé (enregistré dnas catalogue, avec la bonne taille)
        #arrCatalogueReverse = arrCatalogue.reverse()
        flagDL = True
        for item in reversed(arrCatalogue) :
            splitCat= item[0].split('-')
            racineCat = ''
            #assemble la chaine avant a date YYYYMMDD dans racineCat
            for split in splitCat :
                racineCat += split + '-'
                if len(split) == 8 and split.isdigit():
                    racineCat = racineCat[:-1]
                    break

            sizeCat  = item[1]
            if racineCat == racine and sizeCat == podcast['length']:
                print racine + ' : déjà présent dans le catalogue'
                flagDL  = False
                break

        if not flagDL :
            arrPodcasts.remove(podcast)
#        print podcast['title'], index, flagDL, len(arrPodcasts)
        if nombre !=None and index >= nombre:
            break
        index += 1 

    return arrPodcasts





def clean_file_name(nom):
    """
    supprime les caractères superflus du nom de l'émission
    """
    nom = nom.replace('\\"', '"')
    nom = nom.replace('?', '_')
    nom = nom.replace('’', '\'')
    nom = nom.replace('/', '_')
    nom = nom.replace('..', '.')
    return nom



def clean_title(nom):
    """
    supprime les caractères superflus ou incompatibles dans le titre du tag
    """
    nom = nom.replace('’', '\'')
    nom = nom.replace('…', '...')
    return nom







def download_podcasts(emission, arrPodcasts, params):
    """
    télécharge les podcast, le convertit si nécessaire,
    le tag si nécessaire
    """
    print '\nTéléchargements :', len(arrPodcasts), 'fichier(s)'
    for pc in arrPodcasts:
        racine  = emission['nom'] + '-' + pc['date'] 
        title   = clean_file_name(pc['title'])
        pc_file = racine + '-' + title + '.mp3'
        pc_dir  = os.path.join(params['save_dir'], emission['nom'])
        #print title
        #print file
        #print podcast_dir
        #print
        if not os.path.isdir(pc_dir):
            print 'Création dossier : ' + pc_dir 
            os.makedirs(pc_dir)
            
        print racine + ' : ' + title 
        file_name = os.path.join(pc_dir, pc_file)

        # Download the file from `url` and save it locally under `file_name`:
        response = urllib2.urlopen(pc['guid']) 
        fn = open(file_name, 'wb') 
        shutil.copyfileobj(response, fn)
        fn.close()
        #print "Fichier : ", file_name
                
        file_size =  os.path.getsize(file_name)
        if str(file_size) != pc['length']:
            #La taille d'un fichier téléchargé ne correpond pas toujours à la taille annoncée
            #bien que le fichier soit téléchargé correctement
            print '\tWarning'
            print '\tTaille fichier serveur : ', pc['length']
            print '\tTaille fichier local   : ', file_size


        #convertir le fichier si nécessaire
        args = ['avconv', '-y', '-loglevel', 'error' , '-i', file_name]
        flagConvert = False
        if 'bitrate' in emission.keys():
            args.append('-b:a')
            args.append(emission['bitrate'] +'k' )
            flagConvert = True

        if 'channels' in emission.keys():
            args.append('-ac')
            args.append(emission['channels'])
            flagConvert = True

        if flagConvert :
            args.append(file_name + '.tmp.mp3')
            #print ("Conversion ")
            subprocess.call(args)
            os.rename (  file_name + '.tmp.mp3' ,  file_name )


        #tag 
        #print "Tag"
        tag = eyeD3.Tag()
        tag.link(file_name, eyeD3.ID3_V2)
        tag.remove()
        tag.removeComments()
        tag.removeImages()
        tag.removeLyrics()
        tag.removeUserTextFrame('TDAT')
        tag.removeUserTextFrame('TRDA')
        #tag.removeUserTextFrame('WOAF')

        tag.setTitle(clean_title(pc['title']))

        if 'year' in pc.keys():
            tag.setDate(pc['year'])

        if 'artist' in emission.keys():
            tag.setArtist(emission['artist'])

        if 'album' in emission.keys():            
            tag.setAlbum(emission['album'])

        if 'genre' in emission.keys():            
            tag.setGenre(emission['genre'])
            
        try:        
            tag.update()
        except:
            print '*** Erreur écriture tag ***'

        #inscrit le fichier téléchargé dans le catalogue
        fcat = open(params['catalogue'],"a")
        fcat.write(pc_file + ";" + pc['length'] + ";\n")
        fcat.close()







def main():
    args = process_command_line()
    params, arrEmissions = parse_config_file(args.FILE_CONFIG)
    #print "args      : ", args
    #print "params    : ", params
    #print "émissions : ", arrEmissions
    if len(arrEmissions) == 0:
        print "Rien à faire ... (pas d\'émissions dans %s )" %  args.FILE_CONFIG
        exit ()

    arrCatalogue = check_params (params)

    #affichage info
    print "\n== PARAMÈTRES =="
    print "fichier configuration   : %s" % args.FILE_CONFIG
    print "                          %d émissions" % len(arrEmissions)
    print "dossier enregistrements : %s" % params['save_dir']
    print "fichier catalogue       : %s" % params['catalogue']
    print "                          %d lignes" % len(arrCatalogue)
    print "\n"
    
    #boucle sur émissions
    for emission in arrEmissions:
        arrPodcasts = lecture_rss (emission, arrCatalogue, args.NOMBRE)
        download_podcasts(emission, arrPodcasts, params)    

    return 0





if __name__ == "__main__":
    status = main()
    exit(status)

