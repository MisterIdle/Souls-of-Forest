import random
import logic.utils as u
import logic.map as m
import logic.items as i

player = None

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
        self.health -= max(0, damage - self.defense)
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

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

class Player(Entity):
    def __init__(self, player_data):
        super().__init__(
            player_data["name"], 
            player_data["symbol"], 
            player_data["description"],
            player_data["health"], 
            player_data["maxHealth"], 
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
            game_map.check_for_item_collision(self.position)

            game_map.display(new_position)
        else:
            print("Invalid move, try again.")

    def print_inventory(self):
        print("Inventory:")
        for item in self.inventory:
            print(f"  {item}")

class Enemy(Entity):
    def __init__(self, enemy_data):
        super().__init__(
            enemy_data["name"], 
            enemy_data["symbol"], 
            enemy_data["description"],
            enemy_data["health"], 
            enemy_data["maxHealth"], 
            enemy_data["attack"], 
            enemy_data["defense"], 
            random.randint(enemy_data["level"]["min"], enemy_data["level"]["max"]), 
            enemy_data["gold"], 
            enemy_data["inventory"], 
            enemy_data["position"]
        )

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
