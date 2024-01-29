import random
import sys
import shelve

# Game variables
game_vars = {
    'turn': 1,                      # Current Turn
    'monster_kill_target': 20,      # Number of kills needed to win
    'monsters_killed': 0,           # Number of monsters killed so far
    'num_monsters': 0,              # Number of monsters in the field
    'gold': 10,                     # Gold for purchasing units
    'threat': 0,                    # Current threat metre level
    'max_threat': 10,               # Length of threat metre
    'danger_level': 1,              # Rate at which threat increases
    }

archer = {'shortform' : 'ARCHR',
          'name': 'Archer',
          'maxHP': 5,
          'min_damage': 1,
          'max_damage': 4,
          'price': 5
          }

cannon = {'shortform' : 'CANON',
          'name': 'Cannon',
          'maxHP': 8,
          'min_damage': 3,
          'max_damage': 5,
          'price': 7
          }
             
wall = {'shortform': 'WALL',
        'name': 'Wall',
        'maxHP': 20,
        'min_damage': 0,
        'max_damage': 0,
        'price': 3
        }

zombie = {'shortform': 'ZOMBI',
          'name': 'Zombie',
          'maxHP': 15,
          'min_damage': 3,
          'max_damage': 6,
          'moves' : 1,
          'reward': 2
          }

werewolf = {'shortform': 'WWOLF',
            'name': 'Werewolf',
            'maxHP': 10,
            'min_damage': 1,
            'max_damage': 4,
            'moves' : 2,
            'reward': 3
            }

skeleton  = {'shortform': 'SKELE',
          'name': 'Skeleton',
          'maxHP': 20,
          'min_damage': 1,
          'max_damage': 3,
          'moves' : 1,
          'reward': 4
          }

heal  = {'name' : 'Heal',
        'minusHP': 0,
        'addHP': 5,
        'target' : 'defender',
        'area' : 3,
        'price': 5
          }

poison  = {'name' : 'Poison',
          'minusHP': 5,
          'addHP': 0,
          'target' : 'monster',
          'area' : 3,
          'price': 5
          }


field = [ [None, None, None, None, None, None, None],
          [None, None, None, None, None, None, None],
          [None, None, None, None, None, None, None],
          [None, None, None, None, None, None, None],
          [None, None, None, None, None, None, None] ]

function_list = [heal, poison]
monster_list = [zombie, werewolf, skeleton]
defender_list = [wall, archer, cannon]
buy_menu = defender_list + ["Don't buy"]
function_menu = function_list + ["Don't buy"]
main_menu = ["Start new game", "Load saved game", "Quit"]
combat_menu = ["Buy", "End turn", "Save game", "Quit"]
#game_options = ["rows", "columns", "target kills", , 

#----------------------------------------------------------------------
# draw_field()
#
#    Draws the field of play
#    The column numbers only go to 3 since players can only place units
#      in the first 3 columns
#----------------------------------------------------------------------
def draw_field(new):
    if new == False:
        for row in range(len(field)):
            for column in range(3):
                for defender in defender_list[1:]:
                    if field[row][column] != None and field[row][column][0] == defender['shortform']:
                        defender_attack(defender, field, row, column)
        for row in range(len(field)):
            for column in range(len(field[0])):
                for monster in monster_list:
                    if field[row][column] != None and field[row][column][0] == monster['shortform']:
                        monster_advance(monster, field, row, column)
    x = ord("A")
    spawn_monster(field, monster_list)
    for column in range(len(field[0])):
        print("{:>5}".format(column+1),end = " ")
    print()
    for row in range(len(field)):
        print(" "+"+-----"*len(field[0])+"+")
        print(chr(x),end = "")
        for column in range(len(field[0])):
            if field[row][column] != None:
                print("|{:^5}".format(field[row][column][0]),end = "")
            else:
                print("|{:^5}".format(" "),end = "")      

        print("|")
        print(" ",end = "")
        for column in range(len(field[0])):
            if field[row][column]  != None:
                print("|"+"{:2}/{:<2}".format(field[row][column][1],field[row][column][2]),end = "")
            else:
                print("|"+"{:^5}".format(" "),end = "")
        print("|")
        x = x+1
    print(" "+"+-----"*len(field[0])+"+")
    return 

#----------------------------
# show_main_menu()
#
#    Displays the main menu
#----------------------------
def show_main_menu():
    for i in range(len(main_menu)):
        print("{}. {}".format(i+1, main_menu[i]))

#----------------------------
# show_combat_menu()
#
#    Displays the combat menu
#----------------------------
def show_combat_menu(game_vars):
    print('Turn  {:<6}Threat = [{}{}]     Danger Level {}'.format(game_vars['turn'],'-'*game_vars['threat'],' '*(game_vars['max_threat']-game_vars['threat']),game_vars['danger_level']))
    print('Gold = {:<5}Monsters killed = {}/{}'.format(game_vars['gold'],game_vars['monsters_killed'],game_vars['monster_kill_target']))
    for i in range(len(combat_menu)):
        print("{}. {:<13}".format(i+1, combat_menu[i]), end = "")
        if i % 2 != 0:
            print()

