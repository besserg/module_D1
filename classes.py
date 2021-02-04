import requests
import json
from settings import api_key, api_token, base_url

class TrelloDesk:
    def __init__(self, username):

        self.columns = {}
        self.cards = {}
        self.cards_by_column = {}
        self.username = username
        self.desk_dict = {}
        self.get_all()

    def api_responce(self, url, rtype="GET", add_query=None):
        headers = {"Accept": "application/json"}
        query = {
            'key': api_key,
            'token': api_token,
        }

        if add_query:
            for key, value in add_query.items():
                query[key] = value

        response = requests.request(
            rtype,
            url,
            headers=headers,
            params=query
        )
        return response

    def get_all(self):
        self.desk_dict = {}
        self.columns = {}
        self.cards = {}
        self.get_desks()
        self.get_columns()
        self.get_cards()

    def get_desks(self):
        url = "{}/{}/{}/{}".format(base_url, 'members', self.username, 'boards')
        responce = self.api_responce(url)
        sc = responce.status_code
        if sc and sc == 200:
            desks = json.loads(responce.text)
            for desk in desks:
                self.desk_dict[desk.get('name')] = desk.get('id')

    def get_columns(self, desk_name=None, need_upd=False):
        result_columns = {}
        if desk_name:
            desk_id = self.desk_dict[desk_name]
            if desk_id:
                url = "{}/{}/{}/{}".format(base_url, 'boards', desk_id, 'lists')
                responce = self.api_responce(url)
                if responce.status_code == 200:
                    lists = json.loads(responce.text)
                    for column in lists:
                        key = (desk_name, column.get('name'))
                        result_columns[key] = column.get('id')
        elif self.desk_dict and not desk_name:
            if need_upd:
                self.get_desks()
            for desk_name, desk_id in self.desk_dict.items():
                url = "{}/{}/{}/{}".format(base_url, 'boards', desk_id, 'lists')
                responce = self.api_responce(url)
                if responce.status_code == 200:
                    lists = json.loads(responce.text)
                    for column in lists:
                        key = (desk_name, column.get('name'))
                        self.columns[key] = column.get('id')
                    continue
        return result_columns

    def get_cards(self, desk_name=None, column_name=None, need_upd=False):
        result_cards = {}
        if desk_name and column_name:
            try:
                column_id = self.columns[(desk_name, column_name)]
            except:
                return result_cards
            if column_id:
                url = "{}/{}/{}/{}".format(base_url, 'lists', column_id, 'cards')
                responce = self.api_responce(url)
                if responce.status_code == 200:
                    jcards = json.loads(responce.text)
                    for card in jcards:
                        key = (desk_name, column_name, card.get('name'))
                        result_cards[key] = card.get('id')
        elif self.desk_dict and self.columns:
            if need_upd:
                self.get_columns(need_upd=need_upd)
            for column_name, column_id in self.columns.items():
                url = "{}/{}/{}/{}".format(base_url, 'lists', column_id, 'cards')
                responce = self.api_responce(url)
                if responce.status_code == 200:
                    jcards = json.loads(responce.text)
                    card_count = 0
                    for card in jcards:
                        key = (column_name[0], column_name[1], card.get('name'), card_count)
                        self.cards[key] = (card.get('id'), card.get('desc'))
                        card_count += 1
                    self.cards_by_column[column_name] = card_count
                    continue
        return result_cards

    def create_desk(self, name, **kwargs):
        created = False
        url = "{}/{}/".format(base_url, 'boards')
        params = {'name': name}
        if kwargs:
            for key, value in kwargs.items():
                params[key] = value
        responce = self.api_responce(url, "POST", params)
        if responce.status_code == 200:
            desk = json.loads(responce.text)
            self.desk_dict[name] = desk.get('id')
            created = True
        return created

    def create_column(self, desk_name, column_name, **kwargs):
        created = False
        board_id = self.desk_dict.get(desk_name)
        if board_id:
            url = "{}/{}/{}/{}".format(base_url, 'boards', board_id, 'lists')
            params = {'name': column_name}
            if kwargs:
                for key, value in kwargs.items():
                    params[key] = value
            responce = self.api_responce(url, "POST", params)
            if responce.status_code ==200:
                new_col = json.loads(responce.text)
                key = (desk_name, column_name)
                self.columns[key] = new_col.get('id')
                created = True
        return created

    def create_card(self, desk_name, column_name, card_name, **kwargs):
        created = False
        board_id = self.desk_dict.get(desk_name)
        column_id = self.columns.get((desk_name, column_name))
        if board_id and column_id:
            url = "{}/{}/".format(base_url, 'cards')
            params = {'idList': column_id, 'name': card_name, }
            if kwargs:
                for key, value in kwargs.items():
                    params[key] = value
            responce = self.api_responce(url, "POST", params)
            if responce.status_code == 200:
                new_card = json.loads(responce.text)
                key = (desk_name, column_name, card_name)
                self.cards[key] = (new_card.get('id'), new_card.get('desc'))
                created = True
        return created

    def update_item(self, item_id, item, **kwargs):
        result = False
        result_txt = ''
        if kwargs:
            if 'action' in kwargs.keys():
                action = kwargs.pop('action')
                if action == 'move':
                    idList = kwargs.get('idList')
                    url = "{}/{}/{}".format(base_url, item, str(item_id))
                    responce = self.api_responce(url, "PUT", {'idList': idList})
                    if responce.status_code == 200:
                        result = True
                        self.get_all()
                    else:
                        result_txt = responce.text
                elif action == 'update':
                    pass
                elif action == 'delete':
                    url = '{}/{}/{}'.format(base_url, item, str(item_id))
                    responce = self.api_responce(url, "DELETE")
                    if responce.status_code == 200:
                        result = True
                        self.get_all()
        return result, result_txt