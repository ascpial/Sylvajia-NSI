"""Pour plus d'informations sur l'utilité et le fonctionnement de ce fichier,
référez-vous au README.md"""

from __future__ import annotations
from typing import Iterator, List, Optional, Union, TYPE_CHECKING

import logging
import sys

import discordsdk
import discordsdk.exception

from .configuration import configuration
from .payloads import Payload

if TYPE_CHECKING:
    from .game import Pygame

APPLICATION_ID = configuration.application_id
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Règle de nommage :
# get : retourne une information venant de discord
# update : effectue une opération ne dépendant pas d'un paramètre mais de l'état de la classe
# set : prend en compte un paramètre et change l'état de la classe et/ou fait une interaction avec discord
# create : créé un objet sur discord, ne prend pas forcément des paramètres

class Discord:
    """Classe permettant de communiquer avec le client discord"""

    parent: Pygame
    user: discordsdk.User = None # type: ignore
    init_state: int = 0 # indique quelle est la progression de l'initialisation (3=ok)
    lobby: Lobby = None
    route: str
    peer_id: int
    enable: Optional[bool] = None # loading state
    host: bool # True si le client actuel héberge la partie

    def __init__(self, game: Pygame):
        """Initialise la classe Discord permettant de communiquer avec le client"""
        self.parent = game

        try:
            self.application = discordsdk.Discord(
                APPLICATION_ID,
                discordsdk.CreateFlags.default
            )
        except discordsdk.exception.internal_error: # discord n'est pas installé
            self.enable = False
            self.hoster = True
            self.callbacks = Callbacks(self)
            self.user_manager = None
            self.lobby_manager = None
            self.activity_manager = None
            self.network_manager = None
        else:
            self.hoster = True

            self.callbacks = Callbacks(self)

            self.user_manager = self.application.get_user_manager()
            self.lobby_manager = self.application.get_lobby_manager()
            self.activity_manager = self.application.get_activity_manager()
            self.network_manager = self.application.get_network_manager()

            self.network_manager.on_route_update = self.callbacks.on_route_update
            self.user_manager.on_current_user_update = self.callbacks.on_current_user_update
            self.lobby_manager.on_member_connect = self.callbacks.on_member_connect
            self.network_manager.on_message = self.callbacks.on_message
            self.activity_manager.on_activity_join = self.callbacks.on_activity_join
            self.lobby_manager.on_member_update = self.callbacks.on_member_update
            self.lobby_manager.on_member_disconnect = self.callbacks.on_member_disconnect
    
    def loop(self):
        """Boucle principale de la classe, fait tourner les callbacks et execute le serveur logique pour le réseau"""
        if self.enable:
            self.application.run_callbacks()
            if self.lobby:
                self.parent.players.update_pos()
    
    def loop_end(self):
        """Deuxième boucle principale de la classe, envois les messages aux autres utilisateurs"""
        if self.enable:
            self.network_manager.flush()
    
    @property
    def ready(self):
        """Retourne True si l'objet discord est prêt à être utilisé"""
        if self.init_state >= 3:
            self.enable = True
        if self.enable is False:
            return True
        return self.init_state >= 3
    
    def update_activity(self):
        """Met à jour le status discord (Rich presence)"""
        activity = discordsdk.Activity()
        activity.state = "En test d'application"
        activity.details = f"Version {configuration.version}"
        activity.assets.large_image = "player"
        if self.user:
            activity.assets.large_text = self.user.username
        if self.lobby:
            activity.secrets.join = self.lobby_manager.get_lobby_activity_secret(self.lobby.id)
            activity.party.id = str(self.lobby.id)
            activity.party.size.max_size = self.lobby.lobby.capacity
            activity.party.size.current_size = self.lobby_manager.member_count(self.lobby.id)
        
        self.activity_manager.update_activity(activity, self.callbacks.update_activity_callback)
    
    def disconnect(self):
        """Déconnecte le jeu du lobby actuel"""
        if self.lobby is not None:
            self.lobby_manager.disconnect_lobby(self.lobby.id, self.callbacks.disconnect_lobby_callback)
        
    def connect(self):
        """Créé le lobby de jeu actuel"""
        transaction = self.lobby_manager.get_lobby_create_transaction()
        transaction.set_type(1)
        transaction.set_capacity(4)
        self.lobby_manager.create_lobby(
            transaction,
            self.callbacks.create_lobby_callback
        )
    
    def connect_lobby_with_status(self, secret):
        """Déconnecte l'ancien lobby et reconnecte en utilisant le join secret passé en paramètre"""
        self.disconnect()
        self.lobby_manager.connect_lobby_with_activity_secret(secret, self.callbacks.connect_lobby_with_activity_secret_callback)
    
    def update_lobby(self):
        """Met à jour le lobby en se connectant aux utilisateurs et en mettant à jour les métadonnées"""
        self.update_metadata()
    
    def update_metadata(self):
        """Met à jour les métadonnées d'utilisateur pour peer_id et route"""
        self.set_metadata("route", self.route)
        self.set_metadata("peer_id", str(self.peer_id))

    def set_metadata(self, key:str, data:str):
        """Paramètre une métadonnée de membre de lobby"""
        data = str(data)
        mut = self.lobby_manager.get_member_update_transaction(
            self.lobby.id,
            self.user.id
        )
        mut.set_metadata(key, data)
        self.lobby_manager.update_member(
            self.lobby.id,
            self.user.id,
            mut,
            self.callbacks.update_member_callback
        )
    
    def get_metadata(self, user_id: int, key: str):
        try:
            return self.lobby_manager.get_member_metadata_value(self.lobby.id, user_id, key)
        except: return None
    
    def send_message(self, channel:int, data: Union[bytes, Payload], user_id = None, peer_id = None):
        if self.enable:
            if type(data) == Payload:
                data = str(data).encode("utf8")
            self.lobby.send_message(channel, data, user_id, peer_id)
    
    def disable(self):
        self.enable = False