#-------------------------------------------------------------------
# buy_unit()
#
#    Allows player to buy a unit and place it using place_unit()
#-------------------------------------------------------------------
def buy_unit(field, game_vars, buy_menu, defender_list):
    while True:
        print("What unit do you wish to buy?")
        for unit in range(len(buy_menu)-1):
            print("{}. {} ({} gold)".format(unit+1, buy_menu[unit]['name'], buy_menu[unit]['price']))
        print("{}. {}".format(len(buy_menu), buy_menu[-1]))
        choice = choice_error(buy_menu)
        if choice != len(buy_menu):
            defender = defender_list[choice-1]
            if defender['price'] > game_vars['gold']:
                print("Insufficient value. Please select something else.")
                continue
            position = position_error(field)        
            game_vars['gold'] -= defender['price']
            field[ord(position[0].upper())-65][int(position[1])-1] = [defender['shortform'],defender['maxHP'],defender['maxHP']]
            break
        break

#-------------------------------------------------------------------
# buy_functions()
#
#    Allows player to buy a unit and place it using place_unit()
#-------------------------------------------------------------------
def buy_functions(field, function_menu, defender_list, monster_list):
    while True:
        print("What function do you wish to buy?")
        for function in range(len(function_menu)-1):
            print("{}. {} ({} gold)".format(function+1, function_menu[function]['name'], function_menu[function]['price']))
        print("{}. {}".format(len(function_menu), buy_menu[-1]))
        choice = choice_error(function_menu)
        if choice != len(function_menu):
            function = function_list[choice-1]
            if function['price'] > game_vars['gold']:
                print("Insufficient value. Please select something else.")
                continue
            placement = placement_error(function_list)
            game_vars['gold'] -= function['price']
            function_variance = int((function['area']-1)/2)
            if function['target'] == 'monster':
                for row in range(ord(placement[0].upper())-65-function_variance, ord(placement[0].upper())-65+function_variance+1):
                    for column in range(int(placement[1])-1-function_variance, int(placement[1])+function_variance):
                        for monster in monster_list:
                            try:
                                if field[row][column] != None and field[row][column][0] == monster['shortform']:
                                    field[row][column][1] -= function['minusHP']
                                    print("{} reduces health of {} in lane {}{} by {}.".format(function['name'], monster['name'], chr(row+65), column+1, function['minusHP']))
                            except:
                                continue
            else:
                for row in range(ord(placement[0].upper())-65-function_variance, ord(placement[0].upper())-65+function_variance+1):
                    for column in range(int(placement[1])-1-function_variance, int(placement[1])+function_variance):
                        for defender in defender_list:
                            try:
                                if field[row][column] != None and field[row][column][0] == defender['shortform'] and field[row][column][1]<field[row][column][2]:
                                    field[row][column][1] += function['addHP']
                                    if field[row][column][2] < field[row][column][1]:
                                        field[row][column][1] = field[row][column][2]
                                    print("{} increases health of {} in lane {}{} by {}.".format(function['name'], defender['name'], chr(row+65), column+1, function['addHP']))
                            except:
                                continue
        break


#-----------------------------------------------------------
# defender_attack()
#
#    Defender unit attacks.
#-----------------------------------------------------------
def defender_attack(defender, field, row, column):
    first_monster = False 
    for column_monster in range(column+1,len(field[row])):
        for monster in monster_list:
            if first_monster == True:
                continue
            elif field[row][column_monster] != None and field[row][column_monster][0] == monster['shortform']:
                    first_monster = True
                    damage = random.randint(defender['min_damage'],defender['max_damage'])
                    field[row][column_monster][1] -= damage
                    print("{} in lane {} shoots {} for {} damage!".format(defender['name'], chr(row+65), monster['name'], damage))
                    if field[row][column_monster][1] <= 0:
                        print("{} dies!".format(monster['name']))
                        field[row][column_monster] = None
                        print("You gain {} gold as a reward.".format(monster['reward']))
                        game_vars['gold'] += monster['reward']
                        game_vars['threat'] += monster['reward']
                        game_vars['num_monsters'] -= 1
                        game_vars['monsters_killed'] += 1
                        if game_vars['monsters_killed'] == game_vars['monster_kill_target']:
                            print("You have protected the city! You win!")
                            sys.exit()

