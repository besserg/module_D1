from classes import TrelloDesk
from settings import menu_items

def get_boards():
    if td.desk_dict:
        for desk_name, desk_id in td.desk_dict.items():
            print(desk_name)
            for key_col, col_id in td.columns.items():
                if desk_name in key_col:
                    print(f"\t{key_col[1]} ({td.cards_by_column[key_col]})")
                    for key_card, card_id in td.cards.items():
                        if desk_name in key_card and key_col[1] in key_card:
                            print('\t'*2 + key_card[2])

def create_desk():
    board_name = input('Input new Board name:')
    if board_name:
        res = td.create_desk(name=board_name)
        if res:
            print(f'Board {board_name} created succesfully')
        else:
            print(f"Board {board_name} doesn't created")

def check_card_doubles(card_name):
    have_dobles = False
    cc = 0
    desk_name, column_name = '', ''
    for names in td.cards.keys():
        if card_name in names:
            cc += 1
            if cc > 1:
                have_dobles = True
                desk_name = names[0]
                column_name = names[1]
                break
    return have_dobles, desk_name, column_name

def create_column():
    board_name = input('Input created Board name:')
    column_name = input('Input new Column name:')
    if board_name and column_name:
        res = td.create_column(desk_name=board_name, column_name=column_name)
        if res:
            print(f"Column {column_name} created succefully on Board '{board_name}'")
        else:
            print(f"Column {column_name} doesn't created")

def create_card():
    board_name = input('Input created Board name:')
    column_name = input('Input created Column name:')
    card_name = input('Input new Card name:')
    desc_card = input('Input description for new Card:')
    params = {'desc': desc_card}
    doubles, desk_doubles, column_doubles = check_card_doubles(card_name)
    if doubles:
        print(f"You have Card with the same name on the Board '{desk_doubles}' -> Column '{column_doubles}'!")
        choice = input('Do you want to change Card name (Y/N)? ')
        if choice.upper() in ('Y', 'Д', 'YES', 'ДА'):
            card_name = input('Input new Card name:')
    if board_name and column_name and card_name:
        res = td.create_card(board_name, column_name, card_name, **params)
        if res:
            print(f"Card {card_name} created succefully on Board '{board_name}' -> Column '{column_name}'")
            tc = td.cards_by_column[(board_name, column_name)]
            td.cards_by_column[(board_name, column_name)] = tc + 1
        else:
            print(f"Card {card_name} doesn't created")

def move_card():
    card_name = input('Input Card name to move:')
    dbl = {}
    choice = None
    move_id = None
    isdbl, dbld, dblc = check_card_doubles(card_name)
    if isdbl:
        cc = 0
        print('You have more than one Card with tha same name!')
        print("Select one from the list below")
        for key, value in td.cards.items():
            if card_name in key:
                cc += 1
                print(
                    f"{cc}. Board: {key[0]} -> Column: {key[1]} -> "
                    f"Card: {key[2]} -> CardId: {value[0]} -> CardDesc: {value[1]}"
                )
                dbl[cc] = (key[0], value[0])  # Board Name, Card Id
        point = int(input('Select point:'))
        choice = dbl[point]
    else:
        for key, value in td.cards.items():
            if card_name in key:
                choice = (key[0], value[0])
                break
    if choice:
        new_column_name = input(f"Input Column name to move (Board: '{choice[0]}'): ")
        key = (choice[0], new_column_name)
        try:
            move_id = td.columns.get(key)
        except:
            print('You have no that Board and Column!')
            move_id = None
    if move_id:
        params = {'action': 'move', 'idList': move_id}
        res, res_txt = td.update_item(choice[1], 'cards', **params)
        if res:
            print(f"{card_name} moved succesfully. Press 1 to show all info!")
        else:
            print(f"Moving failed! Error: {res_txt}")

def del_card():
    card_name = input('Input Card name to delete:')
    dbl = {}
    choice = None
    isdbl, dbld, dblc = check_card_doubles(card_name)
    if isdbl:
        cc = 0
        print('You have more than one Card with tha same name!')
        print("Select one from the list below")
        for key, value in td.cards.items():
            if card_name in key:
                cc += 1
                print(
                    f"{cc}. Board: {key[0]} -> Column: {key[1]} -> "
                    f"Card: {key[2]} -> CardId: {value[0]} -> CardDesc: {value[1]}"
                )
                dbl[cc] = (key, value)  # Board Name, Card Id
        point = int(input('Select point:'))
        choice = dbl[point]
    else:
        for key, value in td.cards.items():
            if card_name in key:
                choice = (key, value)
                break
    if choice:
        card_id = choice[1][0]
        prop = {'action': 'delete'}
        result, result_txt = td.update_item(card_id, 'cards', **prop)
        if result:
            print(f"Card '{choice[0][2]}' deleted successfully!")
        else:
            print(f"Error! {result_txt}")


def del_desc():
    print('Select Board name from the list below')
    cc = 1
    desks = {}
    for key, value in td.desk_dict.items():
        print(f"{cc}. {key}")
        desks[cc] = (key, value)
        cc += 1
    choice = input('Select point:')
    try:
        board_id = desks[choice][1]
        prop = {'action': 'delete'}
        result, result_txt = td.update_item(board_id, 'boards', **prop)
        if result:
            print(f"Board '{desks[choice][0]}' deleted successfylly!")
        else:
            print(f"Error! {result_txt}")
    except:
        print('Error!')



responce_dict = {
   '1': get_boards,
   '2': create_desk,
   '3': create_column,
   '4': create_card,
   '5': move_card,
   '6': del_card,
   '7': del_desc,
}

name = input('Input Trello username:')
print('Downloading userinfo from Trello API...')
td = TrelloDesk(name)

while 1 == 1:
   for k, v in menu_items.items():
      print('{}:{}'.format(k, v))
   choice = input("Select a menu point:")
   if choice not in menu_items.keys():
      print('Error!')
   elif choice == 'q':
      print('Bye!')
      break
   else:
      if choice in responce_dict.keys():
         trello_func = responce_dict[choice]
         trello_func()
         print()