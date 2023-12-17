from woob.core import Woob
from woob.capabilities.bank import CapBank

import csv

class BankDataExtractor:
    def __init__(self, website, login, password, bank_module):
        self.website = website
        self.login = login
        self.password = password
        self.bank_module = bank_module

    def extract_data(self) -> (list, list):
        w = Woob()
        w.load_backend(self.bank_module, 'bankend_'+self.bank_module, {'website': self.website, 'login': self.login, 'password': self.password})
        accounts = list(w.iter_accounts())
        history = list(w.iter_history(accounts[0]))
        return accounts, history

    def save_history(self, history):

        # Save the history in a csv file
        with open('history2.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'label', 'amount']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in history:
                writer.writerow({'date': str(row.date), 'label': row.label, 'amount': str(float(row.amount))})


bankdataextractor = BankDataExtractor('www.ca-charente-perigord.fr', 'XXXXXXXXX', 'XXXXXX', 'cragr')
print(bankdataextractor.extract_data())


class WebsiteProvider:
    def __init__(self):
        self.modules = {
            'Crédit Agricole': 
                ["cragr" , {"website" : {
                    'www.ca-alpesprovence.fr': 'Alpes Provence',
                    'www.ca-alsace-vosges.fr': 'Alsace-Vosges',
                    'www.ca-anjou-maine.fr': 'Anjou Maine',
                    'www.ca-aquitaine.fr': 'Aquitaine',
                    'www.ca-atlantique-vendee.fr': 'Atlantique Vendée',
                    'www.ca-briepicardie.fr': 'Brie Picardie',
                    'www.ca-cb.fr': 'Champagne Bourgogne',
                    'www.ca-centrefrance.fr': 'Centre France',
                    'www.ca-centreloire.fr': 'Centre Loire',
                    'www.ca-centreouest.fr': 'Centre Ouest',
                    'www.ca-centrest.fr': 'Centre Est',
                    'www.ca-charente-perigord.fr': 'Charente Périgord',
                    'www.ca-cmds.fr': 'Charente-Maritime Deux-Sèvres',
                    'www.ca-corse.fr': 'Corse',
                    'www.ca-cotesdarmor.fr': 'Côtes d\'Armor',
                    'www.ca-des-savoie.fr': 'Des Savoie',
                    'www.ca-finistere.fr': 'Finistere',
                    'www.ca-franchecomte.fr': 'Franche-Comté',
                    'www.ca-guadeloupe.fr': 'Guadeloupe',
                    'www.ca-illeetvilaine.fr': 'Ille-et-Vilaine',
                    'www.ca-languedoc.fr': 'Languedoc',
                    'www.ca-loirehauteloire.fr': u'Loire Haute Loire',
                    'www.ca-lorraine.fr': 'Lorraine',
                    'www.ca-martinique.fr': 'Martinique Guyane',
                    'www.ca-morbihan.fr': 'Morbihan',
                    'www.ca-nmp.fr': 'Nord Midi-Pyrénées',
                    'www.ca-nord-est.fr': 'Nord Est',
                    'www.ca-norddefrance.fr': 'Nord de France',
                    'www.ca-normandie-seine.fr': 'Normandie Seine',
                    'www.ca-normandie.fr': 'Normandie',
                    'www.ca-paris.fr': 'Ile-de-France',
                    'www.ca-pca.fr': 'Provence Côte d\'Azur',
                    'www.ca-reunion.fr': 'Réunion',
                    'www.ca-sudmed.fr': 'Sud Méditerranée',
                    'www.ca-sudrhonealpes.fr': 'Sud Rhône Alpes',
                    'www.ca-toulouse31.fr': 'Toulouse 31',
                    'www.ca-tourainepoitou.fr': 'Tourraine Poitou',
                    'www.ca-valdefrance.fr': 'Val de France',
                    'www.ca-pyrenees-gascogne.fr': 'Pyrénées Gascogne',
                    }}, 
                {'login' : 'Identifiant à 11 chiffres'}, 
                {'password':'Code personnel à 6 chiffres'}]
            }

    def get_websites(self, module):
        return self.modules.get(module, [])


"""
# Save the history in a csv file

with open('history.csv', 'w', newline='') as csvfile:
    fieldnames = ['date', 'label', 'amount']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in history:
        writer.writerow({'date': str(row.date), 'label': row.label, 'amount': str(float(row.amount))})
"""