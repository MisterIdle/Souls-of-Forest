import logic.utils as u
import logic.items as i
import logic.loop as l

class Shop:
    def __init__(self, shop_data):
        self.shop_data = shop_data
        self.items = []
        self.init_loot()

    def init_loot(self):
        for item in self.shop_data["items"]:
            name_item = item["name"]
            item_class = i.get_class_from_name(name_item)
            item_instance = item_class()
            self.items.append(item_instance)

    def print_items(self):
        u.clear_screen()
        u.load_ascii_image("shop")
        print(f"=== Shop: {self.shop_data['name']} ===")
        print(f"Gold: {l.player.gold}")
        print(f"Bag: {len(l.player.inventory)}/{l.player.max_inventory}")
        for index, item in enumerate(self.items):
            print(f"{index + 1}. {item}")
            print(f"   {item.effect}: {item.value}")
            if isinstance(item, i.Weapon):
                print(f"   Critical: {item.critical}%")
            print(f"   Buy: {item.value} / Sell: {item.value // 2} gold")
            print()

    def open_shop(self):
        self.print_items()
        print("[buy] [sell] [bag] [exit]")
        choice = input("Enter choice: ")

        if choice in ["buy", "b"]:
            choice_buy = input("Enter the number of the item you want to buy: ")
            if choice_buy.isdigit():
                choice_buy = int(choice_buy) - 1
                if 0 <= choice_buy < len(self.items):
                    confirm = input(f"Buy {self.items[choice_buy].name} for {self.items[choice_buy].value} gold? [y/n]: ")
                    if confirm.lower() == "y":
                        self.buy_item(l.player, choice_buy)
                        u.wait()
                    else:
                        print("Transaction cancelled.")
                        u.wait()
                else:
                    print("Invalid item number.")
                    u.wait()
            
        elif choice in ["sell", "s"]:
            choice_sell = input("Enter the number of the item you want to sell: ")

            if choice_sell.isdigit():
                choice_sell = int(choice_sell) - 1
                if 0 <= choice_sell < len(l.player.inventory):
                    confirm = input(f"Sell {l.player.inventory[choice_sell].name} for {l.player.inventory[choice_sell].value // 2} gold? [y/n]: ")
                    if confirm.lower() == "y":
                        self.sell_item(l.player, choice_sell)
                        u.wait()
                    else:
                        print("Transaction cancelled.")
                        u.wait()
                else:
                    print("Invalid item number.")
                    u.wait()

        elif choice in ["bag", "inventory", "i"]:
            print()
            print("=== Inventory ===")
            l.player.print_inventory()
            u.wait()

        elif choice in ["exit", "back"]:
            return
        
        self.open_shop()

    def buy_item(self, entity, item_index):
        # Check if inventory is full
        if entity.inventory_full():
            self.open_shop()

        item = self.items[item_index]
        if entity.gold < item.value:
            print("Not enough gold.")
            u.wait()
            return
        entity.gold -= item.value
        entity.inventory.append(item)
        print(f"{entity.name} bought {item.name} for {item.value} gold.")
        u.wait()

    def sell_item(self, entity, item_index):
        item = entity.inventory[item_index]
        sell_value = item.value // 2
        entity.gold += sell_value
        print(f"{entity.name} sold {item.name} for {sell_value} gold.")