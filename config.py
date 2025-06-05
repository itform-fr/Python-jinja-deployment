#!/usr/bin/python3
import apt,subprocess

# définition d'une fonction permettant d'installer une liste de paquets
def install(name):
    cache=apt.Cache()
    paquet=cache.get(name)
    paquet.mark_install()
    cache.commit()

# création de la liste de paquets et installation de ces derniers
packages=("kea","bind9","python3-jinja2","python3-yaml")
for package in packages:
    install(package)

# import des modules yaml et jinja2
import yaml
from jinja2 import Environment,FileSystemLoader

# création d'une fonction qui execute une commande système
def run_cmd(cmd):
    try:
        subprocess.run(cmd.split(),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except:
        print("impossible de déplacer le fichier car il n'existe pas")

# définition d'une fonction qui converti les fichiers template en fichiers de configuration définitifs
# en remplaçant les variable par leurs valeurs
def jinja(path):
    # récuperation du nom de fichier dans a variable fichier
    fichier=path.split("/")
    fichier=fichier[len(fichier)-1]
    # ouverture du fichier config.yaml et récupération du dictionnaire ayant
    # pour nom la variable fichier précédente
    with open('config.yaml') as file:
        dict=yaml.safe_load(file).get(fichier)
    # création d'un environnement jinja permettant d'ouvrir le fichier jinja2 présent
    # dans le dossier template et remplacement des variables par le contenu du fichier yaml correspondant
    env = Environment(loader=FileSystemLoader("."))
    if ".dns" in fichier :
        template=env.get_template('templates/domain.dns.j2')
    else:
        template=env.get_template('templates/' + fichier + '.j2') 
    result=template.render(dict)
    # renomage du fichier de configuration en .back et création du nouveau fichier avec le contenu généré précédemment
    run_cmd("mv " + path + " " + path + ".back")
    file=open(path,'x')
    file.write(result)
    file.close()  


# appel de la fonction jinja pour le fichier interfaces (avec le dictionnaire interfaces dans le fichier config.yaml) et redémarrage du service
jinja('/etc/network/interfaces')
run_cmd("systemctl restart networking")

# appel de la fonction jinja pour le fichier kea-dhcp4.conf (avec le dictionnaire kea-dhcp4.conf dans le fichier config.yaml) et redémarrage du service
jinja('/etc/kea/kea-dhcp4.conf')
run_cmd("systemctl restart kea-dhcp4-server")

jinja('/etc/bind/named.conf.local')
with open('config.yaml') as file:
    domain=yaml.safe_load(file).get('named.conf.local').get('domain')
jinja('/var/cache/bind/'+domain+'.dns')
run_cmd("systemctl restart named")
