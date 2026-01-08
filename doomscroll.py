from controller import AndroidClient 
from ui_state import UINode
import time
import random

if __name__ == "__main__":
    try: 
        client = AndroidClient()
        client.open("com.instagram.android")
        print("Instagram Opened")
        time.sleep(10)
        client.click(UINode(clickable=True, bounds=[324, 324, 2274, 2274]))
        print("Made it to reels")
        while True:
            client.scroll(540, 540, 1500, 500)
            watchtime = random.randint(1, 10)
            print(f"Watching for {watchtime} seconds")
            time.sleep(watchtime)
    except KeyboardInterrupt:
        print("screen monitoring stopped")
    finally:
        client.destroy()