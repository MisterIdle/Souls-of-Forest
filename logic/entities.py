import random
import logic.utils as u
import logic.items as i
import logic.loop as l

class Entity:
    def __init__(self, name, symbol, description, health, max_health, attack, defense, level, gold, inventory, position):
        self.name = name
        self.symbol = symbol
        self.description = description
        self.health = health
        self.max_health = max_health
        self.attack = attack
        self.defense = defense
        self.level = level
        self.gold = gold
        self.inventory = inventory
        self.position = tuple(position)
        self.init_loot()

    def __str__(self):
        return f"{self.name} - {self.description}"
    
    def get_data(self):
        return {
            "name": self.name,
            "symbol": self.symbol,
            "description": self.description,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "level": self.level,
            "gold": self.gold,
            "inventory": [
                item.get_data() for item in self.inventory
            ],
            "position": self.position
        }
                
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def print_stats(self):
        u.print_centered(f"{self.name}")
        print()
        u.print_centered(f"ATK: {self.attack} - DEF: {self.defense} - LVL: {self.level}")
        self.display_health_bar()
        print()

    def display_health_bar(self):
        bar_length = 10
        health_ratio = self.health / self.max_health if self.max_health > 0 else 0
        filled_length = int(bar_length * health_ratio)

        health_bar = "[" + "=" * filled_length + " " * (bar_length - filled_length) + "]"
        
        u.print_centered(f"HP: {health_bar} ({self.health}/{self.max_health})")

    def init_loot(self):
        loot_key = f"loot_{self.name.lower()}"
        loot_data = u.lootable_data.get(loot_key, None)
        if loot_data:
            for item_data in loot_data["items"]:
                item_name = item_data["name"]
                quantity = item_data["quantity"]
                for _ in range(quantity):
                    item_class = i.get_class_from_name(item_name)
                    print(f"Entity {self.name} has loot: {item_name}")
                    item = item_class()
                    self.inventory.append(item)

    def print_inventory(self, show_type=None):
        sorted_inventory = sorted(self.inventory, key=lambda item: (not isinstance(item, i.Weapon), isinstance(item, i.Consumable), item.name))
        print(f"Inventory ({len(self.inventory)}/{self.max_inventory}):")
        for index, item in enumerate(sorted_inventory):
            if show_type is None or isinstance(item, show_type):
                print(f"{index}. {item.name}")
                print(f"   {item.description}")
                print(f"   {item.effect}: {item.value}")
                if isinstance(item, i.Weapon):
                    print(f"   Critical: {item.critical}%")
            print()

    def use_inventory(self):
        u.clear_screen()
        print()
        u.load_ascii_image("bag")
        print("== Bag ==")
        print(f"Gold: {self.gold}")
        self.print_inventory()
        print("[use] [drop] [exit]")
        choice = input("Enter choice: ").strip().lower()
        if choice in ["use", "u"]:
            print("\nSelect the number of the item to use, or type [back]: ")
            choice_use = input("> ").strip()
            if choice_use.isdigit():
                index = int(choice_use)
                if 0 <= index < len(self.inventory):
                    self.use_item(index)
                else:
                    print("Invalid item number")
                    self.use_inventory()
            elif choice_use == "back":
                self.use_inventory()
            else:
                print("Invalid choice")
                self.use_inventory()
        elif choice in ["drop", "d"]:
            print("\nSelect the number(s) of the item(s) to drop (separated by commas), or type [back] to go back")
            choice_drop = input("> ").strip()
            if choice_drop.lower() == "back":
                self.use_inventory()
            else:
                drop_indexes = choice_drop.split(',')
                valid_indexes = []
                for index in drop_indexes:
                    if index.strip().isdigit():
                        valid_indexes.append(int(index.strip()))

                valid_indexes = [index for index in valid_indexes if 0 <= index < len(self.inventory)]
                if valid_indexes:
                    for index in valid_indexes:
                        self.drop_item(index)
                else:
                    print("Invalid item numbers")
                    self.use_inventory()
        elif choice in ["exit", "back"]:
            return
        
    def use_item(self, index, target=None):
        item = self.inventory[index]
        if isinstance(item, i.Weapon):
            if target is None:
                print("No target selected.")
                return
            item.use(self, target)
        elif isinstance(item, i.Consumable):
            item.use(self)
            self.inventory.pop(index)
        else:
            print("Item cannot be used.")
            return

    def die(self):
        print(f"{self.name} has died.")
        if self.position in l.game_map.entities:
            del l.game_map.entities[self.position]


