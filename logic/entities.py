import random
import logic.utils as u
import logic.map as m
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
                
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def print_stats(self):
        print(f"{self.name} - Level {self.level}")
        print(f"HP: {self.health}/{self.max_health} - ATK: {self.attack} - DEF: {self.defense}")

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
        sorted_inventory = sorted(self.inventory, key=lambda item: (not isinstance(item, i.Weapon), isinstance(item, i.Consumable)))

        for index, item in enumerate(sorted_inventory):
            if show_type is None or isinstance(item, show_type):
                print(f"{index}. {item}")


    def use_inventory(self):
        u.clear_screen()
        u.load_ascii_image("bag")
        print("Bag:")
        self.print_inventory()
        print("[use] [drop] [exit]")
        choice = input("Enter choice: ").strip().lower()
        if choice == "use":
            choice_use = input("Enter item number to use: ").strip()
            if choice_use.isdigit():
                index = int(choice_use)
                if 0 <= index < len(self.inventory):
                    self.use_item(index)
                else:
                    print("Invalid item number")
        elif choice == "drop":
            choice_drop = input("Enter item number to drop: ").strip()
            if choice_drop.isdigit():
                index = int(choice_drop)
                if 0 <= index < len(self.inventory):
                    self.drop_item(index)
                else:
                    print("Invalid item number")
        elif choice == "exit":
            return
        else:
            print("Invalid choice")
            self.use_inventory()

    def use_item(self, index, target=None):
        item = self.inventory[index]
        if isinstance(item, i.Weapon) and target is not None:
            item.use(self, target)
        elif isinstance(item, i.Consumable):
            item.use(self)
            self.inventory.pop(index)

    def die(self):
        l.game_map.remove_entity(self)


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
            player_data["position"]
        )

    def __str__(self):
        return f"{self.name} - {self.description}"

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
            self.position = new_position
            print(f"Player moves to {new_position}")
            game_map.check_for_entity_collision(self.position)
            game_map.check_for_teleporter(self.position)
        else:
            print("Invalid move, try again.")

    def pick_up_item(self):
        if self.position in l.game_map.items and l.game_map.items[self.position]:
            items_at_position = l.game_map.items[self.position]
            print("Items available to pick up:")
            for index, item in enumerate(items_at_position):
                print(f"{index}. {item.name}")

            choice = input("Enter item number to pick up (or 'exit' to cancel): ").strip().lower()
            if choice == "exit":
                return

            if choice.isdigit():
                index = int(choice)
                if 0 <= index < len(items_at_position):
                    item = items_at_position[index]
                    self.inventory.append(item)
                    print(f"Player picked up {item.name}.")
                    l.game_map.pick_up_item(self.position)
                else:
                    print("Invalid item number.")
            else:
                print("Invalid input.")
        else:
            print("No items to pick up here.")


    def drop_item(self, index):
        item = self.inventory.pop(index)
        print(f"Player dropped item {item.name}")
        item.position = self.position 
        l.game_map.drop_item(item)
              
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
