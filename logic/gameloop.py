from logic.entities import Player
from logic.map import Map
from logic.utils import clear_screen, exit_game, entities_data, map_data
from logic.items import Hand, Sword, HealthPotion, DefensePotion

player = None
game_map = None

## MAIN MENU ##
def main_menu():
    print("[1] - New Game")
    print("[X] - Exit")

    option = input("Choose an option: ").lower()

    if option == "1":
        new_game()
    elif option == "x":
        exit_game()
    else:
        print("Invalid option!")
        main_menu()

## NEW GAME ##
def new_game():
    print("Starting a new game...")
    global player
    player = Player(entities_data["player"])
    global game_map
    game_map = Map(map_data)

    hand = Hand()
    sword = Sword()
    health_potion = HealthPotion()
    defense_potion = DefensePotion()

    player.pick_up_item(hand)
    player.pick_up_item(sword)
    player.pick_up_item(health_potion)
    player.pick_up_item(defense_potion)

    print("Press any key to continue...")
    input()
    game_loop()

## GAME LOOP ##
def game_loop():
    while True:
        game_map.print_map()
        game_map.display_loot(player.position)
        player_action()

def player_action():
    print("\n# Would you like to move? <z/q/s/d>")
    print("# Type 'bag' to check your inventory.")
    print("# Type 'exit' to return to the main menu.")

    choice = input("> ").lower()

    if choice in ["z", "q", "s", "d"]:
        clear_screen()
        player.move(choice, game_map)
    elif choice == "bag":
        clear_screen()
        player.use_inventory()
    elif choice == "pick":
        game_map.pick_up_loot(player.position)
    elif choice == "exit":
        main_menu()
    else:
        print("Invalid option!")