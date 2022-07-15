from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.menu import MDDropdownMenu
import pymongo
import certifi
import dns.resolver

#requirements = python3,kivy,pillow,kivymd,pymongo,certifi,dnspython

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']


class MainLayout(Screen):
    pass


class VilLayout(Screen):
    pass


class AccLayout(Screen):
    pass


class GatherLayout(Screen):
    pass


class FarmAssistLayout(Screen):
    pass


class MainApp(MDApp):
    mongo = None
    sm = None

    table_acc = None
    acc_active = False
    acc_data = {}
    table_vil = None
    vil_active = False
    vil_data = {}
    table_attack = None
    attack_active = False

    menu = None

    def build(self):
        if not self.mongo:
            self.mongo = Mongo()

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"

        self.sm = ScreenManager()
        self.sm.add_widget(MainLayout(name="main"))
        self.sm.add_widget(AccLayout(name="accounts"))
        self.sm.add_widget(VilLayout(name="villages"))
        self.sm.add_widget(GatherLayout(name="gather"))
        self.sm.add_widget(FarmAssistLayout(name="farmassist"))

        self.sm.current = "main"

        return self.sm

    def press_acc(self):
        self.acc_active = True
        self.vil_active = False
        self.attack_active = False

        if self.table_acc:
            self.sm.get_screen("main").ids.screen_acc.remove_widget(self.table_acc)
        accounts = self.mongo.get_all_player()

        for i in accounts:
            if i["status"] == "Online":
                i["status"] = ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1], "Online")
            if i["status"] == "Offline":
                i["status"] = ("alert-circle", [1, 0, 0, 1], "Offline")
            if i["status"] == "Alert":
                i["status"] = ("alert", [255 / 256, 165 / 256, 0, 1], "Bot-Captcha")

        self.table_acc = MDDataTable(
            rows_num=100,
            background_color=(69, 25, 56, 1),
            column_data=[
                ("Player", dp(20)),
                ("Status", dp(20)),
                ("Points", dp(15)),
                ("Villages", dp(15)),
            ],
            row_data=[
                (
                    i["player"],
                    i["status"],
                    i["points"],
                    i["villages"],
                ) for i in accounts

            ],
        )

        self.table_acc.bind(on_row_press=self.on_row_press)
        self.sm.get_screen("main").ids.screen_acc.add_widget(self.table_acc)

    def press_vil(self):
        self.acc_active = False
        self.vil_active = True
        self.attack_active = False

        if self.table_vil:
            self.sm.get_screen("main").ids.screen_vil.remove_widget(self.table_vil)
        villages = self.mongo.get_all_villages()

        for i in villages:
            if i["build"]:
                i["build"] = ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1], "")
            else:
                i["build"] = ("alert-circle", [1, 0, 0, 1], "")
            if i["farm"]:
                i["farm"] = ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1], "")
            else:
                i["farm"] = ("alert-circle", [1, 0, 0, 1], "")
            if i["recruit"]:
                i["recruit"] = ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1], "")
            else:
                i["recruit"] = ("alert-circle", [1, 0, 0, 1], "")
            if i["gather"]:
                i["gather"] = ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1], "")
            else:
                i["gather"] = ("alert-circle", [1, 0, 0, 1], "")

        self.table_vil = MDDataTable(
            rows_num=100,
            column_data=[
                ("Name", dp(15), self.sort_on_name),
                ("ID", dp(10)),
                ("Bauen", dp(15)),
                ("Farmen", dp(15)),
                ("Raubzug", dp(15)),
                ("Rekrut.", dp(15)),
            ],
            row_data=[
                (
                    i["game_data"]["village"]["name"],
                    i["game_data"]["village"]["id"],
                    i["build"],
                    i["farm"],
                    i["gather"],
                    i["recruit"],
                ) for i in villages
            ],
            sorted_on="Name",
            sorted_order="ASC",
        )

        for i in villages:
            if i["build"] == ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1]):
                i["build"] = True
            else:
                i["build"] = False
            if i["farm"] == ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1]):
                i["farm"] = True
            else:
                i["farm"] = False
            if i["recruit"] == ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1]):
                i["recruit"] = True
            else:
                i["recruit"] = False
            if i["gather"] == ("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1]):
                i["gather"] = True
            else:
                i["gather"] = False

        self.table_vil.bind(on_row_press=self.on_row_press)
        self.sm.get_screen("main").ids.screen_vil.add_widget(self.table_vil)

    def sort_on_name(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][-1]))

    def press_attack(self):
        self.acc_active = False
        self.vil_active = False
        self.attack_active = True

        default_temp = {
            "id": 9999,
            "game_data": {
                "village": {
                    "id": 9999,
                    "name": "Vorlage Vil"
                }
            },
            "build": False,
            "recruit": False,
            "farm": True,
            "gather": True,
            "buildorder": [],
            "farmlist": [],
            "crush_wall": True,
            "crush_building": True,
            "gather_units": {
                "spear": True,
                "sword": True,
                "axe": False,
                "archer": True,
                "light": False,
                "marcher": False,
                "heavy": False,
            },
            "hold_back_gather": {
                "spear": 500,
                "sword": 0,
                "axe": 0,
                "archer": 0,
                "light": 0,
                "marcher": 0,
                "heavy": 100,
            },
            "hold_back_farm": {
                "spear": 500,
                "sword": 0,
                "axe": 0,
                "archer": 0,
                "spy": 0,
                "light": 0,
                "marcher": 0,
                "heavy": 100,
                "ram": 0,
                "catapult": 0,
            },
        }

        test_s = {
            "FA_template_A": {
                "spear": 0,
                "sword": 0,
                "axe": 0,
                "archer": 0,
                "spy": 0,
                "light": 10,
                "marcher": 0,
                "heavy": 0,

        },
            "FA_template_B": {
                "spear": 0,
                "sword": 0,
                "axe": 0,
                "archer": 0,
                "spy": 0,
                "light": 0,
                "marcher": 18,
                "heavy": 0,

            }}
        self.mongo.update_player("stoffl2108", test_s)
        pass

    def on_row_press(self, table, row):
        start_index, end_index = row.table.recycle_data[row.index]["range"]
        if self.acc_active:
            query = row.table.recycle_data[int(start_index)]["text"]
            self.acc_data = self.mongo.get_player(query)
            self.sm.get_screen("accounts").ids.tool_acc.title = self.acc_data['player']
            self.sm.get_screen("accounts").ids.slider_apm.value = self.acc_data['apm_cap']
            self.sm.get_screen("accounts").ids.check_build.active = self.acc_data["build"]
            self.sm.get_screen("accounts").ids.check_gather.active = self.acc_data["gather"]
            self.sm.get_screen("accounts").ids.check_recruit.active = self.acc_data["recruit"]
            self.sm.get_screen("accounts").ids.check_farm.active = self.acc_data["farm"]
            self.sm.get_screen("accounts").ids.slider_sleep.value = self.acc_data["sleep"]
            self.sm.get_screen("accounts").ids.slider_farm.value = self.acc_data["timeout_farm"]
            self.sm.get_screen("accounts").ids.slider_scout.value = self.acc_data["timeout_scout"]
            self.sm.get_screen("accounts").ids.slider_ram.value = self.acc_data["timeout_ram"]

            items_d = ['FarmAssist']
            menu_items = [
                {
                    "text": f"{i}",
                    "viewclass": "OneLineListItem",
                    "height": dp(40),
                    "on_release": lambda x=f"{i}": self.menu_callback(x),
                } for i in items_d
            ]
            self.menu = MDDropdownMenu(
                caller=self.sm.get_screen("accounts").ids.tool_acc,
                items=menu_items,
                width_mult=2,
            )

            self.sm.transition.direction = "left"
            self.sm.current = "accounts"

        if self.vil_active:
            query = row.table.recycle_data[int(start_index + 1)]["text"]
            self.vil_data = self.mongo.get_village(int(query))
            self.sm.get_screen("villages").ids.tool_vil.title = str(self.vil_data["game_data"]["village"]["id"])
            self.sm.get_screen("villages").ids.check_build.active = self.vil_data["build"]
            self.sm.get_screen("villages").ids.check_gather.active = self.vil_data["gather"]
            self.sm.get_screen("villages").ids.check_recruit.active = self.vil_data["recruit"]
            self.sm.get_screen("villages").ids.check_crush_wall.active = self.vil_data["crush_wall"]
            self.sm.get_screen("villages").ids.check_crush_building.active = self.vil_data["crush_building"]
            self.sm.get_screen("villages").ids.check_farm.active = self.vil_data["farm"]
            self.sm.transition.direction = "left"
            self.sm.current = "villages"

            items_d = ['Bauliste', 'Farmliste', 'Raubzug']
            menu_items = [
                {
                    "text": f"{i}",
                    "viewclass": "OneLineListItem",
                    "height": dp(40),
                    "on_release": lambda x=f"{i}": self.menu_callback(x),
                } for i in items_d
            ]
            self.menu = MDDropdownMenu(
                caller=self.sm.get_screen("villages").ids.tool_vil,
                items=menu_items,
                width_mult=2,
            )

        if self.attack_active:
            data = None
            # self.sm.switch_to("attacks")

    def save_acc_data(self):
        structure = {
            "build": self.sm.get_screen("accounts").ids.check_build.active,
            "recruit": self.sm.get_screen("accounts").ids.check_recruit.active,
            "farm": self.sm.get_screen("accounts").ids.check_farm.active,
            "gather": self.sm.get_screen("accounts").ids.check_gather.active,
            "sleep": self.sm.get_screen("accounts").ids.slider_sleep.value,
            "apm_cap": self.sm.get_screen("accounts").ids.slider_apm.value,
            "timeout_farm": self.sm.get_screen("accounts").ids.slider_farm.value,
            "timeout_scout": self.sm.get_screen("accounts").ids.slider_scout.value,
            "timeout_ram": self.sm.get_screen("accounts").ids.slider_ram.value,
        }
        player = self.sm.get_screen("accounts").ids.tool_acc.title
        self.mongo.update_player(player, structure)

    def save_vil_data(self):
        structure = {
            "build": self.sm.get_screen("villages").ids.check_build.active,
            "recruit": self.sm.get_screen("villages").ids.check_recruit.active,
            "farm": self.sm.get_screen("villages").ids.check_farm.active,
            "gather": self.sm.get_screen("villages").ids.check_gather.active,
            "crush_wall": self.sm.get_screen("villages").ids.check_crush_wall.active,
            "crush_building": self.sm.get_screen("villages").ids.check_crush_building.active,

        }

        vil_id = int(self.sm.get_screen("villages").ids.tool_vil.title)
        self.mongo.update_village(vil_id, structure)

    def menu_callback(self, text_item):
        self.menu.dismiss()
        if text_item == "Raubzug":
            self.sm.get_screen("gather").ids.tool_gather.title = str(self.vil_data["game_data"]["village"]["id"])

            self.sm.get_screen("gather").ids.check_gather_spear.active = self.vil_data["gather_units"]["spear"]
            self.sm.get_screen("gather").ids.check_gather_sword.active = self.vil_data["gather_units"]["sword"]
            self.sm.get_screen("gather").ids.check_gather_axe.active = self.vil_data["gather_units"]["axe"]
            self.sm.get_screen("gather").ids.check_gather_archer.active = self.vil_data["gather_units"]["archer"]
            self.sm.get_screen("gather").ids.check_gather_marcher.active = self.vil_data["gather_units"]["marcher"]
            self.sm.get_screen("gather").ids.check_gather_light.active = self.vil_data["gather_units"]["light"]
            self.sm.get_screen("gather").ids.check_gather_heavy.active = self.vil_data["gather_units"]["heavy"]

            self.sm.get_screen("gather").ids.input_gather_spear.text = str(self.vil_data["hold_back_gather"]["spear"])
            self.sm.get_screen("gather").ids.input_gather_sword.text = str(self.vil_data["hold_back_gather"]["sword"])
            self.sm.get_screen("gather").ids.input_gather_axe.text = str(self.vil_data["hold_back_gather"]["axe"])
            self.sm.get_screen("gather").ids.input_gather_archer.text = str(self.vil_data["hold_back_gather"]["archer"])
            self.sm.get_screen("gather").ids.input_gather_marcher.text = str(
                self.vil_data["hold_back_gather"]["marcher"])
            self.sm.get_screen("gather").ids.input_gather_light.text = str(self.vil_data["hold_back_gather"]["light"])
            self.sm.get_screen("gather").ids.input_gather_heavy.text = str(self.vil_data["hold_back_gather"]["heavy"])

            self.sm.transition.direction = "up"
            self.sm.current = "gather"

        if text_item == "FarmAssist":


            self.sm.get_screen("farmassist").ids.tool_fa.title = str(self.acc_data['player'])

            self.sm.get_screen("farmassist").ids.input_spear_a.text = str(self.acc_data["FA_template_A"]["spear"])
            self.sm.get_screen("farmassist").ids.input_sword_a.text = str(self.acc_data["FA_template_A"]["sword"])
            self.sm.get_screen("farmassist").ids.input_axe_a.text = str(self.acc_data["FA_template_A"]["axe"])
            self.sm.get_screen("farmassist").ids.input_archer_a.text = str(self.acc_data["FA_template_A"]["archer"])
            self.sm.get_screen("farmassist").ids.input_spy_a.text = str(self.acc_data["FA_template_A"]["spy"])
            self.sm.get_screen("farmassist").ids.input_light_a.text = str(self.acc_data["FA_template_A"]["light"])
            self.sm.get_screen("farmassist").ids.input_marcher_a.text = str(self.acc_data["FA_template_A"]["marcher"])
            self.sm.get_screen("farmassist").ids.input_heavy_a.text = str(self.acc_data["FA_template_A"]["heavy"])

            self.sm.get_screen("farmassist").ids.input_spear_b.text = str(self.acc_data["FA_template_B"]["spear"])
            self.sm.get_screen("farmassist").ids.input_sword_b.text = str(self.acc_data["FA_template_B"]["sword"])
            self.sm.get_screen("farmassist").ids.input_axe_b.text = str(self.acc_data["FA_template_B"]["axe"])
            self.sm.get_screen("farmassist").ids.input_archer_b.text = str(self.acc_data["FA_template_B"]["archer"])
            self.sm.get_screen("farmassist").ids.input_spy_b.text = str(self.acc_data["FA_template_B"]["spy"])
            self.sm.get_screen("farmassist").ids.input_light_b.text = str(self.acc_data["FA_template_B"]["light"])
            self.sm.get_screen("farmassist").ids.input_marcher_b.text = str(self.acc_data["FA_template_B"]["marcher"])
            self.sm.get_screen("farmassist").ids.input_heavy_b.text = str(self.acc_data["FA_template_B"]["heavy"])

            self.sm.transition.direction = "up"
            self.sm.current = "farmassist"

    def save_gather_data(self):
        v_id = self.sm.get_screen("gather").ids.tool_gather.title
        structure = {
            "gather_units": {
                "spear": self.sm.get_screen("gather").ids.check_gather_spear.active,
                "sword": self.sm.get_screen("gather").ids.check_gather_sword.active,
                "axe": self.sm.get_screen("gather").ids.check_gather_axe.active,
                "archer": self.sm.get_screen("gather").ids.check_gather_archer.active,
                "marcher": self.sm.get_screen("gather").ids.check_gather_marcher.active,
                "light": self.sm.get_screen("gather").ids.check_gather_light.active,
                "heavy": self.sm.get_screen("gather").ids.check_gather_heavy.active,
            },
            "hold_back_gather": {
                "spear": self.sm.get_screen("gather").ids.input_gather_spear.text,
                "sword": self.sm.get_screen("gather").ids.input_gather_sword.text,
                "axe": self.sm.get_screen("gather").ids.input_gather_axe.text,
                "archer": self.sm.get_screen("gather").ids.input_gather_archer.text,
                "marcher": self.sm.get_screen("gather").ids.input_gather_marcher.text,
                "light": self.sm.get_screen("gather").ids.input_gather_light.text,
                "heavy": self.sm.get_screen("gather").ids.input_gather_heavy.text,
            }
        }

        self.mongo.update_village(int(v_id), structure)

    def save_farmassist_data(self):
        structure = {
            "FA_template_A": {
                "spear": int(self.sm.get_screen("farmassist").ids.input_spear_a.text),
                "sword": int(self.sm.get_screen("farmassist").ids.input_sword_a.text),
                "axe": int(self.sm.get_screen("farmassist").ids.input_axe_a.text),
                "archer": int(self.sm.get_screen("farmassist").ids.input_archer_a.text),
                "spy": int(self.sm.get_screen("farmassist").ids.input_spy_a.text),
                "light": int(self.sm.get_screen("farmassist").ids.input_light_a.text),
                "marcher": int(self.sm.get_screen("farmassist").ids.input_marcher_a.text),
                "heavy": int(self.sm.get_screen("farmassist").ids.input_heavy_a.text),
            },
            "FA_template_B": {
                "spear": int(self.sm.get_screen("farmassist").ids.input_spear_b.text),
                "sword": int(self.sm.get_screen("farmassist").ids.input_sword_b.text),
                "axe": int(self.sm.get_screen("farmassist").ids.input_axe_b.text),
                "archer": int(self.sm.get_screen("farmassist").ids.input_archer_b.text),
                "spy": int(self.sm.get_screen("farmassist").ids.input_spy_b.text),
                "light": int(self.sm.get_screen("farmassist").ids.input_light_b.text),
                "marcher": int(self.sm.get_screen("farmassist").ids.input_marcher_b.text),
                "heavy": int(self.sm.get_screen("farmassist").ids.input_heavy_b.text),
            }
        }

        player = self.sm.get_screen("farmassist").ids.tool_fa.title
        self.mongo.update_player(player, structure)