## PLAYERS ##
class Player(Entity):
    def __init__(self, player_data):
        super().__init__(
            player_data["name"], 
            player_data["symbol"], 
            player_data["description"],
            player_data["health"], 
            player_data["max_health"], 
            player_data["attack"], 
            player_data["defense"], 
            player_data["level"], 
            player_data["gold"], 
            player_data["inventory"], 
            player_data["position"],
        )
        self.current_map = player_data["current_map"]
        self.max_inventory = player_data["max_inventory"]
        self.last_position = self.position
        self.experience = 0
        self.next_level = 10

    def __str__(self):
        return f"{self.name} - {self.description}"
    
    def get_data(self):
        return {
            **super().get_data(),
            "max_inventory": self.max_inventory,
            "current_map": self.current_map
        }
    
    # Move
    def move(self, direction, game_map):
        x, y = self.position
        if direction in ["z", "n"]:  # North
            new_position = (x - 1, y)
        elif direction == "s":       # South
            new_position = (x + 1, y)
        elif direction in ["q", "w"]:  # West
            new_position = (x, y - 1)
        elif direction in ["d", "e"]:  # East
            new_position = (x, y + 1)
        else:
            return

        if game_map.is_move_valid(new_position):
            self.last_position = self.position
            self.position = new_position
            print(f"Player moves to {new_position}")
            game_map.check_for_entity_collision(self.position)
            game_map.check_for_teleporter(self.position)
            game_map.check_for_shop(new_position)
        else:
            print("Invalid move, try again.")

    def inventory_full(self):
        print("Inventory is full.")
        u.wait()
        return len(self.inventory) >= self.max_inventory

    def see_items_on_tile(self):
        if self.position in l.game_map.items:
            items = l.game_map.items[self.position]
            u.clear_screen()
            u.load_ascii_image("ground")
            print("Items on the ground:")

            for index, item in enumerate(items):
                print(f"{index}. {item.name}")
                print(f"   {item.description}")
                print(f"   {item.effect}: {item.value}")
                if isinstance(item, i.Weapon):
                    print(f"   Critical: {item.critical}%")
                print()
            choice = input("Select the number(s) of the item(s) to pick up (separated by commas), or type [back] to go back: ").strip().lower()

            if choice == "back":
                return
            else:
                self.pick_up_item(choice)

    # Inventory
    def pick_up_item(self, indices):
        if self.inventory_full():
            return
        
        if isinstance(indices, str):
            try:
                indices = [int(i.strip()) for i in indices.split(',')]
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
                return
            
        elif isinstance(indices, int):
            indices = [indices]

        invalid_indices = [index for index in indices if not (0 <= index < len(l.game_map.items[l.player.position]))]

        if invalid_indices:
            print(f"Invalid indices: {', '.join(map(str, invalid_indices))}. Try again.")
            return
        
        indices.sort(reverse=True)
        for index in indices:
            item = l.game_map.items[l.player.position].pop(index)
            print(f"Player picked up item {item.name}")
            item.position = self.position
            self.inventory.append(item)

    def drop_item(self, indices):
        if isinstance(indices, str):
            try:
                indices = [int(i.strip()) for i in indices.split(',')]
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
                return
        elif isinstance(indices, int):
            indices = [indices]

        invalid_indices = [index for index in indices if not (0 <= index < len(self.inventory))]
        if invalid_indices:
            print(f"Invalid indices: {', '.join(map(str, invalid_indices))}. Try again.")
            return
        
        indices.sort(reverse=True)
        for index in indices:
            item = self.inventory.pop(index)
            print(f"Player dropped item {item.name}")
            item.position = self.position
            l.game_map.drop_item(item)

    def level_up(self):
        self.level += 1
        self.attack += 1
        self.defense += 1
        self.max_health += 5
        self.max_inventory += 2
        self.health = self.max_health
        self.next_level = self.level * 10
        print(f"Player leveled up to level {self.level}.")
        print(f"Player stats: ATK {self.attack} - DEF {self.defense} - HP {self.health}/{self.max_health} - INV {len(self.inventory)}/{self.max_inventory}")
        print(f"Next level at {self.next_level} experience points.")
        self.experience = 0
    
    def win_combat(self, enemy):
        u.clear_screen()
        print(f"{self.name} defeated {enemy.name}!")
        xp_reward = random.randint(enemy.level, enemy.level * 2)
        
        self.experience += xp_reward
        if self.experience >= self.next_level:
            self.level_up()

        self.gold += random.randint(1, enemy.gold)
        print(f"{self.name} gained {xp_reward} experience points and {self.gold} gold.")
        u.wait()

    def xp_to_next_level(self):
        progress_percentage = int((self.experience / self.next_level) * 100)
        progress_bar_length = 10
        filled_length = int(progress_bar_length * progress_percentage / 100)
        progress_bar = "[" + "=" * filled_length + "-" * (progress_bar_length - filled_length) + "]"
        u.print_centered(f"Next level: {progress_bar} {progress_percentage}%")

## ENEMIES ##
class Enemy(Entity):
    def __init__(self, enemy_data):
        super().__init__(
            enemy_data["name"], 
            enemy_data["symbol"], 
            enemy_data["description"],
            enemy_data["health"], 
            enemy_data["max_health"], 
            enemy_data["attack"], 
            enemy_data["defense"], 
            random.randint(enemy_data["level"]["min"], enemy_data["level"]["max"]), 
            enemy_data["gold"], 
            enemy_data["inventory"], 
            enemy_data["position"]
        )

    def __str__(self):
        return f"{self.name} - {self.description}"
    
    def has_consumables(self):
        for item in self.inventory:
            if isinstance(item, i.Consumable):
                return True
        return False
    
class EasySlime(Enemy):
    def __init__(self):
        slime_data = u.entities_data["enemies"]["easy_slime"]
        super().__init__(slime_data)

class Slime(Enemy):
    def __init__(self):
        slime_data = u.entities_data["enemies"]["slime"]
        super().__init__(slime_data)

class Goblin(Enemy):
    def __init__(self):
        goblin_data = u.entities_data["enemies"]["goblin"]
        super().__init__(goblin_data)

def get_class_from_name(class_name):
    return globals()[class_name]
