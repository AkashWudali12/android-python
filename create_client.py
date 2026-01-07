from controller import AndroidClient 

if __name__ == "__main__":
    try: 
        client = AndroidClient()
        client.create()
    except KeyboardInterrupt:
        print("screen monitoring stopped")
    finally:
        client.destroy()