#-----------------------------------------------------------
# monster_advance()
#
#    Monster unit advances.
#       - If it lands on a defender, it deals damage
#       - If it lands on a monster, it does nothing
#       - If it goes out of the field, player loses
#-----------------------------------------------------------
def monster_advance(monster, field, row, column):
    moves = int(monster['moves'])
    new_column = column
    while moves > 0:
        if field[row][new_column-1] != None:
            for defender in defender_list:
                if field[row][new_column-1][0] == defender['shortform']:
                    damage = random.randint(monster['min_damage'],monster['max_damage'])
                    field[row][new_column-1][1] -= damage
                    print("{} in lane {} hits {} for {} damage!".format(monster['name'], chr(row+65), defender['name'], damage))
                    if field[row][new_column-1][1] <= 0:
                        print("{} dies!".format(defender['name']))
                        field[row][new_column-1] = None
                        break
        else:
            field[row][new_column-1] = field[row][new_column]
            field[row][new_column] = None
            print("{} in lane {} advances!".format(monster['name'], chr(row+65)))
            new_column -= 1
            if new_column < 0:
                print("A {} has reached the city! All is lost!".format(monster['name']))
                print("You have lost the game. :(")
                sys.exit()
        moves -= 1
        
#---------------------------------------------------------------------
# spawn_monster()
#
#    Spawns a monster in a random lane on the right side of the field.
#---------------------------------------------------------------------
def spawn_monster(field, monster_list):
    game_vars['num_monsters'] = 0
    for row in range(len(field)):
        for column in range(len(field[0])):
            for monster in monster_list:
                if field[row][column] != None and field[row][column][0] == monster['shortform']:
                    game_vars['num_monsters'] += 1

    monster = monster_list[random.randint(0,len(monster_list)-1)]
    if game_vars['num_monsters'] == 0:
        field[random.randint(1,len(field)-1)][-1] = [monster['shortform'],monster['maxHP'],monster['maxHP']]
    if game_vars['threat'] >= 10:
        field[random.randint(1,len(field)-1)][-1] = [monster['shortform'],monster['maxHP'],monster['maxHP']]

#-------------------------------------
# save_game()
#
#    Saves the game in the file
#-------------------------------------
def save_game():
    f = shelve.open('save')
    f['field'] = field
    f['game_vars'] = game_vars
    f['monster_list'] = monster_list
    f.close()
    print()
    print('Game saved!')

#-------------------------------------
# load_game()
#
#    Loads the game from file
#-------------------------------------
def load_game():
    f = shelve.open('save')
    field = f['field']
    game_vars = f['game_vars']
    monster_list = f['monster_list']
    return(field, game_vars, monster_list)

#-------------------------------
# error()
#
#    Checks for errors in inputs
#-------------------------------
def choice_error(item_list):
    while True:
        try:
            choice = int(input("Your choice? "))
            if choice <= 0 or choice > len(item_list):
                print("Please enter a number from 1 to {}".format(len(item_list)))
            else:
                return choice
                break
        except:
            print("Please enter a number.")

def position_error(item_list):
    while True:
        position = input("Place where? ")
        if len(position)> 2 or position[0].isalpha() == False or ord(position[0].upper())-65 > len(item_list) or int(position[1]) > 3:
            print("Invalid position. Please enter a position from {}{} to {}{}".format(chr(65),1,chr(65+len(item_list)-1),3))
        elif field[ord(position[0].upper())-65][int(position[1])-1] != None:
            print("This position is taken.")
        else:
            return position
            break

def placement_error(function_list):
    while True:
        placement = input("Place where? ")
        if len(placement)> 2 or placement[0].isalpha() == False or ord(placement[0].upper())-65 > len(field) or int(placement[1]) > len(field[0]):
            print("Invalid position. Please enter a position from {}{} to {}{}".format(chr(65),1,chr(65+len(field)-1),len(field[0])))
        else:
            return placement
            break


#-----------------------------------------
#               MAIN GAME
#-----------------------------------------

print("Desperate Defenders")
print("-------------------")
print("Defend the city from undead monsters!")
print()
show_main_menu()
while True:
    choice = choice_error(main_menu)
    if choice == 1:
        new = False
        break
    elif choice == 2:
        try:
            field, game_vars, monster_list = load_game()
            new = True
            break
        except:
            print("No saved game.")            
    else:
        print()
        print('See you next time!')
        sys.exit()

while True:
    draw_field(new)
    new = False
    show_combat_menu(game_vars)
    choice = choice_error(combat_menu)
    if choice == 1:
        buy_unit(field, game_vars, buy_menu, defender_list)
        buy_functions(field, function_menu, defender_list, monster_list)
    elif choice == 2:
        pass
    elif choice == 3:
        save_game()
        break
    else:
        print()
        print('See you next time!')
        sys.exit()
    game_vars['gold'] += 1
    game_vars['turn'] += 1
    game_vars['threat'] += random.randint(1,game_vars['danger_level'])
    if game_vars['turn'] % 12 == 0:
        game_vars['danger_level'] += 1
        print("The evil grows stronger!")
        for monster in monster_list:
            monster['maxHP'] += 1
            monster['min_damage'] += 1
            monster['max_damage'] += 1
            monster['reward'] += 1            
    if game_vars['threat'] > game_vars['max_threat']:
        game_vars['threat'] = 0

# TO DO: ADD YOUR CODE FOR THE MAIN GAME HERE!

