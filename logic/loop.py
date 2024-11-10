import logic.map as m
import logic.utils as u
import logic.entities as e

game_map = None
player = None

def main_menu():
    print("Main menu")
    print("[1] Start game")
    print("[X] Exit")
    choice = input("Enter choice: ")
    if choice == "1":
        new_game()
    elif choice.lower() == "x":
        print("Exiting game")
    else:
        print("Invalid choice")
        main_menu()

def new_game():
    print("Starting new game")
    global game_map, player
    game_name = "Tutorial"
    game_map = m.Map(u.map_data[game_name], u.tiles_data, game_name)

    player = e.Player(u.entities_data["player"])
    print(player)
    
    game_loop()

def game_loop():
    print("Game loop")
    player.print_stats()
    print("Use [Z/Q/S/D] or [N/W/S/E] to move")
    print("[B] bag")
    print("[X] Exit")

    choice = input("Enter choice: ").strip().lower()

    if choice in ["z", "q", "s", "d", "n", "w", "e"]:
        player.move(choice, game_map)
        game_loop()
    elif choice == "b":
        print("Opening bag")
        player.use_inventory()
        game_loop()
    elif choice == "p":
        player.pick_up_item()
        game_loop()
    elif choice == "x":
        print("Exiting game")
    else:
        print("Invalid choice")
        game_loop()
