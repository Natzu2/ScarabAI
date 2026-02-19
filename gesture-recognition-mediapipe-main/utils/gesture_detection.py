import copy
import itertools
import cv2 as cv
import numpy as np
import mediapipe as mp
import time
import json
from deepface import DeepFace
from utils import History, CvFpsCalc
import dearpygui.dearpygui as dpg
from model import KeyPointClassifier
from pygrabber.dshow_graph import FilterGraph
import os
mp_hands = mp.solutions.hands

class GestureDetection():
    def __init__(self, pi_connection, src=0, name="WebCamVideoStream"):
        self.hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        )
        
        self.keypoint_classifier = KeyPointClassifier()

        # Settings Loading   
        with open("data/GestureSettings.json",) as jsonfile:
            self.settings = json.load(jsonfile)
            self.keypoint_classifier_labels = self.settings.get("keypoints")
            self.globalSettings = self.settings.get("GlobalSettings")
            
        self.fps  = CvFpsCalc(buffer_len=10)
        self.history = History()
        self.name = name
        self.timemark = 0.0
        self.trigered = False

        self.stream = cv.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.switch = "Gesture"
        self.pi_connection = pi_connection

    # Prepocess functions of landmarks and arguments
    def draw_landmarks(self, image, landmark_point):
        if len(landmark_point) > 0:
            # Thumb
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]),
                    (233, 131, 0), 2)

            # Index finger
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]),
                    (233, 131, 0), 2)

            # Middle finger
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]),
                    (233, 131, 0), 2)

            # Ring finger
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]),
                    (233, 131, 0), 2)

            # Little finger
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]),
                    (233, 131, 0), 2)

            # Palm
            cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]),
                        (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]),
                    (233, 131, 0), 2)
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]),
                    (0, 0, 0), 6)
            cv.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]),
                    (233, 131, 0), 2)

        # Key Points
        for index, landmark in enumerate(landmark_point):
            if index == 0:  # 手首1
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 1:  # 手首2
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 2:  # 親指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 3:  # 親指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 4:  # 親指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 5:  # 人差指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 6:  # 人差指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 7:  # 人差指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 8:  # 人差指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 9:  # 中指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 10:  # 中指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 11:  # 中指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 12:  # 中指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 13:  # 薬指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 14:  # 薬指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 15:  # 薬指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 16:  # 薬指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
            if index == 17:  # 小指：付け根
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 18:  # 小指：第2関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 19:  # 小指：第1関節
                cv.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
            if index == 20:  # 小指：指先
                cv.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                          -1)
                cv.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)

        return image
    def pre_process_landmark(self,landmark_list):
        temp_landmark_list = copy.deepcopy(landmark_list)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        # Convert to a one-dimensional list
        temp_landmark_list = list(
            itertools.chain.from_iterable(temp_landmark_list))

        # Normalization
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list
    def draw_info(self, image, fps):
        cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
                   1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
                   1.0, (255, 255, 255), 2, cv.LINE_AA)
        return image
    def calc_landmark_list(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # Keypoint
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            # landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point
    # Process video streaming
    def process_video(self):
        if self.switch == "Gesture":
            try:
                (self.grabbed, self.frame) = self.stream.read()
                data = cv.flip(self.frame, 2)
                data = cv.cvtColor(data, cv.COLOR_BGR2RGB)
                result = self.hands.process(data)
                fps = self.fps.get()

                if result.multi_hand_landmarks is not None:
                    for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                        landmark_list = self.calc_landmark_list(data, hand_landmarks)
                        pre_processed_landmark_list = self.pre_process_landmark(landmark_list)
                        # Hand sign classification
                        hand_sign_id = self.keypoint_classifier(pre_processed_landmark_list)
                        command = self.mapGesture(self.keypoint_classifier_labels[hand_sign_id])
                        #print(command, "tipo: ", type(command))
                        self.detectTrigger(hand_sign_id, handedness, data, command)
                        data = self.draw_landmarks(data, landmark_list)
                else: 
                    self.detectTrigger(sign_id=-1, handedness=None, data=None, command=None)

                data = self.draw_info(data, fps)
                data = data.ravel()
                data = np.asarray(data, dtype='f') 
                texture_data = np.true_divide(data, 255.0)
                dpg.set_value("Cam 1", texture_data)
            except Exception as e:
                print("The process video Failed")
                self.history.save_error("The process video Failed")
                print("Cause", e)
    
    def process_nomal_video(self,):
        if self.switch == "Face":
            try:
                (self.grabbed, self.frame) = self.stream.read()
                data = cv.flip(self.frame, 2)
                data = cv.cvtColor(data, cv.COLOR_BGR2RGB)
                fps = self.fps.get()
                data = self.draw_info(data, fps)
                data = data.ravel()
                data = np.asfarray(data, dtype='f') 
                texture_data = np.true_divide(data, 255.0)
                dpg.set_value("Cam 2", texture_data)
            except Exception as e:
                print("The process video Failed")
                print("Cause", e)
    
    
    def firsFrame(self):
        (self.grabbed, self.frame) = self.stream.read()
        data = cv.flip(self.frame, 2)
        data = cv.cvtColor(data, cv.COLOR_BGR2RGB)
        data = np.asfarray(data, dtype='f')
        texture_data = np.true_divide(data, 255.0)
        return texture_data, self.frame
    
    def releaseStream(self):
        self.stream.release()
    
    def changeCam(self, src):
        self.stream = cv.VideoCapture(src)
    
    def GetListOfCameras(self):
        try:
            devices = FilterGraph().get_input_devices()
            available_cameras = {}
            for device_index, device_name in enumerate(devices):
                available_cameras[device_index] = device_name
        except:
            available_cameras = False
        return available_cameras
    
    def mapGesture(self, gesture):
        try:
            jsonfile = open("data/GestureSettings.json",)
            self.settings = json.load(jsonfile)
            self.gestures = self.settings.get("GestureSettings")
            command = list(self.gestures.keys())[list(self.gestures.values()).index(gesture)]
            return command
        except:
            return "None"
    
    def mapBit(self, command):
        if command == "Trigger": return 0
        if command == "Alarm Reset": return 4
        if command == "Start": return 2
        if command == "Stop": return 1
        if command == "End production": return 3
    
    def detectTrigger(self, sign_id, handedness, data, command=None):
         # Settings Loading   
        with open("data/GestureSettings.json",) as jsonfile:
            settings = json.load(jsonfile)
            self.keypoint_classifier_labels = self.settings.get("keypoints")
            self.globalSettings = self.settings.get("GlobalSettings")
        
        triggertime = self.globalSettings["triggertime"]
        gesturetime = self.globalSettings["gesturetime"]
        if not self.trigered:
            if command == "Trigger":
                if self.timemark == 0.0:
                    self.timemark = time.time() 
                else:
                    if self.timemark != -1:
                        #Progress Bar
                        dpg.set_value("ProgressBar",(time.time() - self.timemark)/triggertime)
                        if (self.timemark+triggertime) < time.time():
                            message, result = self.auth(frame=data)
                            if result: #self.face_reco.recognizeAsync(data)
                                self.history.save("Facial recognition successful")
                                #dpg.set_value("Trigger", "Trigger ON")
                                dpg.configure_item("ProgressBar", overlay="Trigger ON")
                                self.history.save("Trigger command received")
                                self.trigered = True
                                self.pi_connection.writeDB(0, 0, True)
                                self.timemark = time.time()
                                dpg.set_value("ProgressBar", 1)
                            else:
                                dpg.set_value("ProgressBar", 0.0)
                                dpg.set_value("Gesture", message)
                                dpg.configure_item("Gesture", color=(255, 0, 0, 255))
                                self.history.save_error("Facial recognition failed (Unauthorized)")
                                self.timemark = -1
            else:
                self.timemark = 0.0
                dpg.set_value("ProgressBar", 0.0)
        else:
            
            #Progress Bar
            dpg.set_value("ProgressBar",((self.timemark+gesturetime) - time.time())/gesturetime)

            if (self.timemark+gesturetime) >= time.time():
                if command != None:
                    command = self.mapGesture(self.keypoint_classifier_labels[sign_id])
                    dpg.configure_item("Gesture", color=(0, 0, 0, 255))
                    dpg.bind_item_font("Gesture", "tff-commands")
                    dpg.set_value("Gesture", command)
                else: dpg.set_value("Gesture", "")
            else:
                if command != None:
                    self.history.save(command + " command received")
                    self.pi_connection.sendCommand(0, self.mapBit(command))
                    
                #dpg.set_value("Trigger", "Trigger OFF")
                dpg.configure_item("ProgressBar", overlay="Trigger OFF")
                self.history.save("Gesture time out")
                self.timemark = 0.0
                self.trigered = False
                self.pi_connection.writeDB(0, 0, False)
                #self.pi_connection.writeDB(0, self.mapBit(command), False)
                dpg.set_value("Gesture", "")
                
    def setupFaceModel(self, frame):
        inicio = time.time()
        try:
            model = "data/user_db/representations_vgg_face.pkl"
            os.remove(model)
            result = DeepFace.find(frame, db_path="./data/user_db/", enforce_detection=False)
            fin = time.time()
            print(result, "Tiempo de ejecución====>"+str(fin-inicio))
        except OSError as error:
            result = DeepFace.find(frame, db_path="./data/user_db/", enforce_detection=False)
            print(error)
        
        
    def modelFace(self, frame):
        inicio = time.time()
        try:
            result = DeepFace.find(frame, db_path="./data/user_db/", enforce_detection=False)
            fin = time.time()
            print(result, "Tiempo de ejecución ===>"+str(fin-inicio))
            result = result[0].values.tolist() 
            return result[0]['confidence'].item()
        except Exception:
            print(Exception)
    
    def auth(self, frame):
        inicio = time.time()
        try:
            auth_value = self.modelFace(frame=frame)
            if  auth_value >= 90:
                fin = time.time()
                print("Autorizado", "Tiempo de ejecución auth ===>"+str(fin-inicio))
                return "", True
            else:
                fin = time.time()
                print("NO Autorizado", "Tiempo de ejecución auth ===>"+str(fin-inicio))
                dpg.bind_item_font("Gesture", "tff-commands")
                return "You are not authorized",False
        except Exception as e:
            print(e)
            dpg.bind_item_font("Gesture", "ttf-menu")
            return "No users captured, Try improving your face \n visibility or add yourself as user", False