import socket
import time
import av
import cv2

def monitor_dual_stream():
    # Ensure 'adb forward tcp:27183 localabstract:scrcpy' is active
    video_sock = None
    control_sock = None
    
    try:
        # 1. Establish Video Connection (First)
        video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        video_sock.connect(('127.0.0.1', 27183))
        print("✅ Video Socket Connected")

        # 2. Establish Control Connection (Second)
        # Small delay helps the server distinguish the two incoming connections
        time.sleep(0.1) 
        control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_sock.connect(('127.0.0.1', 27183))
        print("✅ Control Socket Connected")

        # 3. Read Device Metadata from the Video Socket
        # The server only sends this on the video channel
        device_name_raw = video_sock.recv(64)
        device_name = device_name_raw.decode('utf-8', errors='ignore').strip('\x00')
        print(f"📱 Device Name: {device_name}")

        # 4. Read Video Header (Codec, Width, Height)
        header = video_sock.recv(12)
        if len(header) == 12:
            print(f"📊 Header Received (Hex): {header.hex()}")
        else:
            print("⚠️ Header incomplete or delayed")

        print("Created Socket File")
        socket_file = video_sock.makefile('rb', buffering=0)

        # 5. Continuous Stream Loop
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
    finally:
        if video_sock:
            video_sock.close()
        if control_sock:
            control_sock.close()
        print("Sockets closed.")

if __name__ == "__main__":
    monitor_dual_stream()