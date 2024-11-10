import random
import logic.utils as u
import logic.map as m

class Item:
    def __init__(self, name, description, value, effect):
        self.name = name
        self.description = description
        self.value = value
        self.effect = effect
        self.position = None

    def __str__(self):
        return f"{self.name} - {self.description}"


class Weapon(Item):
    def __init__(self, weapon_data):
        super().__init__(
            weapon_data["name"], 
            weapon_data["description"], 
            weapon_data["value"],
            weapon_data["effect"]
        )

class Knife(Weapon):
    def __init__(self):
        knife_data = u.items_data["weapons"]["knife"]
        super().__init__(knife_data)

class Sword(Weapon):
    def __init__(self):
        sword_data = u.items_data["weapons"]["sword"]
        super().__init__(sword_data)

## CONSUMABLES ##
class Consumable(Item):
    def __init__(self, consumable_data):
        super().__init__(
            consumable_data["name"], 
            consumable_data["description"], 
            consumable_data["value"],
            consumable_data["effect"]
        )

class HealthPotion(Consumable):
    def __init__(self):
        health_potion_data = u.items_data["consumables"]["health_potion"]
        super().__init__(health_potion_data)

def get_class_from_name(item_name):
    return globals()[item_name]