class Mongo:
    def __init__(self):
        ca = certifi.where()
        self.client = pymongo.MongoClient(
            "mongodb+srv://admin:admin@cluster0.kxi86.mongodb.net/Database?retryWrites=true&w=majority", tlsCAFILE=ca)
        self.db = self.client.tribalwars
        self.player = self.db.player
        self.own_villages = self.db.own_villages

    def get_all_villages(self):
        villages = []
        for x in self.own_villages.find():
            villages.append(x)
        return villages

    def get_all_player(self):
        player = []
        for x in self.player.find():
            player.append(x)
        return player

    def get_player(self, player):
        find = {"player": player}
        result = self.player.find_one(find)
        return result

    def get_village(self, v_id):
        find = {"id": v_id}
        result = self.own_villages.find_one(find)
        return result

    def upload_player(self, player, data):
        find = {"player": player}
        result = self.player.find_one(find)
        if result:
            return
        else:
            self.player.insert_one(data)

    def update_player(self, player, data):
        query = {"player": player}
        update = {"$set": data}
        self.player.update_one(query, update)

    def update_village(self, v_id, data):
        query = {"id": v_id}
        update = {"$set": data}
        self.own_villages.update_one(query, update)

    def upload_village(self, v_id, data):
        find = {"id": v_id}
        result = self.own_villages.find_one(find)
        if result:
            return
        else:
            self.own_villages.insert_one(data)


if __name__ == '__main__':
    MainApp().run()
