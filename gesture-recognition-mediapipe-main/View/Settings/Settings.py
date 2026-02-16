from dearpygui.dearpygui import *
from View.Settings.PasswordAccess import AccessPassword
from utils import History
from utils import popUp
import json
import time
from utils import Theme

themes =  Theme()
popups = popUp()

class Settings:
    def __init__(self, detection):
        self.detection = detection
        self.history = History()
        self.access= AccessPassword(detection=detection)
    def View(self, objParent):
        def loadTable():
            with window(label="History", width=720, height=320, no_resize=True, pos=(100,200), modal=True, no_move=True):
                bind_item_theme(last_item(),themes.getPopUpTheme())
                with table(header_row=False,borders_innerH=True):
                    add_table_column()
                    for row in self.history.getHistoryArray():
                        with table_row():
                            add_text(row)

                            
        
        def CamChange():
            if(get_value("camSelector") != "Select a camera"):
                cameraList = self.detection.GetListOfCameras()
                self.detection.changeCam(list(cameraList.keys())[list(cameraList.values()).index(get_value("camSelector"))])
                print(get_value("camSelector"))
            
        def reloadCamList():
            configure_item("camSelector", items=list(self.detection.GetListOfCameras().values()))
            set_value("camSelector", "Select a camera")
        
        def changePassword():
            self.access.changePass()

        def compareChanges(plc_info, times):
            result = True
            with open("data/GestureSettings.json") as jsonfile:
                settings = json.load(jsonfile)
                plc_json = settings.get("plc_info")
                times_json = settings.get("GlobalSettings")
                if plc_info == plc_json and times == times_json:
                    result = False
            
            return result
                

        def loadSettings():
            with open("data/GestureSettings.json") as jsonfile:
                settings = json.load(jsonfile)
                plc_info = settings.get("plc_info")
                set_value("Ip", plc_info["ip"])
                set_value("rack", plc_info["rack"])
                set_value("slot", plc_info["slot"])
                set_value("DB", plc_info["db_number"])
                set_value("Start", plc_info["start_addres"])
                set_value("Size", plc_info["size"])
                times = settings.get("GlobalSettings")
                set_value("triggertime", times["triggertime"])
                set_value("gesturetime", times["gesturetime"])
                
        def applyChanges():
            try:
                if get_value("ByIpCheck"):
                    ip = get_value("camIp")
                    self.detection.changeCam(ip)
                else: 
                    CamChange()
                plc_info = None
                settings = None
                times = None
                with open("data/GestureSettings.json") as jsonfile:
                    settings = json.load(jsonfile)
                    plc_info = settings.get("plc_info")
                    plc_info["ip"] = get_value("Ip")
                    plc_info["rack"] = get_value("rack")
                    plc_info["slot"] = get_value("slot")
                    plc_info["db_number"] = get_value("DB")
                    plc_info["start_addres"] = get_value("Start")
                    plc_info["size"] = get_value("Size")
                    times = settings.get("GlobalSettings")
                    times["triggertime"] = get_value("triggertime")
                    times["gesturetime"] = get_value("gesturetime")

                if compareChanges(plc_info, times):

                    with open("data/GestureSettings.json", "w") as jsonfile:
                        settings["plc_info"] = plc_info
                        settings["GlobalSettings"] = times
                        json.dump(settings, jsonfile)
                    popups.show_info("Notice", "The changes have been \n successfully implemented", large=300)
                else:
                    popups.show_info("Notice", "No changes have been \n applied", large=300)
            except Exception as e:
                popups.show_info("Error", e, large=500)

        with tab(label="Settings", parent=objParent, tag="Settings") as windowsettings:
            bind_item_theme(last_item(), themes.getWhiteText())
            with table(borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True) as PLC_connection:
                add_table_column(label="PLC Connection",tag="plc_connection")

                with table_row():
                    highlight_table_row(PLC_connection, 0 , color=(255,255,255,220))
                    with table(borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True):
                        add_table_column(label="Connection", width=450)
                        add_table_column(label="DB Data", width=450)
                        with table_row(height=140):
                            with table_cell():
                                with group():
                                    bind_item_theme(last_item(),themes.getBlackText())
                                    add_input_text(label="Ip Address", tag="Ip", hint="198.162.0.1")
                                    with tooltip(last_item()):
                                        add_text("Ip Address")
                                    add_input_int(width=200, label="rack", tag="rack")
                                    with tooltip(last_item()):
                                        add_text("rack")
                                    add_input_int(width=200, label="slot", tag="slot")
                                    with tooltip(last_item()):
                                        add_text("slot")

                            with table_cell():
                                with group():
                                    bind_item_theme(last_item(),themes.getBlackText())
                                    add_input_int(width=200,label="DB Number", tag="DB")
                                    with tooltip(last_item()):
                                            add_text("DB Number")
                                    add_input_int(width=200,label="Start Address", tag="Start")
                                    with tooltip(last_item()):
                                            add_text("Start Address")
                                    add_input_int(width=200,label="Size (Byte / offset)", tag="Size")
                                    with tooltip(last_item()):
                                            add_text("Size (Byte / offset)")
                        
            with table(borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True) as Software_settings:
                add_table_column(label="Software Settings")
                with table_row(height=117):
                    highlight_table_row(Software_settings, 0 , color=(255,255,255,220))
                    with table_cell():
                        with group():
                            bind_item_theme(last_item(),themes.getBlackText())
                            add_text("Camera Conecction")

                            with group(horizontal=True, tag="cbxCam", show=True):
                                add_combo(items=list(self.detection.GetListOfCameras().values()), tag="camSelector")
                                set_value("camSelector", "Select a camera")
                                add_button(label="Research WebCams", callback=reloadCamList)
                with table_row(height=117):
                    highlight_table_row(Software_settings, 1 , color=(255,255,255,220))
                    with table_cell():
                        with group():
                            bind_item_theme(last_item(),themes.getBlackText())
                            add_text("Parameter setting")
                            with group(horizontal=True, horizontal_spacing=60):
                                with group(horizontal=True):
                                    add_text("Trigger Time")
                                    add_input_float(tag="triggertime", width=160)
                                    with tooltip(last_item()):
                                        add_text("Trigger Time")
                                with group(horizontal=True):
                                    add_text("Gesture Time")
                                    add_input_float(tag="gesturetime", width=160)
                                    with tooltip(last_item()):
                                        add_text("Gesture Time")
            
            with group(horizontal=True, horizontal_spacing=600):
                bind_item_theme(last_item(),themes.getBlackText())
                add_button(label="Apply changes", callback=applyChanges)
                add_button(label="Open History Log", callback=loadTable)
            
            with group(horizontal=True, horizontal_spacing=600):
                bind_item_theme(last_item(),themes.getBlackText())
                resBtn = add_button(label="Reset Password",callback=changePassword)

                with theme() as button_theme:
                        with theme_component(mvAll):
                            add_theme_color(mvThemeCol_Button, (255,0,0,255), category=mvThemeCat_Core)
                
                bind_item_theme(resBtn, button_theme)
            loadSettings()
        bind_item_handler_registry(windowsettings, "FaceTabEvent")