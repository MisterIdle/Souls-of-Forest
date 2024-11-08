from logic.utils import items_data
import random

## ITEMS ##
class Item:
    def __init__(self, data, position=(0, 0)):
        self.name = data["name"]
        self.description = data["description"]
        self.position = position

## WEAPONS ##
class Weapon(Item):
    def __init__(self, data, position=(0, 0)):
        super().__init__(data)
        self.damage = data["damage"]
        self.position = position

    def use(self, entity, target):
        from logic.entities import Entity
        if not isinstance(target, Entity):
            print("Invalid target!")
            return
        
        miss_chance = random.randint(1, 100) <= 10
        if miss_chance:
            print(f"{entity.name}'s attack missed!")
            return
        
        defense_factor = random.uniform(0.5, 1.0) * target.defense
        adjusted_damage = self.damage - defense_factor

        adjusted_damage = max(adjusted_damage, 1)

        target.health -= adjusted_damage
        print(f"{entity.name} attacked {target.name} with {self.name} for {adjusted_damage} damage.")

class Hand(Weapon):
    def __init__(self):
        hand_data = items_data["weapons"]["hand"]
        super().__init__(hand_data)

class Sword(Weapon):
    def __init__(self):
        sword_data = items_data["weapons"]["sword"]
        super().__init__(sword_data)

## CONSUMABLES ##
class Consumable(Item):
    def __init__(self, data):
        super().__init__(data)
        self.effect = data["effect"]
        self.amount = data["amount"]

    def use(self, entity):
        effect = self.effect
        entity.effect(effect, self.amount)

class HealthPotion(Consumable):
    def __init__(self):
        health_potion_data = items_data["consumables"]["health_potion"]
        super().__init__(health_potion_data)

class DefensePotion(Consumable):
    def __init__(self):
        defense_potion_data = items_data["consumables"]["defense_potion"]
        super().__init__(defense_potion_data)