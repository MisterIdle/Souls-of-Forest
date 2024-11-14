import random
import logic.utils as u

## ITEM CLASS ##
class Item:
    def __init__(self, name, description, value, effect):
        self.name = name
        self.description = description
        self.value = value
        self.effect = effect
        self.position = None
    
    # Get item data
    def get_data(self):
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "effect": self.effect,
            "position": self.position
        }
    
    # Use item
    def use(self, entity):
        pass

## WEAPONS ##
class Weapon(Item):
    def __init__(self, weapon_data):
        super().__init__(
            weapon_data["name"],
            weapon_data["description"],
            weapon_data["value"],
            weapon_data["effect"]
        )

        self.critical = weapon_data["critical"]

    # Use weapon to attack, if attack has a chance to miss, critical hit, or deal extra damage
    def use(self, entity, target=None):
        if not target:
            print("No target to attack")
            return
        
        miss = random.randint(1, 100) <= 10
        if miss:
            print(f"{entity.name} missed the attack.")
            return
        
        critical = random.randint(1, 100) <= self.critical
        damage = entity.attack + self.value / target.defense
        if critical:
            damage *= 2
            print("Critical hit!")

        damage = round(damage, 2)

        target.take_damage(damage)
        print(f"{entity.name} attacked {target.name} with {self.name} and dealt {damage} damage.")

## WEAPONS ##
class Knife(Weapon):
    def __init__(self):
        knife_data = u.items_data["weapons"]["knife"]
        super().__init__(knife_data)

class Sword(Weapon):
    def __init__(self):
        sword_data = u.items_data["weapons"]["sword"]
        super().__init__(sword_data)

class Axe(Weapon):
    def __init__(self):
        axe_data = u.items_data["weapons"]["axe"]
        super().__init__(axe_data)

class DragonSlayer(Weapon):
    def __init__(self):
        dragon_slayer_data = u.items_data["weapons"]["dragonslayer"]
        super().__init__(dragon_slayer_data)

## CONSUMABLES ##
class Consumable(Item):
    def __init__(self, consumable_data):
        super().__init__(
            consumable_data["name"], 
            consumable_data["description"], 
            consumable_data["value"],
            consumable_data["effect"]
        )

    def use(self, entity):
        pass

## POTIONS ##
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

class BigHealthPotion(Consumable):
    def __init__(self):
        big_health_potion_data = u.items_data["consumables"]["big_health_potion"]
        super().__init__(big_health_potion_data)

    def use(self, entity):
        if entity.health == entity.max_health:
            print("Health is already full")
            return
        entity.health += self.value
        if entity.health > entity.max_health:
            entity.health = entity.max_health
        print(f"{entity.name} used {self.name} and recovered {self.value} health.")

class AttackPotion(Consumable):
    def __init__(self):
        strength_potion_data = u.items_data["consumables"]["attack_potion"]
        super().__init__(strength_potion_data)

    def use(self, entity):
        entity.attack += self.value
        print(f"{entity.name} used {self.name} and increased attack by {self.value}.")

class DefensePotion(Consumable):
    def __init__(self):
        defense_potion_data = u.items_data["consumables"]["defense_potion"]
        super().__init__(defense_potion_data)

    def use(self, entity):
        entity.defense += self.value
        print(f"{entity.name} used {self.name} and increased defense by {self.value}.")

# Get specific item class from name
def get_class_from_name(item_name):
    return globals()[item_name]
