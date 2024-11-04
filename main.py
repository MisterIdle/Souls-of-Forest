def main():
    print("Welcome to the game!")
    main_menu()

# Main menu

def main_menu():
    print("=== Main Menu ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        new_game()
    elif choice == "2":
        load_game()
    elif choice == "3":
        exit_game()
    else:
        print("Invalid choice. Please try again.")
        main_menu()

def new_game():
    print("Starting new game...")
    gameloop()

def load_game():
    print("Loading game...")
    print("No save files found.")
    main_menu()

def exit_game():
    print("Exiting game...")
    exit()

# Gameloop

def gameloop():
    print("=== Game Loop ===")
    
    print("1. Map")
    print("2. Inventory")

    print("Player position: ", player.getpos())

    print("Move: n (north), s (south), e (east), w (west)")
    choice = input("Enter choice: ")

    if choice in ["n", "s", "e", "w"]:
        player.move(choice)

    show_map()

    gameloop()

# Map

data_map = [
    ["#", "#", "#", "#", "#", "#", "#"],
    ["#", ".", ".", ".", ".", "E", "#"],
    ["#", ".", "#", ".", ".", ".", "#"],
    ["#", ".", ".", ".", "#", ".", "#"],
    ["#", "#", "#", "#", "#", "#", "#"]
]

def show_map():
    map_copy = [row[:] for row in data_map]
    
    px, py = player.getpos()
    
    if 0 <= py < len(map_copy) and 0 <= px < len(map_copy[0]):
        map_copy[py][px] = "@"

    for row in map_copy:
        print(" ".join(row))

# Entity

class Entity:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.attack = 10
        self.defense = 5
        self.x = 1
        self.y = 1

class Player(Entity):
    def __init__(self, name):
        super().__init__(name)

    def move(self, direction):
        if direction == "n" and self.y > 0:
            self.y -= 1
        elif direction == "s" and self.y < len(data_map) - 1:
            self.y += 1
        elif direction == "e" and self.x < len(data_map[0]) - 1:
            self.x += 1
        elif direction == "w" and self.x > 0:
            self.x -= 1

    def getpos(self):
        return self.x, self.y

player = Player("Player")

if __name__ == "__main__":
    main()
