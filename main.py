from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.menu import MDDropdownMenu
# from kivy.core.window import Window
import pymongo

# Window.size = (414, 736)


class MainLayout(Screen):
    pass


class VilLayout(Screen):
    pass


class AccLayout(Screen):
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
        self.table_vil = MDDataTable(
            rows_num=100,
            column_data=[
                ("Player", dp(20)),
                ("ID", dp(10)),
                ("Name", dp(30)),
                ("Points", dp(15)),
                ("Coords", dp(15)),
            ],
            row_data=[
                (
                    i["game_data"]["player"]["name"],
                    i["game_data"]["village"]["id"],
                    i["game_data"]["village"]["name"],
                    i["game_data"]["village"]["points"],
                    f'{i["game_data"]["village"]["x"]}|{i["game_data"]["village"]["y"]}',
                ) for i in villages
            ],
            sorted_on="Name",
            sorted_order="ASC",
        )

        self.table_vil.bind(on_row_press=self.on_row_press)
        self.sm.get_screen("main").ids.screen_vil.add_widget(self.table_vil)


    def press_attack(self):
        self.acc_active = False
        self.vil_active = False
        self.attack_active = True
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

            items_d = ['Snapshot', 'Settings', 'History', 'Logout', 'Exit']
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
            query = row.table.recycle_data[int(start_index+1)]["text"]
            self.vil_data = self.mongo.get_village(int(query))
            self.sm.get_screen("villages").ids.tool_vil.title = str(self.vil_data["game_data"]["village"]["id"])
            self.sm.get_screen("villages").ids.check_build.active = self.vil_data["build"]
            self.sm.get_screen("villages").ids.check_gather.active = self.vil_data["gather"]
            self.sm.get_screen("villages").ids.check_recruit.active = self.vil_data["recruit"]
            self.sm.get_screen("villages").ids.check_crush_wall = self.vil_data["crush_wall"]
            self.sm.get_screen("villages").ids.check_crush_building = self.vil_data["crush_building"]
            self.sm.get_screen("villages").ids.check_farm.active = self.vil_data["farm"]
            self.sm.transition.direction = "left"
            self.sm.current = "villages"

            items_d = ['Bauliste', 'Farmliste', 'Raubzug', 'Farmen']
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
            "FA_template_A": {"heavy": 5},
            "FA_template_B": {"light": 4},
        }
        player = self.sm.get_screen("accounts").ids.tool_acc.title
        self.mongo.update_player(player, structure)


    def save_vil_data(self):
        structure = {
            "build": self.sm.get_screen("villages").ids.check_build.active,
            "recruit": self.sm.get_screen("villages").ids.check_recruit.active,
            "farm": self.sm.get_screen("villages").ids.check_farm.active,
            "gather": self.sm.get_screen("villages").ids.check_gather.active,

        }

        vil_id = int(self.sm.get_screen("villages").ids.tool_vil.title)
        self.mongo.update_village(vil_id, structure)

    def menu_callback(self, text_item):
        self.menu.dismiss()



class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient(
            "mongodb+srv://admin:admin@cluster0.kxi86.mongodb.net/Database?retryWrites=true&w=majority")
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

    def upload_player(self, command_id, data):
        result = self.player.find_one(command_id)
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


if __name__ == '__main__':
    MainApp().run()
