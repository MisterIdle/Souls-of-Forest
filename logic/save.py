import os
import json
import logic.entities as e
import logic.utils as u
import logic.map as m
import logic.loop as l

class Save:
    def __init__(self, save_directory="saves", key=12345):
        self.save_directory = save_directory
        self.key = key
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def xor_encrypt_decrypt(self, data):
        return ''.join(chr(ord(c) ^ self.key) for c in data)

    def get_save_path(self, save_name):
        if save_name.endswith(".save"):
            save_name = save_name[:-5]
        return os.path.join(self.save_directory, save_name + ".save")

    def save_game(self, explored_maps, player, save_name=None):
        if not save_name:
            save_name = input("Enter save file name: ")
            if not save_name:
                save_name = player.name

        save_path = self.get_save_path(save_name)

        data = {
            "player": player.get_data(),
            "explored_maps": {
                map_name: map_instance.get_data()
                for map_name, map_instance in explored_maps.items()
            }
        }

        json_data = json.dumps(data, indent=4)
        encrypted_data = self.xor_encrypt_decrypt(json_data)

        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(encrypted_data)
        print(f"Game saved as {save_path}")

    def load_game(self, save_name=None):
        if not save_name:
            save_name = input("Enter the save file name to load: ")

        save_path = self.get_save_path(save_name)

        if not os.path.exists(save_path):
            print(f"No save game found with name {save_name}.save")
            return None, None

        return self.load_save(save_name)

    def load_save(self, save_name):
        save_path = self.get_save_path(save_name)

        with open(save_path, 'r', encoding='utf-8') as file:
            encrypted_data = file.read()

        decrypted_data = self.xor_encrypt_decrypt(encrypted_data)
        data = json.loads(decrypted_data)

        m.Map.load_all_maps()
        print("Maps loaded")

        player = e.Player(data["player"])
        print("Player loaded")

        explored_maps = {
            map_name: m.Map(map_data=map_data, tiles_data=u.tiles_data, map_name=map_name)
            for map_name, map_data in data["explored_maps"].items()
        }

        l.game_map = explored_maps[player.current_map]
        print("Maps loaded")

        return explored_maps, player
    
    def delete_save(self, save_name=None):
        if not save_name:
            save_name = input("Enter the save file name to delete: ")

        if save_name.endswith(".save"):
            save_name = save_name[:-5]

        save_path = self.get_save_path(save_name)

        if os.path.exists(save_path):
            os.remove(save_path)
            print(f"Save game {save_name}.save deleted")
        else:
            print(f"No save game found with name {save_name}.save")
    
    def get_save_files(self):
        return [file[:-5] for file in os.listdir(self.save_directory) if file.endswith(".save")]
