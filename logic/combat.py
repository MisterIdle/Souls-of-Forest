import logic.items as items
import logic.utils as utils
import logic.loop as loop
import random

# Combat class to handle combat between player and enemy
class Combat:
    def __init__(self, player, enemy, game_map):
        self.player = player
        self.enemy = enemy
        self.game_map = game_map

    # Start combat between player and enemy
    def start_combat(self):
        print(f"Combat started between {self.player.name} and {self.enemy.name}")
        self.combat_loop()

    # Main combat loop
    def combat_loop(self):
        while self.player.health > 0 and self.enemy.health > 0:
            self.player_turn()
            if self.enemy.health <= 0:
                self.player.win_combat(self.enemy)
                break
            
            self.enemy_turn()
            if self.player.health <= 0:
                self.player.game_over()
                break

    # Display header with player and enemy stats
    def header(self):
        utils.clear_screen()
        print()
        utils.load_ascii_image(self.enemy.name, centered=True)
        print()
        self.enemy.print_stats()
        print()
        utils.line()
        print()
        self.player.print_stats()
    
    # Player turn to choose action
    def player_turn(self):
        self.header()
        print("\n== Player turn ==")
        print("Attack [A] | Use item [U] | Run [R]")
        choice = input("Enter choice: ").strip().lower()
        
        if choice in ["attack", "a"]:
            self.execute_attack(self.player, self.enemy)
        elif choice in ["use", "u"]:
            self.execute_use(self.player)
        elif choice in ["run", "r"]:
            if random.randint(1, 100) <= 50:
                print("You ran away successfully.")
                loop.player.position = loop.player.last_position
                utils.wait()
                loop.game_loop()
            else:
                print("You failed to run away.")
        else:
            print("Invalid choice")
            self.player_turn()

    # Execute player attack
    def execute_attack(self, attacker, target):
        weapons = [item for item in attacker.inventory if isinstance(item, items.Weapon)]
        if not weapons:
            damage = attacker.attack / target.defense
            target.take_damage(damage)
            print(f"{attacker.name} attacked {target.name} with their fists and dealt {damage}  damage.")
            return

        for index, weapon in enumerate(weapons):
            print(f"{index}. {weapon.name}")
            print(f"   {weapon.effect}: {weapon.value}")
            print(f"   Crit: {weapon.critical}% chance")
            print()

        try:
            weapon_index = input("Enter weapon number or [back]: ").strip()
            if weapon_index.isdigit() and 0 <= int(weapon_index) < len(weapons):
                attacker.use_item(attacker.inventory.index(weapons[int(weapon_index)]), target)
            elif weapon_index in ["back", "b"]:
                self.player_turn()
            else:
                print("Invalid weapon number")
                self.execute_attack(attacker, target)
        except ValueError:
            print("Invalid input, please enter a valid number.")
            self.execute_attack(attacker, target)

    # Execute player use item  
    def execute_use(self, entity):
        consumables = [item for item in entity.inventory if isinstance(item, items.Consumable)]
        if not consumables:
            print("No consumables in your inventory.")
            self.player_turn()
            return

        for index, consumable in enumerate(consumables):
            print(f"{index}. {consumable.name}")
            print(f"   {consumable.effect}: {consumable.value}")
            print()

        try:
            consumable_index = input("Enter consumable number or [back]: ").strip()
            if consumable_index.isdigit() and 0 <= int(consumable_index) < len(consumables):
                entity.use_item(entity.inventory.index(consumables[int(consumable_index)]))
            elif consumable_index in ["back", "b"]:
                self.player_turn()
            else:
                print("Invalid consumable number")
                self.execute_use(entity)
        except ValueError:
            print("Invalid input, please enter a valid number.")
            self.execute_use(entity)

    # Enemy turn to choose action
    def enemy_turn(self):
        self.header()
        if self.enemy.health <= 0:
            self.player.win_combat(self.enemy)
            utils.clear_screen()
            return

        print("\n== Enemy turn ==")
        if self.enemy.health < self.enemy.max_health / 2:
            self.enemy_use_item()
        else:
            self.enemy_attack()
        utils.wait()

    # Enemy attack player
    def enemy_attack(self):
        weapons = [item for item in self.enemy.inventory if isinstance(item, items.Weapon)]
        if not weapons:
            damage = self.enemy.attack / self.player.defense
            self.player.take_damage(damage)
            print(f"{self.enemy.name} attacked you with their fists and dealt {damage} damage.")
            return
        
        weapon = random.choice(weapons)
        weapon_index = self.enemy.inventory.index(weapon)
        self.enemy.use_item(weapon_index, self.player)

    # Enemy use item
    def enemy_use_item(self):
        consumables = [item for item in self.enemy.inventory if isinstance(item, items.Consumable)]
        if not consumables:
            self.enemy_attack()
            return

        consumable = random.choice(consumables)
        self.enemy.use_item(self.enemy.inventory.index(consumable))
