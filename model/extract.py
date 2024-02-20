from woob.core import Woob
from woob.capabilities.bank import CapBank
from model.db.data import Account, Transaction
from datetime import date
import csv

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
                {'login' : '11-digit'}, 
                {'password':'6-digit'}]
            }
        
    def get_banks(self) -> list:
        return list(self.modules.keys())
    
    def get_bank_module(self, bank : str) -> str:
        return self.modules[bank][0]
    
    def get_websites(self, bank : str) -> list:
        return list(self.modules[bank][1]['website'])
    
    def get_login_conditions(self, bank : str) -> dict:
        return self.modules[bank][2]['login']
    
    def get_password_conditions(self, bank : str) -> dict:
        return self.modules[bank][3]['password']


class BankDataExtractor:
    def __init__(self, website, login, password, bank_name):
        self.website = website
        self.login = login
        self.password = password
        self.bank_module = WebsiteProvider().get_bank_module(bank_name)

    def extract_data(self) -> tuple[list[Account], list[list[Transaction]]]:
        """
        Extract the data from the bank website
        
        Returns:
        -------
        list
            The accounts
        list
            The list of the history of each account
        """
        try:
            w = Woob()
            w.load_backend(self.bank_module, 'bankend_'+self.bank_module, {'website': self.website, 'login': self.login, 'password': self.password})
            accounts = list(w.iter_accounts())
            accounts_model = [Account(number=account.id, name=account.label, balances=[str(account.balance)], dates=[str(date.today())], currency=account.currency) for account in accounts]
            history = []
            for account in accounts:
                transactions = list(w.iter_history(account))
                # Convert the transactions to the Transaction model
                history.append([Transaction(date=str(transaction.date), description=transaction.label, amount=str(transaction.amount)) for transaction in transactions])
            return accounts_model, history
        except Exception as e:
            if "password" in str(e) :
                raise ValueError("Password format incorrect")
            else:
                raise ValueError("Invalid client number or password, please check your bank service")

    def save_history(self, history : list[Transaction]):

        # Save the history in a csv file
        with open('history2.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'label', 'amount']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for transaction in history:
                writer.writerow({'date': transaction.date, 'label': transaction.label, 'amount': transaction.amount})

if __name__ == "__main__":
    bde = BankDataExtractor('www.ca-charente-perigord.fr', '******', '*****', 'Crédit Agricole')
    accounts, history = bde.extract_data()
    print(accounts)
    print(history)
    bde.save_history(history[0])