import logic.utils as u
import logic.items as i
import logic.loop as l

# Shop class to handle shop interactions
class Shop:
    def __init__(self, shop_data):
        self.shop_data = shop_data
        self.items = []
        self.init_loot()

    # Initialize shop items
    def init_loot(self):
        for item in self.shop_data["items"]:
            name_item = item["name"]
            item_class = i.get_class_from_name(name_item)
            self.items.append(item_class())

    # Display shop header
    def display_shop_header(self):
        u.clear_screen()
        u.load_ascii_image("shop")
        print(f"=== Shop: {self.shop_data['name']} ===")
        print(f"Gold: {l.player.gold}")
        print(f"Bag: {len(l.player.inventory)}/{l.player.max_inventory}")

    # Print shop items
    def print_items(self):
        self.display_shop_header()
        for index, item in enumerate(self.items):
            print(f"{index + 1}. {item.name}")
            print(f"   {item.effect}: {item.value}")
            if isinstance(item, i.Weapon):
                print(f"   Critical: {item.critical}%")
            print(f"   Buy: {item.value} / Sell: {item.value // 2} gold")
            print()

    # Prompt player choice
    def prompt_choice(self):
        print("[buy] [sell] [bag] [exit]")
        return input("Enter choice: ").lower()
    
    # Open shop
    def open_shop(self):
        while True:
            self.print_items()
            choice = self.prompt_choice()

            if choice in ["buy", "b"]:
                self.handle_buy()
            elif choice in ["sell", "s"]:
                self.handle_sell()
            elif choice in ["bag", "inventory", "i"]:
                l.player.print_inventory()
                u.wait()
            elif choice in ["exit", "back"]:
                break
            else:
                print("Invalid choice.")
                u.wait()

    # Handle buy item
    def handle_buy(self):
        choice_buy = input("Enter the number of the item you want to buy: ")
        if choice_buy.isdigit():
            item_index = int(choice_buy) - 1
            if 0 <= item_index < len(self.items):
                item = self.items[item_index]
                confirm = input(f"Buy {item.name} for {item.value} gold? [y/n]: ").lower()
                if confirm == "y":
                    self.buy_item(l.player, item_index)
                else:
                    print("Transaction cancelled.")
            else:
                print("Invalid item number.")
        else:
            print("Please enter a valid number.")
        u.wait()

    # Handle sell item
    def handle_sell(self):
        l.player.print_inventory()
        choice_sell = input("Enter the number of the item you want to sell: ")
        if choice_sell.isdigit():
            item_index = int(choice_sell) - 1
            if 0 <= item_index < len(l.player.inventory):
                item = l.player.inventory[item_index]
                confirm = input(f"Sell {item.name} for {item.value // 2} gold? [y/n]: ").lower()
                if confirm == "y":
                    self.sell_item(l.player, item_index)
                else:
                    print("Transaction cancelled.")
            else:
                print("Invalid item number.")
        else:
            print("Please enter a valid number.")
        u.wait()

    # Buy item
    def buy_item(self, entity, item_index):
        item = self.items[item_index]
        if entity.inventory_full():
            print("Inventory full.")
        elif entity.gold < item.value:
            print("Not enough gold.")
        else:
            entity.gold -= item.value
            entity.inventory.append(item)
            print(f"{entity.name} bought {item.name} for {item.value} gold.")
        u.wait()

    # Sell item
    def sell_item(self, entity, item_index):
        item = entity.inventory[item_index]
        sell_value = item.value // 2
        entity.gold += sell_value
        entity.inventory.pop(item_index)
        print(f"{entity.name} sold {item.name} for {sell_value} gold.")
        u.wait()
