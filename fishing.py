import minescript, re, time, random

axe_list = {
    "VENATOR_GENESIS",
    "SILVA_DOMINUS",
    "CURSUS_FERAE",
    "APEX_PREDATOR",
    "NEX_TITANUM",
    "FIGSTONE_AXE"
}

rod_list = {
    "STARTER_LAVA_ROD",
    "POLISHED_TOPAZ_ROD",
    "MAGMA_ROD",
    "INFERNO_ROD",
    "HELLFIRE_ROD"
}

minescript.echo("Script Started")


class Manager:
    def __init__(self):
        self.hasHooked = False
        self.found = False
        self.fishing_start_time = None
        self.fishing_duration = random.uniform(116, 140) # Random duration between 116 and 140 seconds

    def get_inventory(self):
        """Returns a list of (sb_id, item) tuples from inventory"""
        inv = minescript.player_inventory()
        result = []

        for item in inv:
            raw = str(item.nbt)
            match = re.search(r'id:"([^"]+)"', raw)
            if match:
                sb_id = match.group(1)
            else:
                sb_id = None
            result.append((sb_id, item))
        return result

    def get_hand(self):
        """Returns the sb_id of the item in main hand"""
        hand_raw = minescript.player_hand_items()  # gibt scheinbar einen String zurück

        if not hand_raw:
            return None

        # Suche direkt den id-Wert innerhalb des Strings
        match = re.search(r'id:"([^"]+)"', str(hand_raw))
        if match:
            return match.group(1)
        return None

    def switch_to_axe(self):
        """Switches to huntaxe if found in hotbar"""
        if self.get_hand() in axe_list:
            return  # Already holding an axe
        
        self.found = False
        for sb_id, item in self.get_inventory():
            if sb_id in axe_list and not self.found:
                if item.slot <= 8:
                    minescript.echo(f"Huntaxe found in hotbar slot {item.slot}, switching to it.")
                    minescript.player_inventory_select_slot(item.slot)
                else:
                    minescript.echo(f"Huntaxe found in inventory. It has to be moved to hotbar manually.")

                self.found = True

        if not self.found:
            minescript.echo("No axe in inventory found!")

    def switch_to_rod(self):
        """Switches to lava fishing rod if found in hotbar"""
        if self.get_hand() in rod_list:
            return  # Already holding a rod

        self.found = False
        for sb_id, item in self.get_inventory():
            if sb_id in rod_list and not self.found:
                if item.slot <= 8:
                    minescript.echo(f"Lava rod found in hotbar slot {item.slot}, switching to it.")
                    minescript.player_inventory_select_slot(item.slot)
                else:
                    minescript.echo(f"Lava rod found in inventory. It has to be moved to hotbar manually.")

                self.found = True
                
        if not self.found:
            minescript.echo("No lava rod in inventory found!")

    def click(self, click):
        """Clicks the mouse button"""
        actions = {
            "left": minescript.player_press_attack,
            "right": minescript.player_press_use
        }

        action_func = actions.get(click)
        if action_func is None:
            raise ValueError(f"Unknown click type: {click}")
        
        action_func(True)
        time.sleep(random.uniform(0.05, 0.1))
        action_func(False)
        time.sleep(random.uniform(0.1, 0.2))

    def search_entities(self):
        """Searches for armor stands named "!!!" (Fish indicator)"""
        entities = minescript.entities(max_distance=6)
        for e in entities:
            if e.type == ("entity.minecraft.armor_stand") and e.name == ("!!!"):
                # print(f"Name: {e.name}, Type: {e.type}")
                self.hasHooked = True
                break

    def search_striders(self):
        """Searches for striders to attack"""
        entity = minescript.player_get_targeted_entity()
        if entity and getattr(entity, "type", None) == "entity.minecraft.strider":
            return True
        return False

    def stop_fishing(self):
        """Stops fishing process after duration"""
        if self.fishing_start_time is None:
            return False
        return time.time() - self.fishing_start_time >= self.fishing_duration


    def fish(self):
        """Start the whole fishing process"""
        self.switch_to_rod()
        self.click("right")  # Cast the rod

        while True:
            self.search_entities()
            if self.hasHooked:
                break

            if self.stop_fishing():
                return False

            time.sleep(0.1)  # Wait before checking again        

        self.click("right")  # Reel in the fish
        time.sleep(random.uniform(0.15, 0.3))  # Simulate time taken to reel in
        self.hasHooked = False # Reset for next cast
        return True
    
    def attack(self):
        """Attack with the axe"""
        minescript.echo("Started killing Strider...")
        self.switch_to_axe()
        time.sleep(0.2)  # Small delay to ensure axe is switched
        self.click("right") # Buff with the axe
        time.sleep(0.1)  # Small delay 
        while self.search_striders():
            self.click("left")
        time.sleep(0.3)  # Small delay to ensure all striders are killed
        minescript.echo("Killed all Striders in range.")

    def start_fishing_cycle(self):
        """Start fishing again"""
        minescript.echo("Starting fishing cycle...")
        self.fishing_start_time = time.time()
        
        while not self.stop_fishing():
            continue_fishing = self.fish()
            if not continue_fishing:
                break

        minescript.echo("Fishing cycle completed!")

    def run(self):
        """Main loop to alternate between fishing and attacking"""
        while True:
            self.start_fishing_cycle()
            self.attack()

manager = Manager()

manager.run()
