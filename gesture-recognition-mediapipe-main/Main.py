from View import FaceSettings
from View import GestureSettings
from View import Settings
from utils import *
from View.Settings.PasswordAccess import AccessPassword
from utils.picrawler_connection import PiCrawlerConnect
import dearpygui.dearpygui as dpg
import time
import threading
import sys

inicio = time.time()
loading = True
theme = Theme()


# Adapter to provide the minimal PLC-like interface expected by GestureDetection
class PiCrawlerAdapter:
    def __init__(self, piconnect):
        self.piconnect = piconnect
        self.trigger_state = False

    def writeDB(self, byte, bit, value):
        # emulate PLC bit writes for trigger state (bit 0)
        try:
            if bit == 0:
                self.trigger_state = bool(value)
                print(f"[PiCrawlerAdapter] trigger_state set to {self.trigger_state}")
            else:
                # store or ignore other bits for now
                print(f"[PiCrawlerAdapter] writeDB byte={byte} bit={bit} value={value}")
        except Exception as e:
            print("[PiCrawlerAdapter] writeDB error:", e)

    def sendCommand(self, byte, bit):
        # Map PLC bits to PiCrawler action names (customize as needed)
        mapping = {
            1: 'sit',        # Stop
            2: 'stand',      # Start
            3: 'wave_hand',  # End production
            4: 'excited'     # Alarm Reset
        }
        action = mapping.get(bit)
        if not action:
            print(f"[PiCrawlerAdapter] No action mapped for bit {bit}")
            return False

        try:
            print(f"[PiCrawlerAdapter] Executing action '{action}' for bit {bit}")
            return self.piconnect.executeAction(action)
        except Exception as e:
            print("[PiCrawlerAdapter] sendCommand error:", e)
            return False

def loading():
    dpg.create_context()
    
    width, height, channels, data = dpg.load_image("img/logoTEHGM.png")
    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="Te_logo")
    with dpg.window(label="Example Window") as window:
        dpg.add_image("Te_logo",width=700, height=450)
        dpg.add_text("The Application will start in a few seconds...", color=(255,255,255,255))
        with dpg.group(horizontal=True):
            dpg.add_progress_bar(tag="loading", overlay="0%", width=590)
            dpg.add_text("Loading...", color=(255,255,255,255))
    
    dpg.create_viewport(title='Hand-Gesture Command Machine', decorated=False, width=710, height=580, x_pos=630,y_pos=50, disable_close=True, resizable=False)
    dpg.set_primary_window(window, True)
    dpg.bind_theme(theme.getTheme())
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        if(loading == False):
            break
        else: 
            dpg.render_dearpygui_frame()
                #sys.exit()
                

t1 = threading.Thread(target=loading)
t1.start()
time.sleep(3)
dpg.set_value("loading", 0.10); dpg.configure_item("loading", overlay="10%")
dpc = PiCrawlerConnect()
picrawler_adapter = PiCrawlerAdapter(dpc)
dpg.set_value("loading", 0.20); dpg.configure_item("loading", overlay="20%")
detection = GestureDetection(pi_connection=picrawler_adapter)
dpg.set_value("loading", 0.30); dpg.configure_item("loading", overlay="30%")

if(detection.GetListOfCameras() == False):
    print("No camera has been detected")
    popup = popUp()
    popup.show_info("Error", "No camera has been detected \nThe program will now close", large=320)
    loading = False
    t1.join()
    sys.exit()

viewFace = FaceSettings(detection=detection)
dpg.set_value("loading", 0.40); dpg.configure_item("loading", overlay="40%")
viewGesture = GestureSettings()
dpg.set_value("loading", 0.50); dpg.configure_item("loading", overlay="50%")
viewSettings = Settings(detection=detection)
dpg.set_value("loading", 0.60); dpg.configure_item("loading", overlay="60%")
history = History()
dpg.set_value("loading", 0.70); dpg.configure_item("loading", overlay="70%")
acccess = AccessPassword(detection=detection)
dpg.set_value("loading", 0.80); dpg.configure_item("loading", overlay="80%")
popup = popUp()
dpg.set_value("loading", 0.90); dpg.configure_item("loading", overlay="90%")

texture_data1, frame1 = detection.firsFrame()
if viewFace.validate_db(False):
    detection.setupFaceModel(frame=frame1)
else:
    pass
dpg.set_value("loading", 1)
loading = False
t1.join()

dpg.destroy_context()

dpg.create_context()
dpg.create_viewport(title='Hand-Gesture Command Machine', width=975, height=760, resizable=False, x_pos=350,y_pos=30, disable_close=True)
dpg.setup_dearpygui()

history.save("The Application is booting")
viewGesture.loadGestureImagesAsync()



#print(detection.GetListOfCameras())

def tabEventFace():
    detection.switch = "Face"
    acccess.view()
        
