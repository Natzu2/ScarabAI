import json
import dearpygui.dearpygui as dpg
import hashlib
import sys
import time
from utils.popUp import popUp
from utils import Theme

notice = popUp()
themes = Theme()
class AccessPassword:
    def __init__(self, detection) -> None:
        self.detection = detection

    def access(self, input):
        with open("data/GestureSettings.json") as jsonfile:
            self.settings = json.load(jsonfile)
            self.globalSettings = self.settings.get("GlobalSettings")
        password = self.globalSettings["password"]
        if hashlib.md5(input.encode('utf-8')).hexdigest() == password:
            return True
        else:
            return False
    
    def savePass(self):
        with open("data/GestureSettings.json") as jsonfile:
            self.settings = json.load(jsonfile)
            self.globalSettings = self.settings.get("GlobalSettings")
        password = dpg.get_value("currentpassword")
        newpassword =dpg.get_value("newpassword")
        if self.access(password):
            value = hashlib.md5(newpassword.encode('utf-8')).hexdigest()
            self.globalSettings["password"] = value
            self.settings["GlobalSettings"] = self.globalSettings
            try:
                with open("data/GestureSettings.json", "w") as jsonFile:
                    json.dump(self.settings, jsonFile)
                    message = "Password Reset Successfully!!!"
                
            except Exception:
                print(Exception)
                message = "Failed at password reset"
        else:
            message = "Please insert current password correctly"
        
        dpg.delete_item("resetWindow")
        notice.show_info("Notice", message, 470)

    def changePass(self):
        with dpg.window(label="Reset Password", no_resize=True, tag="resetWindow",no_close=True, width=270, pos=(350,300)):
            dpg.add_text("Enter current password")
            dpg.add_input_text(tag="currentpassword", password=True)
            dpg.add_text("Enter new password")
            dpg.add_input_text(tag="newpassword", password= True)
            dpg.add_button(label="Confirm", callback=self.savePass)
        notice.centered_popup("resetWindow")
        dpg.bind_item_theme("resetWindow", themes.getPopUpTheme())

    def PasswordConfirm(self):
        if self.access(dpg.get_value("pass")):
            dpg.set_value("statusPass","Success!!!")
            time.sleep(1)
            dpg.delete_item("passFace")
        else:
            dpg.set_value("statusPass","Wrong Password!")
            dpg.configure_item("statusPass", color=(255,0,0,255))
            time.sleep(2)
            dpg.set_value("statusPass","")
            dpg.configure_item("statusPass", color=(0,0,0,255))
    def collapse(self):
        dpg.set_value("tabBar", "Gest")
        dpg.delete_item("passFace")
        self.detection.switch = "Gesture"

    def view(self):
        with dpg.window(label="Verification needed", tag="passFace", modal=True, pos=(380, 280), width=300, no_resize=True, no_close=True):
            dpg.add_input_text(tag="pass", password=True, hint="Password", width=235, callback=self.PasswordConfirm, on_enter= True)
            dpg.add_text(default_value="",tag="statusPass")
            dpg.add_separator()
            with dpg.group(horizontal=True, horizontal_spacing=15):
                dpg.add_button(label="Confirm", callback=self.PasswordConfirm)
                dpg.add_button(label="Cancel", callback=self.collapse)
            notice.centered_popup("passFace")
        dpg.bind_item_theme("passFace", themes.getPopUpTheme())