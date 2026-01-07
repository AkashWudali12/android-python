import socket
from typing import Optional
import av
import cv2
import time
import subprocess
import threading
import xml.etree.ElementTree as ET

UI_STATE_FILE = "/data/local/tmp/t.xml"
ADB_PATH = "/Users/akashwudali/Library/Android/sdk/platform-tools/adb"


class AndroidClient:
    def __init__(self):
        self.__video_socket : Optional[socket.socket] = None
        self.__control_socket : Optional[socket.socket] = None
        self.ready = False
        self.__running = False
        self.current_root = None
    
    def __setup_environment(self) -> None:
        pass

    def __get_ui_root(self) -> Optional[ET.Element]:
        cmd = f"{ADB_PATH} shell 'uiautomator dump {UI_STATE_FILE} > /dev/null && cat {UI_STATE_FILE}'"
        raw_xml = subprocess.check_output(cmd, shell=True, text=True)

        if raw_xml.startswith("<?xml"):
            return ET.fromstring(raw_xml)
        
        print("Could not get current ui hierarchy")
        return None

    def __update_ui_state(self):
        updates = 0
        while self.__running:
            self.current_root = self.__get_ui_root()
            updates += 1

            if updates % 10 == 0:
                print(f"Took {updates} snapshots of ui")
                if self.current_root is None:
                    print("No root found")
                else:
                    print(f"Root has tag {self.current_root.tag}")
        
        print("Stopped collecting ui state")
    
    def create(self) -> bool:
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
            
            self.__running = True
            threading.Thread(target=self.__update_ui_state(), daemon=True)

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
            return self.ready

    def destroy(self) -> None:
        try:
            if self.__video_socket:
                self.__video_socket.close()
            if self.__control_socket:
                self.__control_socket.close()
            self.ready = False
            self.__running = False

            cmd = [ADB_PATH, "shell", "rm", UI_STATE_FILE]
            subprocess.run(cmd)
        except Exception as e:
            print(f"The following error occured when destroying client:\n{e}")

    def monitor_screen_cv2(self) -> None:
        if self.__video_socket is not None:
            try:
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
            except KeyboardInterrupt:
                print("\n👋 Stopping client...")
            except Exception as e:
                print(f"\n❗ Error: {e}")