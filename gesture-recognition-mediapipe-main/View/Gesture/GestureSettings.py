from dearpygui.dearpygui import*
import numpy as np
import asyncio
import json
from utils import Theme
from utils import popUp

notice = popUp()

theme = Theme()
class GestureSettings:
    def __init__(self) -> None:
        self.imagenes = ("Fist","Live-Long","Okay","Peace","Rock","Stop","Thumbs-DOWN","Thumbs-UP")
        self.selectTheme = Theme()
        # Settings Loading   
        with open("data/GestureSettings.json",) as jsonfile:
            self.settings = json.load(jsonfile)
            self.gestures = self.settings.get("GestureSettings")
            self.keypoint = self.settings.get("keypoints")
    
    async def loadGestureImages(self):
        width = np.zeros(len(self.imagenes)).tolist()
        height = np.zeros(len(self.imagenes)).tolist()
        channels = np.zeros(len(self.imagenes)).tolist()
        data = np.zeros(len(self.imagenes)).tolist()
        for n, i in enumerate(self.imagenes):
            width[n], height[n], channels[n], data[n] = load_image(f"View/Gesture/img/{i}.png")
        width2 = np.zeros(3).tolist()
        height2 = np.zeros(3).tolist()
        channels2 = np.zeros(3).tolist()
        data2 = np.zeros(3).tolist()
        for n, i in enumerate(("1","2","3")):
            width2[n], height2[n], channels2[n], data2[n] = load_image(f"View/Face/img/{i}.png")
        with texture_registry(show=False):
            for i in range(len(self.imagenes)):
                add_static_texture(width=width[i], height=height[i], default_value=data[i], tag=f"imagen{i+1}")
            for i in range(3):
                add_static_texture(width=width2[i], height=height2[i], default_value=data2[i], tag=f"face{i+1}")
    
    def loadGestureImagesAsync(self):
        asyncio.run(self.loadGestureImages())

    def getGestureLegend(self,option):
        for i in range(0, 4):
            with table_row():
                for j in range(0, 2):
                    if self.imagenes[(i*2)+(j)] in list(self.gestures.values()):
                        maptext = list(self.gestures.keys())[list(self.gestures.values()).index(self.imagenes[(i*2)+(j)])]
                    else:
                        maptext = "None"
                    with table_cell():
                        with drawlist(width=140, height=140):
                            if(option == 1):
                                #draw_rectangle((0, 0), (150, 150), color=(255, 255, 255, 255), fill=(255, 255, 255, 255))
                                draw_image(f"imagen{(i*2)+(j+1)}", (0, 0), (140, 140), uv_min=(0, 0), uv_max=(1, 1))
                                draw_rectangle((2, 90), (138, 120), color=(247,159,17, 125), fill=(0, 255, 0, 105))
                                draw_text((2, 100), maptext, color=(0, 0, 0, 255), size=20, tag=f"imagemap{(i*2)+(j+1)}")
                            else:    
                                #draw_rectangle((0, 0), (150, 150), color=(255, 255, 255, 255), fill=(255, 255, 255, 255))
                                draw_image(f"imagen{(i*2)+(j+1)}", (0, 0), (140, 140), uv_min=(0, 0), uv_max=(1, 1))
                                draw_rectangle((2, 90), (138, 120), color=(247,159,17, 125), fill=(0, 255, 0, 105))
                                draw_text((2, 100), self.imagenes[(i*2)+(j)], color=(0, 0, 0, 255), size=20)
    
    def loadGestureMapping(self):
            for i in range(8):
                if self.imagenes[i] in list(self.gestures.values()):
                    maptext = list(self.gestures.keys())[list(self.gestures.values()).index(self.imagenes[i])]
                else:
                    maptext = "None"
                configure_item(f"imagemap{i+1}", text=maptext)

    def compareChanges(self, gestures):
            repeated = False
            if gestures == self.gestures:
                repeated = True
                notice.show_info("Notice", "No changes have been \n applied", large=300)
            
            return repeated

    def saveSettings(self):
        gestures = {"Trigger": get_value("option1"), "Alarm Reset": get_value("option2"), "Start": get_value("option3"), "Stop": get_value("option4"), "End production": get_value("option5")}
        repeated = self.compareChanges(gestures)
        for g in self.keypoint:
            if list(gestures.values()).count(g)>=2:
                repeated = True
                notice.show_info("Error","Unable to save \nGesture Settings", 300)

        if(repeated is not True):
            self.gestures = gestures
            self.settings["GestureSettings"] = self.gestures
            with open("data/GestureSettings.json", "w") as jsonfile:
                json.dump(self.settings, jsonfile)
            self.loadGestureMapping()
            notice.show_info("Success","Saved Gesture Settings", 300)


            # with window(label="Success", popup=True, no_move=True, no_resize=True, no_open_over_existing_popup=True, no_title_bar=True):
            #     add_text("Saved Gesture Settings")

    def loadSettings(self):
        elements = list(self.gestures.keys())

        for i in (range(1, len(elements)+1)):
            if self.gestures.get(elements[i-1]) in self.keypoint or self.gestures.get(elements[i-1]) == "None":
                    set_value(f"option{i}", self.gestures.get(elements[i-1]))
    
    def View(self, objParent):
        with tab(label="Gesture Mapping", parent=objParent) as window:
            bind_item_theme(last_item(), theme.getWhiteText())
            with table(header_row=True):

                add_table_column(label="Gestures", tag="gestures")
                add_table_column(label="Commands", tag="commands")

                with table_row():
                        with table_cell():
                            with group():
                                bind_item_theme(last_item(),theme.getBlackText())

                                with table(header_row=False, policy=mvTable_SizingFixedFit, resizable=False):

                                    add_table_column()
                                    add_table_column()
                                    self.getGestureLegend(2)
                        with table_cell():
                            with group():
                                bind_item_theme(last_item(),theme.getBlackText())

                                with group() as g:
                                    self.selectTheme = self.selectTheme.getSelectTheme()
                                    bind_item_theme(g,self.selectTheme)
                                    add_text("Trigger - 0.0 offset", color=(255, 255, 255, 255))
                                    add_combo(items=self.keypoint+["None"], tag="option1")
                                    add_text("Alarm Reset - 0.1 offset", color=(255, 255, 255, 255))
                                    add_combo(items=self.keypoint+["None"], tag="option2")
                                    add_text("Start - 0.2 offset", color=(255, 255, 255, 255))
                                    add_combo(items=self.keypoint+["None"], tag="option3")
                                    add_text("Stop - 0.3 offset", color=(255, 255, 255, 255))
                                    add_combo(items=self.keypoint+["None"], tag="option4")
                                    add_text("End Production - 0.4 offset", color=(255, 255, 255, 255))
                                    add_combo(items=self.keypoint+["None"], tag="option5")

                                add_button(label="Apply", callback=self.saveSettings)

                                self.loadSettings()
        bind_item_handler_registry(window, "FaceTabEvent")
        #bind_item_theme("gesture", theme.getWhiteText())
