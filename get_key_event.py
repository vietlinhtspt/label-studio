from pynput import mouse, keyboard
import time 

def on_press(key):
    print(f'{key} pressed')

def on_release(key):
    print(f'{key} release')
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def get_keyboard_event():
    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
        
if __name__ == "__main__":
    get_keyboard_event()