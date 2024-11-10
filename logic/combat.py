import logic.entities as e
import logic.items as i

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
                break
            
            self.enemy_turn()
            if self.player.health <= 0:
                break

    def player_turn(self):
        self.player.print_stats()
        print("vs")
        self.enemy.print_stats()
        print("Player turn")
        choice = input("Enter choice: [attack] [use] [run] ").strip().lower()
        
        if choice == "attack":
            self.execute_attack(self.player, self.enemy, i.Weapon)
        elif choice == "use":
            self.execute_use(self.player, i.Consumable)
        elif choice == "run":
            print("Player ran away")
            return
        else:
            print("Invalid choice")
            self.player_turn()

    def execute_attack(self, attacker, target, item_type):
        attacker.print_inventory(item_type)
        try:
            weapon_index = int(input("Enter weapon number to use: ").strip())
            if 0 <= weapon_index < len(attacker.inventory):
                weapon = attacker.inventory[weapon_index]
                if isinstance(weapon, item_type):
                    attacker.use_item(weapon_index, target)
                else:
                    print("Selected item is not a weapon.")
            else:
                print("Invalid weapon number")
        except ValueError:
            print("Invalid input")


    def execute_use(self, user, item_type):
        user.print_inventory(item_type)
        try:
            consumable_index = int(input("Enter consumable number to use: ").strip())
            if 0 <= consumable_index < len(user.inventory):
                consumable = user.inventory[consumable_index]
                if isinstance(consumable, item_type):
                    user.use_item(consumable_index)
                else:
                    print("Selected item is not a consumable.")
            else:
                print("Invalid consumable number")
        except ValueError:
            print("Invalid input")

    def enemy_turn(self):
        self.player.print_stats()
        print("vs")
        self.enemy.print_stats()
        if self.enemy.health <= 0:
            return

        print("Enemy turn")
        if self.enemy.health >= self.enemy.max_health * 0.5:
            self.enemy_attack()
        elif self.enemy.health >= self.enemy.max_health * 0.25:
            if self.enemy.has_consumables():
                self.enemy_use_item()
            else:
                self.enemy_attack()

    def enemy_attack(self):
        for index, item in enumerate(self.enemy.inventory):
            if isinstance(item, i.Weapon):
                self.enemy.use_item(index, self.player)
                return
        damage = self.enemy.attack - self.player.defense
        self.player.take_damage(damage)
        print(f"{self.enemy.name} attacked {self.player.name} and dealt {damage} damage.")


    def enemy_use_item(self):
        for item in self.enemy.inventory:
            if isinstance(item, i.Consumable):
                self.enemy.use_item(item)
                return
        print(f"{self.enemy.name} has no consumables to use.")
