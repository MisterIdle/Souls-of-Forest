import random
import logic.utils as u
import logic.map as m

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
        self.position = position

    def __str__(self):
        return f"{self.name} - {self.description}"

    def take_damage(self, damage):
        self.health -= max(0, damage - self.defense)
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0
    
    def spawn_in_map(self, position, quantity=1):
        for _ in range(quantity):
            self.position = position

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

    def move(self, direction_input, map_obj):
        direction_map = {
            "up": (-1, 0), "z": (-1, 0), "n": (-1, 0), "north": (-1, 0),
            "down": (1, 0), "s": (1, 0), "south": (1, 0),
            "left": (0, -1), "q": (0, -1), "a": (0, -1), "west": (0, -1),
            "right": (0, 1), "d": (0, 1), "east": (0, 1)
        }

        if direction_input in direction_map:
            dx, dy = direction_map[direction_input]
            new_position = (self.position[0] + dx, self.position[1] + dy)

            if map_obj.is_move_valid(new_position):
                entity_at_new_position = next((ent for ent in map_obj.entities if ent.position == new_position), None)
                item_at_new_position = next((item for item in map_obj.items if item.position == new_position), None)

                if entity_at_new_position:
                    u.clear_screen()
                    print(f"Warning: You have encountered a {entity_at_new_position.name}!")
                elif item_at_new_position:
                    print(f"Congratulations: You have found a {item_at_new_position.name}!")
                
                self.position = new_position
                print(f"{self.name} moved {direction_input} to {new_position}.")
            else:
                print(f"Move to {new_position} is blocked.")
        else:
            print(f"Invalid direction '{direction_input}'.")

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
