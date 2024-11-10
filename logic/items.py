import random
import logic.utils as u
import logic.map as m

class Item:
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value
        self.position = None

    def __str__(self):
        return f"{self.name} - {self.description}"
    
    def use(self, entity):
        pass

## WEAPONS ##
class Weapon(Item):
    def __init__(self, weapon_data):
        super().__init__(
            weapon_data["name"], 
            weapon_data["description"], 
            weapon_data["value"],
        )

    def use(self, entity, target=None):
        if not target:
            print("No target to attack")
            return
        
        miss = random.randint(1, 20) <= 5
        if miss:
            print(f"{entity.name} missed the attack.")
            return
        
        damage = self.value + entity.attack - target.defense
        target.take_damage(damage)
        print(f"{entity.name} attacked {target.name} with {self.name} and dealt {damage} damage.")

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
        )

    def use(self, entity):
        pass

class HealthPotion(Consumable):
    def __init__(self):
        health_potion_data = u.items_data["consumables"]["health_potion"]
        super().__init__(health_potion_data)

    def use(self, entity):
        if entity.health == entity.max_health:
            print("Health is already full")
            return
        entity.health += self.value
        if entity.health > entity.max_health:
            entity.health = entity.max_health
        print(f"{entity.name} used {self.name} and recovered {self.value} health.")

def get_class_from_name(item_name):
    return globals()[item_name]