def tabEventGest():
    detection.switch = "Gesture"
    

with dpg.item_handler_registry(tag="FaceTabEvent"):
    dpg.add_item_clicked_handler(callback=tabEventFace)
    
with dpg.item_handler_registry(tag="GestTabEvent"):
    dpg.add_item_clicked_handler(callback=tabEventGest)

def confirmExit():
    texture,frame=detection.firsFrame()
    message, auth = detection.auth(frame=frame)
    dpg.configure_item("exitModal", show=False)    
    if(auth):
        popup.show_info("Exit", "Closing the program...", 240)
        dpg.stop_dearpygui()
    else:
        popup.show_info("Warning", "You are not allowed to exit de program", 400)
# Graphic interfacer window #################################################################
#detection.detectTrigger()
with dpg.texture_registry(show=False):
    dpg.add_raw_texture(frame1.shape[1], frame1.shape[0], texture_data1, tag="Cam 1", format=dpg.mvFormat_Float_rgb)

with dpg.texture_registry(show=False):
    dpg.add_raw_texture(frame1.shape[1], frame1.shape[0], texture_data1, tag="Cam 2", format=dpg.mvFormat_Float_rgb)

with dpg.window(label="Gesture Cam1", tag="Gesture Cam1"):
    dpg.bind_font("ttf")
    dpg.add_button(label="Exit", pos=((dpg.get_viewport_width() - 120), 5), tag="btnExit", width=100, callback=lambda: dpg.configure_item("exitModal", show=True, pos=popup.centered_popup("exitModal")))
    with dpg.tab_bar(label="TabBar", tag="tabBar") as tab:
        with dpg.tab(label="Home", tag="Gest"):
            
            with dpg.table(row_background=True) as mainTable:
                webcam = dpg.add_table_column(width=250,width_fixed=True, label="WebCam", tag="webcam") 
                gesture_commands = dpg.add_table_column(width=250, label="Gesture Commands", tag="gesture_commands")

                with dpg.table_row():
                        dpg.highlight_table_row(mainTable, 0 , color=(255,255,255,220))

                        with dpg.table_cell():
                            with dpg.group():
                                dpg.bind_item_theme(dpg.last_item(),theme.getBlackText())
                                dpg.add_image("Cam 1")
                                #dpg.add_text("Trigger OFF", tag="Trigger")
                                #dpg.add_progress_bar(default_value=0.0, tag="ProgressBar", width=635)
                                dpg.add_progress_bar(default_value=0.0, tag="ProgressBar", overlay = "Trigger OFF", width=635)
                                dpg.add_text("", tag="Gesture")
                        with dpg.table_cell():
                            with dpg.group():
                                dpg.bind_item_theme(dpg.last_item(),theme.getBlackText())    
                                
                                with dpg.table(header_row=False, policy=dpg.mvTable_SizingFixedFit, resizable=False):

                                    dpg.add_table_column()
                                    dpg.add_table_column()
                                    viewGesture.getGestureLegend(1)

                                with dpg.window(label="Exit", width=350, modal=True, show=False, no_collapse=True, no_resize=True, tag="exitModal"):
                                    dpg.add_text("Are you sure you want to exit?", color=(0,0,0,255))
                                    dpg.add_separator()
                                    with dpg.group(horizontal=True, horizontal_spacing=15):
                                        dpg.add_button(label="OK", width=75, callback=confirmExit)
                                        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("exitModal", show=False))
                            
    
viewFace.View(tab)
viewGesture.View(tab)
viewSettings.View(tab)

# When you try to close the program are gonna do this
#####################################################

dpg.bind_theme(theme.getTheme())
dpg.bind_item_theme("camSelector", theme.getSelectTheme())
dpg.bind_item_theme("exitModal", theme.getPopUpTheme())
dpg.bind_item_theme("btnExit", theme.getExitTheme())
dpg.bind_item_theme("Gest", theme.getWhiteText())
#dpg.bind_item_font("Trigger", "tff-commands")
dpg.bind_item_font("Gesture", "tff-commands")
dpg.bind_item_handler_registry("Gest", "GestTabEvent")
dpg.bind_item_handler_registry("Face", "FaceTabEvent")
#detection.start()
# Graphic interfacer window (end) #################################################################
#dpg.show_style_editor()
dpg.set_primary_window("Gesture Cam1", True)
dpg.set_viewport_resize_callback(callback=lambda: dpg.set_item_pos(item="btnExit", pos=((dpg.get_viewport_width() - 120), 5)))
dpg.show_viewport()
history.save("Applications is running succesfuly")
while dpg.is_dearpygui_running():
    detection.process_video()
    detection.process_nomal_video()
    dpg.render_dearpygui_frame()
detection.releaseStream()
dpg.destroy_context()
history.save("Application off")
fin = time.time()
print("tiempo en ejecución => ",fin-inicio)
