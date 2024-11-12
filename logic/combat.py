import logic.items as i
import logic.utils as u
import logic.loop as l
import random

class Combat:
    def __init__(self, player, enemy, game_map, player_last_position):
        self.player = player
        self.enemy = enemy
        self.game_map = game_map
        self.player_last_position = player_last_position

    def start_combat(self):
        print(f"Combat started between {self.player.name} and {self.enemy.name}")
        self.combat_loop()

    def combat_loop(self):
        while self.player.health > 0 and self.enemy.health > 0:
            self.player_turn()
            if self.enemy.health <= 0:
                self.player.win_combat(self.enemy)
                self.enemy.die()
                break
            
            self.enemy_turn()
            if self.player.health <= 0:
                self.enemy.win_combat(self.player)
                self.player.die()
                break

    def header(self):
        u.clear_screen()
        u.load_ascii_image(self.enemy.name)
        self.enemy.print_stats()
        print("=" * 20)
        self.player.print_stats()
    
    def player_turn(self):
        self.header()
        print("\n== Player turn ==")
        print("Attack [A] | Use item [U] | Run [R]")
        choice = input("> ").strip().lower()
        
        if choice in ["attack", "a"]:
            self.execute_attack(self.player, self.enemy)
        elif choice in ["use", "u"]:
            self.execute_use(self.player)
        elif choice in ["run", "r"]:
            if random.randint(1, 100) <= 50:
                print("You ran away successfully.")
                self.player.position = self.player_last_position
                l.game_loop()
            else:
                print("You failed to run away.")
            u.wait()
        else:
            print("Invalid choice")
            self.player_turn()

    def execute_attack(self, attacker, target):
        weapons = [item for item in attacker.inventory if isinstance(item, i.Weapon)]
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
            
    def execute_use(self, entity):
        consumables = [item for item in entity.inventory if isinstance(item, i.Consumable)]
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

    def enemy_turn(self):
        u.wait()
        self.header()
        if self.enemy.health <= 0:
            self.player.win_combat(self.enemy.name)

        print("\n== Enemy turn ==")
        if self.enemy.health >= self.enemy.max_health * 0.5:
            self.enemy_attack()
        elif self.enemy.health >= self.enemy.max_health * 0.25:
            if self.enemy.has_consumables():
                self.enemy_use_item()
            else:
                self.enemy_attack()
        u.wait()

    def enemy_attack(self):
        for index, item in enumerate(self.enemy.inventory):
            if isinstance(item, i.Weapon):
                self.enemy.use_item(index, self.player)
                return
            
        damage = self.enemy.attack / self.player.defense
        self.player.take_damage(damage)
        print(f"{self.enemy.name} attacked {self.player.name} and dealt {damage} damage.")


    def enemy_use_item(self):
        for index, item in enumerate(self.enemy.inventory):
            if isinstance(item, i.Consumable):
                self.enemy.use_item(index)
                return
            else:
                self.enemy_attack()
                return
