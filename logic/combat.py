import logic.items as i
import logic.utils as u
import random

class Combat:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

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
            run_chance = random.randint(1, 100) <= 70
            if run_chance:
                print("You ran away successfully.")
                self.player.position = (self.enemy.position[0] + random.randint(-1, 1), self.enemy.position[1] + random.randint(-1, 1))
                return
        else:
            print("Invalid choice")
            self.player_turn()

    def execute_attack(self, attacker, target):
        weapons = [item for item in attacker.inventory if isinstance(item, i.Weapon)]
        if not weapons:
            damage = attacker.attack / target.defense
            target.take_damage(damage)
            print(f"{attacker.name} attacked {target.name} with their fists and dealt {damage} damage.")
            return

        for index, weapon in enumerate(weapons):
            print(f"{index}. {weapon.name}")

        try:
            weapon_index = int(input("Enter weapon number to attack: ").strip())
            if 0 <= weapon_index < len(weapons):
                selected_weapon = weapons[weapon_index]
                attacker.use_item(attacker.inventory.index(selected_weapon), target)
            else:
                print("Invalid weapon number")
                self.execute_attack(attacker, target)
        except ValueError:
            print("Invalid input, please enter a valid number.")

    def execute_use(self, entity):
        consumables = [item for item in entity.inventory if isinstance(item, i.Consumable)]
        if not consumables:
            print("No consumables available in your inventory.")
            return

        for index, consumable in enumerate(consumables):
            print(f"{index}. {consumable.name}")

        try:
            consumable_index = int(input("Enter consumable number to use: ").strip())
            if 0 <= consumable_index < len(consumables):
                entity.use_item(entity.inventory.index(consumables[consumable_index]))
            else:
                print("Invalid consumable number")
                self.execute_use(entity)
        except ValueError:
            print("Invalid input, please enter a valid number.")

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
