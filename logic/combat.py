import random

## COMBAT ##
class CombatManager:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def start_combat(self):
        print(f"A battle has started between {self.player.name} and {self.enemy.name}!\n")
        while self.player.health > 0 and self.enemy.health > 0:
            self.player_turn()
            if self.enemy.health <= 0:
                print(f"{self.enemy.name} has been defeated!")
                self.enemy.die()
                break

            self.enemy_turn()
            if self.player.health <= 0:
                print(f"{self.player.name} has been defeated!")
                self.player.die()
                break

    def display_health(self):
        print(f"{self.player.name} - Health: {self.player.health}")
        print(f"{self.enemy.name} - Health: {self.enemy.health}\n")

    def player_turn(self):
        from logic.items import Weapon, Consumable
        self.display_health()
        print("Choose an action:")
        print("[1] Attack")
        print("[2] Use a consumable")
        print("[3] Run away")
        choice = input("> ")
        if choice == "1":
            print("Choose your weapon:")
            weapons = [item for item in self.player.inventory if isinstance(item, Weapon)]
            for index, item in enumerate(weapons, 1):
                print(f"{index}. {item.name} - Damage: {item.damage}")  

            weapon_choice = input("Select weapon number: ") 

            if weapon_choice.isdigit():
                weapon_choice = int(weapon_choice) - 1
                if 0 <= weapon_choice < len(weapons):
                    weapon = weapons[weapon_choice]
                    weapon.use(self.player, self.enemy)
                else:
                    print("Invalid weapon choice! Please enter a valid number.")
                    self.player_turn()
            else:
                print("Please enter a valid number.")
                self.player_turn()
        elif choice == "2":
            print("Choose a consumable:")
            consumables = [item for item in self.player.inventory if isinstance(item, Consumable)]

            for index, item in enumerate(consumables, 1):
                print(f"{index}. {item.name} - {item.description}")

            consumable_choice = input("Select consumable number: ")
            if consumable_choice.isdigit():
                consumable_choice = int(consumable_choice) - 1
                if 0 <= consumable_choice < len(consumables):
                    consumable = consumables[consumable_choice]
                    consumable.use(self.player)
                    self.player.remove_item(consumable)
                else:
                    print("Invalid consumable choice! Please enter a valid number.")
                    self.player_turn()
            else:
                print("Please enter a valid number.")
                self.player_turn()
                
        elif choice == "3":
            from logic.gameloop import game_map, game_loop
            run_chance = random.randint(1, 100) <= 70
            if run_chance:
                print("You run away from the battle!")
                directions = ["z", "q", "s", "d"]
                random_direction = random.choice(directions)
                self.player.move(random_direction, game_map)
                game_loop()
            else:
                print("You failed to run away!")
                self.enemy_turn()
        else:
            print("Invalid choice!")
            self.player_turn()

    def enemy_turn(self):
        self.display_health()
        from logic.items import Weapon, Consumable
        consumables = [item for item in self.enemy.inventory if isinstance(item, Consumable)]
        if consumables:
            consumable = random.choice(consumables)
            consumable.use(self.enemy)
            self.enemy.remove_item(consumable)
        else:
            weapons = [item for item in self.enemy.inventory if isinstance(item, Weapon)]
            if weapons:
                weapon = random.choice(weapons)
                weapon.use(self.enemy, self.player)
            else:
                print(f"{self.enemy.name} has no weapons or consumables to use!")
                print(f"{self.enemy.name} skips their turn.")