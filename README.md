# podrf
gestion podcasts Radio France

Script python automatisant le téléchargement, le classement,
la conversion et le taggage de podcasts de Radio France (testé 
sur France Inter et France Culture)

Les fichiers sont nommés selon la syntaxe : 

 CODE_EMISSION-DATE-Titre.mp3

dans le dossier 'CODE-EMISSION'

    CODE_EMISSION est défini dans le fichier de configuration
    DATE est au format AAAAMMJJ
    Titre est récupéré sur la page du flux rss

voir fichier config.txt pour plus d'infos

4 fichiers :

    podrf.py       : programme principal
                     utiliser l'option -n pour limiter le
                     nombre de podcasts à télécharger
    rss_inter.py   : liste les flux rss de France Inter
    rss_culture.py : liste les flux rss de France Culture
    config.cfg     : exemple de fichier de configuration

dépendances :

    python-eyed3
    avconv

contact :
    wlourf1@yahoo.com
