import socket
from typing import Optional
import av
import cv2
import time
import subprocess
import threading
import xml.etree.ElementTree as ET
from ui_state import UINode

UI_STATE_FILE = "/data/local/tmp/t.xml"

# TODO: Implement __setup method so each instance of an Android Client controls a specific emulator

class AndroidClient:
    def __init__(self, __adb_path="/Users/akashwudali/Library/Android/sdk/platform-tools/adb", __emulator_id=""):
        self.__video_socket : Optional[socket.socket] = None
        self.__control_socket : Optional[socket.socket] = None
        self.ready = False

        self.__ADB_PATH = __adb_path
    
    def __setup_environment(self) -> None:
        pass

    def get_ui_root(self) -> Optional[ET.Element]:
        cmd = f"{self.__ADB_PATH} shell 'uiautomator dump {UI_STATE_FILE} > /dev/null && cat {UI_STATE_FILE}'"
        raw_xml = subprocess.check_output(cmd, shell=True, text=True)

        if raw_xml.startswith("<?xml"):
            return ET.fromstring(raw_xml)
        
        print("Could not get current ui hierarchy")
        return None
    
    def destroy(self) -> None:
        try:
            if self.__video_socket:
                self.__video_socket.close()
            if self.__control_socket:
                self.__control_socket.close()
            self.ready = False

            cmd = [self.__ADB_PATH, "shell", "rm", UI_STATE_FILE]
            subprocess.run(cmd)
        except Exception as e:
            print(f"The following error occured when destroying client:\n{e}")

    def __connect_socket(self) -> None:
        try:
            # 1. Establish Video Connection (First)
            self.__video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__video_socket.connect(('127.0.0.1', 27183))
            print("✅ Video Socket Connected")

            # 2. Establish Control Connection (Second)
            # Small delay helps the server distinguish the two incoming connections
            time.sleep(0.1) 
            self.__control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__control_socket.connect(('127.0.0.1', 27183))
            print("✅ Control Socket Connected")

            # 3. Read Device Metadata from the Video Socket
            # The server only sends this on the video channel
            device_name_raw = self.__video_socket.recv(64)
            device_name = device_name_raw.decode('utf-8', errors='ignore').strip('\x00')
            print(f"📱 Device Name: {device_name}")

            # 4. Read Video Header (Codec, Width, Height)
            header = self.__video_socket.recv(12)
            if len(header) == 12:
                print(f"📊 Header Received (Hex): {header.hex()}")
            else:
                print("⚠️ Header incomplete or delayed")
            
            self.ready = True

        except KeyboardInterrupt:
            print("\n👋 Stopping client...")
        except Exception as e:
            print(f"\n❗ Error: {e}")
        finally:
            if self.ready:
                print("Successfully created Android client")
            else:
                print("Failed to create Android client")

    def monitor_screen_cv2(self) -> None:
        try:
            self.__connect_socket()
            if self.ready:
                print("Created Socket File")
                socket_file = self.__video_socket.makefile('rb', buffering=0)

                # Continuous Stream Loop
                print("Reading raw video data (Ctrl+C to stop)...")
                container = av.open(socket_file, format='h264')

                for frame in container.decode(video=0):
                    img = frame.to_ndarray(format='bgr24')
                    cv2.imshow("Android Screen", img)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            else:
                print("Could not connect to video socket")
        except KeyboardInterrupt:
            print("\n👋 Stopping client...")
        except Exception as e:
            print(f"\n❗ Error: {e}")
    
    def click(self, node: UINode) -> bool:
        if node.clickable:
            try:
                x, y = node.center
                cmd = [self.__ADB_PATH, "shell", "input", "tap", str(x), str(y)]
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"Error occured clicking on {node.center}:\n{e}")
        else:
            print(f"Element at {node.center} not a clickable element")
            return False
    
    def scroll(self, x1, x2, y1, y2, speed=500) -> bool:
        try:
            cmd = [
                self.__ADB_PATH, 
                "shell", 
                "input", 
                "swipe", 
                str(x1), str(y1), 
                str(x2), str(y2), 
                str(speed)
            ]
            subprocess.run(cmd)
        except Exception as e:
            print(f"Error occured scrolling at {x1} {y1} {x2} {y2} with speed {speed}:\n{e}")
    
    def open(self, app_pkg):
        try:
            cmd = [
                self.__ADB_PATH, 
                "shell", 
                "monkey", 
                "-p", app_pkg, 
                "-c", "android.intent.category.LAUNCHER", 
                "1"
            ]
            subprocess.run(cmd)
        except Exception as e:
            print(f"Error opening {app_pkg}:\n{e}")