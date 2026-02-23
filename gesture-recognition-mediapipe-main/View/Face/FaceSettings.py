from dearpygui.dearpygui import*
from utils import popUp
import os
import cv2 as cv
import unicodedata
import time as t
import dearpygui.dearpygui as dpg
from deepface import DeepFace
from utils import Theme

themes =  Theme()
notice = popUp()

class FaceSettings:
    def __init__(self, detection):
        self.detection = detection
    def View(self, objParent):
        with texture_registry(show=False, tag="face_texture_registry"):
            
            #widthi, heighti, channelsi, datai = load_image(file="img/No image.png")
            #add_static_texture(width=widthi, height=heighti, default_value=datai, tag="No image")

            texture_data, frame = self.detection.firsFrame()
            add_raw_texture(width=frame.shape[1], height=frame.shape[0], default_value=texture_data, tag="Photo", format=mvFormat_Float_rgb)
            for file in self.getUsersNames():
                width, height, channels, data = load_image(file=f"data/user_db/{file}.png")
                add_static_texture(width=width, height=height, default_value=data, tag=file, parent="face_texture_registry")
        
        def takePhoto():
            disable_item("takePhoto")
            valid = self.validate_db(True)
            if valid == True:
                name = get_value("name")
                texture_data, frame = self.detection.firsFrame()
                message, result =self.addUserFace(frame=frame, name=name)
                if result:
                    #configure_item("preview", texture_tag="Photo")
                    set_value("Photo", texture_data)
                    show_item("preview")
                    delete_item("spacer")
                    t.sleep(0.5)
                    set_value("trainProgress", 1); dpg.configure_item("trainProgress", overlay="100%")
            else:
                print("Failure")
                message = "missing directory created, repeat process"
            
            notice.show_info("Notice", message, 300)
            set_value("trainProgress", 0); dpg.configure_item("trainProgress", overlay="0%")
            enable_item("takePhoto")

        with tab(label="User Manager", parent=objParent, tag="Face"):
            bind_item_theme("Face", themes.getWhiteText())
            with table(header_row=False):

                add_table_column()
                add_table_column()

                with table_row():
                        with table_cell():
                            with dpg.group():
                                dpg.bind_item_theme(dpg.last_item(),themes.getBlackText())
                                add_image("Cam 2")
                                with dpg.group(horizontal=True):
                                    add_input_text(tag="name", hint="e.g. Riccardo")
                                    add_text("Operator Name", color=(255,255,255,255))
                                add_button(tag="takePhoto", label="Take a photo", callback=takePhoto)
                        with table_cell():
                            with dpg.group():
                                dpg.bind_item_theme(dpg.last_item(),themes.getBlackText())
                                add_image("Photo", tag="preview")
                                add_spacer(height=dpg.get_item_height("Photo"), tag="spacer")
                                add_progress_bar(default_value=0, tag="trainProgress", overlay="0%", width=430)
                                add_button(label="Manage Users", callback=self.ShowUsersTable)
                                hide_item("preview")

    def strip_accents(self, text):
        text = unicodedata.normalize('NFD', text)\
            .encode('ascii', 'ignore')\
            .decode("utf-8")
        return str(text)

    def getUsersNames(self):
        files = os.listdir("data/user_db/")
        names = filter(lambda file: file[-1] == "g", files)
        names = [name.replace(".png", "") for name in names]
        return list(names)

    def ShowUsersTable(self):
        names = self.getUsersNames()
        for name in names:
            width, height, channels, data = load_image(file=f"data/user_db/{name}.png")
            try:
                add_static_texture(width=width, height=height, default_value=data, tag=name, parent="face_texture_registry")
            except:
                remove_alias(name)
                add_static_texture(width=width, height=height, default_value=data, tag=name, parent="face_texture_registry")
        
        def removeUser(sender, app_data, user_data):
            path = f"data/user_db/{user_data[0]}.png"
            delete_item(user_data[1])
            try:
                os.remove(path)
                model = "data/user_db/ds_model_vggface_detector_opencv_aligned_normalization_base_expand_0.pkl"
                os.remove(model)
                texture_data, frame = self.detection.firsFrame()
                self.detection.setupFaceModel(frame)
            except OSError as error:
                print(error)
                print("File doesn't exists!")
                texture_data, frame = self.detection.firsFrame()
                self.detection.setupFaceModel(frame)

        def editar(sender, app_data, user_data):
            set_value("name", user_data[0])
            delete_item(user_data[1])

        with window(label="Users Table", modal=True, width=450, height=400, pos=(260, 200), no_resize=True) as usertable:
            with table(row_background=True, borders_innerH=True, borders_innerV=True):
                add_table_column(label="User",init_width_or_weight=0.1)
                add_table_column(label="Photo",init_width_or_weight=0.1)
                add_table_column(label="Actions",init_width_or_weight=0.1)
                for i in range(len(names)):
                    with table_row() as row:
                        add_text(names[i])
                        add_image(names[i], width=135, height=150)
                        with dpg.group():
                            btnUpdate = add_button(label="Update",width=130, callback=editar, user_data=[names[i], usertable])
                            btnDelete = add_button(label="Delete", callback=removeUser, user_data=[names[i], row], width=130)
                            bind_item_theme(btnDelete, themes.getExitTheme())
        bind_item_theme(usertable, themes.getPopUpTheme())
        
                        
    def isEmptyDir(self):
        if os.listdir("data/user_db/"):
            return True
        else:
            print("No training values!")
            return False

    def validate_db(self, train):
        if os.path.isdir("data/user_db/"):
            if not self.isEmptyDir() and train == True:
                return True
            elif not self.isEmptyDir():
                print("No data found...")
                return False
            elif self.isEmptyDir():
                print("Data found, proceed")
                return True
        else:
            print("Directory not found, Creating it...")
            dir_name = "user_db"
            parent_dir = "data/"
            path = os.path.join(parent_dir, dir_name)
            os.mkdir(path)
            print("Created! Repeat process")
            return False
    
    def addUserFace(self, frame, name):
        verify = DeepFace.extract_faces(frame, enforce_detection=False)
        set_value("trainProgress", 0.15); dpg.configure_item("trainProgress", overlay="15%")
        t.sleep(0.5)
        dict = verify[0]
        confidence = dict["confidence"]
        name = self.strip_accents(name)
        name = name.replace(" ", "")

        if not name:
            message = "Found empty name, \n type a valid entry"
            return message, False
        elif len(verify)>1:
            message = "Found More than a single face in image"
            return message, False 
        elif confidence > 0.80 :
            set_value("trainProgress", 0.30); dpg.configure_item("trainProgress", overlay="30%")
            t.sleep(0.5)
            path = f"data/user_db/{name}.png"
            cv.imwrite(path,frame)
            set_value("trainProgress", 0.45); dpg.configure_item("trainProgress", overlay="45%")
            t.sleep(0.5)
            try:
                path = "data/user_db/ds_model_vggface_detector_opencv_aligned_normalization_base_expand_0.pkl"
                os.remove(path)
                set_value("trainProgress", 0.60); dpg.configure_item("trainProgress", overlay="60%")
                t.sleep(0.5)
            except OSError as error:
                print(error)
            self.detection.setupFaceModel(frame)
            message ="User was added successfully"
            set_value("trainProgress", 0.80); dpg.configure_item("trainProgress", overlay="80%")
            t.sleep(0.5)
            return message, True
        else:
            message ="No faces found in image!"
            return message, False
        
        