class Member:
    """Classe représentant le membre d'un lobby"""

    def __init__(self, parent:Discord, user_id, peer_id, route):
        self.parent = parent
        self.id = user_id
        self.route = route
        self.peer_id = peer_id
    
    def open_network(self):
        self.parent.network_manager.open_peer(self.peer_id, self.route)
        self.parent.network_manager.open_channel(self.peer_id, 1, False) # pos channel
        self.parent.network_manager.open_channel(self.peer_id, 2, True) # world channel, for tile updates...
    
    def update_network(self, peer_id, route):
        if peer_id != self.peer_id or route != self.route:
            self.peer_id = peer_id
            self.route = route
            self.open_network()
    
    def __eq__(self, value):
        if type(value) == Member:
            return value.id == self.id
        else:
            return value == self.id

class Lobby:
    """Classe contenant les méthodes et les variables utiles pour gérer le lobby"""

    id: int
    users: List[Member]

    def __init__(self, parent:Discord, lobby:discordsdk.Lobby):
        """Initialise le lobby"""
        self.parent = parent
        self.lobby = lobby
        self.id = lobby.id
        self.users = []
    
    def iter_members(self) -> Iterator[discordsdk.User]:
        """Retourne un itérateur de tout les membres du lobby"""
        for user_id in self.iter_members_id():
            user = self.parent.lobby_manager.get_member_user(self.id, user_id)
            yield user
    
    def iter_members_id(self) -> Iterator[int]:
        """Retourne un itérateur des ids des membres du lobby"""
        for i in range(self.parent.lobby_manager.member_count(self.id)):
            yield self.parent.lobby_manager.get_member_user_id(self.id, i)
        
    def update_member(self, user_id, peer_id, route):
        if user_id not in self.users:
            member = Member(self.parent, user_id, peer_id, route)
            member.open_network()
            if member not in self.users:
                self.users.append(member)
        else:
            index = self.users.index(user_id)
            self.users[index].update_network(peer_id, route)
    
    def update_members(self):
        """Associe tout les utilisateur du lobby actuel et demande le monde au premier joueur rencontré
        (en règle générale la personne qui héberge la partie)"""
        asked = False
        for user_id in self.iter_members_id():
            if user_id != self.parent.user.id:
                peer_id = int(self.parent.lobby_manager.get_member_metadata_value(self.id, user_id, "peer_id"))
                route = self.parent.lobby_manager.get_member_metadata_value(self.id, user_id, "route")
                self.update_member(user_id, peer_id, route)
            self.parent.parent.players.new(user_id)
    
    def get_user(self, user_id):
        return self.users[self.users.index(user_id)]
    
    def get_user_with_peer_id(self, peer_id: int):
        for member in self.users:
            if member.peer_id == peer_id:
                return member
        else:
            raise KeyError("Le peer_id données n'est pas contenu dans la liste de membres")
    
    def send_message(self, channel_id: int, data: bytes, user_id: int = None, peer_id: int = None) -> None:
        if user_id is not None or peer_id is not None:
            if user_id is not None:
                peer_id = self.get_user(user_id).peer_id,
            self.parent.network_manager.send_message(
                peer_id,
                channel_id,
                data
            )
        else:
            for member in self.users:
                self.parent.network_manager.send_message(
                    member.peer_id,
                    channel_id,
                    data
                )

