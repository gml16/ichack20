import keyboard

class KeyboardController():
    def __init__(self):
        pass

    def press_keys(self, key_string):
        keys = key_string.split()
        for key in keys:
            try:
                keyboard.press(key)
            except:
                print(key, "does not exist.")

if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--keys', help='One or multiple keys to press (key names can be space, left, a, ...)')
    args = parser.parse_args()
    press_keys(args.keys)
