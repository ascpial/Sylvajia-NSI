import json

CONFIGURATION_FILE = "./data/configuration.json"

class Configuration:
    """Classe permettant de lire et d'écrire facilement la configuration
    """
    def __init__(self):
        """Initialise la configuration en lisant le fichier de configuration dans `./data/configuration.json`."""
        self.read()

    def read(self):
        """Lit le fichier de configuration au chemin `CONFIGURATION_FILE`.
        """
        with open(CONFIGURATION_FILE, 'r') as config:
            self.json = json.load(config)
    def write(self):
        """Ecrit dans le fichier de configuration `CONFIGURATION_FILE`.
        """
        with open(CONFIGURATION_FILE, 'w') as config:
            json.dump(
                self.json,
                config,
                indent=4
            )

    @property
    def application_id(self):
        return self.json["application_id"]
    
    @application_id.setter
    def application_id(self, value):
        self.json["application_id"] = value
    
    @property
    def version(self):
        return self.json["version"]
    
    @version.setter
    def version(self, value):
        self.json["version"] = value

configuration = Configuration() # on créé la configuration directement pour un accès plus aisé