class Callbacks:
    """Classe contenant les callbacks des requêtes pour plus de clarté"""

    parent: Discord

    def __init__(self, parent:Discord):
        """Initialise la classe en paramétrant le parent de la classe"""
        self.parent = parent

    def on_current_user_update(self):
        """Appelé quand l'utilisateur actuel subit une mise à jour, tel que un changement de pseudo"""
        self.parent.user = self.parent.user_manager.get_current_user()
        self.parent.init_state += 1
    
    def on_route_update(self, route:str):
        """Appelé quand la route d'accès au client discord change"""
        self.parent.route = route
        self.parent.peer_id = self.parent.network_manager.get_peer_id()
        self.parent.init_state += 1
        self.parent.connect()
    
    def on_member_update(self, lobby_id, user_id):
        if user_id == self.parent.user.id:
            return
        try:
            peer_id = int(self.parent.lobby_manager.get_member_metadata_value(lobby_id, user_id, "peer_id"))
            route = self.parent.lobby_manager.get_member_metadata_value(lobby_id, user_id, "route")
            self.parent.lobby.update_member(user_id, peer_id, route)
            self.parent.update_activity()
        except discordsdk.exception.not_found: pass
        try:
            color = int(self.parent.lobby_manager.get_member_metadata_value(lobby_id, user_id, "color"))
            self.parent.parent.players[user_id].color = color
        except discordsdk.exception.not_found: pass
    
    def on_member_connect(self, lobby_id:int, user_id:int):
        if lobby_id == self.parent.lobby.id:
            self.parent.parent.players.new(user_id)
            self.parent.parent.players.update_colors()
        
    def on_member_disconnect(self, lobby_id: int, user_id: int):
        if lobby_id == self.parent.lobby.id:
            self.parent.parent.players.remove(user_id)
            self.parent.parent.players.update_colors()
            self.parent.update_activity()
        
    def on_activity_join(self, join_secret: str):
        logging.info("Demande de join reçu")
        self.parent.connect_lobby_with_status(join_secret)
    
    def on_message(self, peer_id: int, channel_id: int, message: bytes):
        payload = Payload.from_bytes(message)
        payload.peer_id = peer_id
        payload.channel_id = channel_id

        if payload.channel_id == 1:
            self.parent.parent.players.on_message(
                payload,
                self.parent
            )
        elif payload.channel_id == 2:
            self.parent.parent.map.on_message(payload, self.parent)
    
    def update_activity_callback(self, result:discordsdk.Result):
        if result == discordsdk.Result.ok:
            logging.info("Mise à jour du status faite avec succès")
        else:
            logging.error(f"Erreur lors de la mise à jour du status : {result}")
        
    def disconnect_lobby_callback(self, result:discordsdk.Result):
        if result == discordsdk.Result.ok:
            logging.info("Déconnexion au lobby faite avec succès")
        else:
            logging.error(f"Erreur lors de la déconnexion au lobby : {result}")
    
    def create_lobby_callback(self, result:discordsdk.Result, lobby:discordsdk.Lobby):
        if result == discordsdk.Result.ok:
            logging.info("Création du lobby faite avec succès")
            self.parent.lobby = Lobby(self.parent, lobby)
            self.parent.init_state += 1
            self.parent.update_lobby()
            self.parent.set_metadata("color", str(1))
            self.parent.update_activity()
        else:
            logging.error(f"Erreur lors de la création du lobby : {result}")
    
    def update_member_callback(self, result:discordsdk.Result.ok):
        if result == discordsdk.Result.ok:
            logging.info("Mise à jour de l'utilisateur faite avec succès")
        else:
            logging.error(f"Erreur lors de la mise à jour de l'utilisateur : {result}")
    
    def connect_lobby_with_activity_secret_callback(self, result:discordsdk.Result, lobby:discordsdk.Lobby):
        if result == discordsdk.Result.ok:
            logging.info("Connexion au lobby faite avec succès")
            self.parent.lobby = Lobby(self.parent, lobby)
            self.parent.update_lobby()
            self.parent.lobby.update_members()
            self.parent.parent.players.update_colors()
            self.parent.update_activity()
            self.parent.parent.map.query(self.parent)

        else:
            logging.error(f"Erreur lors de la connexion au lobby : {result}")