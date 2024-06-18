import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
from pythonosc import udp_client
import neopixel

# Initialize I2C bus and PN532
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to communicate with RFID tags
pn532.SAM_configuration()

# Define OSC client
args = {"ip": "shine.local", "port": 5005}
client = udp_client.SimpleUDPClient(args["ip"], args["port"])

# Define GPIO pin for the NeoPixel data line
PIXEL_PIN = board.D18  # Assuming data line is connected to GPIO 18

# Define the number of pixels (24 for your ring)
NUM_PIXELS = 24

# Initialize NeoPixel strip
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5)

# Define RFID tags
rfid_tags = {
    1: {"uid": [0x23, 0xa8, 0x18, 0xf7, 0x64], "message": "Blue tag 1"},
    2: {"uid": [0xC9, 0x00, 0xFA, 0xB9, 0x8A], "message": "Blue tag 2"},
    3: {"uid": [0x4, 0x79, 0x8a, 0xea, 0xd1, 0x64, 0x80], "message": "Sticker 1"},
    4: {"uid": [0x04, 0xbb, 0x8a, 0xea, 0xd1, 0x64, 0x80], "message": "Sticker 2"},
    5: {"uid": [0x04, 0x47, 0xc8, 0xd2, 0x56, 0x49, 0x81], "message": "It'sa me"},
    6: {"uid": [0xb3, 0xc2, 0x00, 0xfd, 0x8c], "message": "White card"},
    7: {"uid": [0x04, 0x20, 0xee, 0x1a, 0x5c, 0x15, 0x90], "message": "Ticket"},
}

# Function to detect RFID tag
def detect_tag(uid):
    for tag_key, tag_data in rfid_tags.items():
        if uid == bytearray(tag_data["uid"]):
            return tag_key
    return None

# LED animation functions
def fadein_light_effect(delay=0.02, steps=10):
    max_brightness = 10  # Maximum brightness level
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        pixels.fill(dim_white)
        pixels.show()
        time.sleep(delay)

def fadeout_light_effect(delay=0.02, steps=10):
    max_brightness = 10  # Maximum brightness level
    for step in range(steps + 1):
        intensity = int(max_brightness * (steps - step) / steps)
        dim_white = (intensity, intensity, intensity)
        pixels.fill(dim_white)
        pixels.show()
        time.sleep(delay)

def move_light_effect(delay=0.02):

    white = (127, 127, 127) # Warm white color at 50% intensity
    dim_white = (10, 10, 10) # Warm white color at 50% intensity

    # Turn off all pixels
    pixels.fill(dim_white)
    pixels.show()
    
    # Sequence to light up two LEDs radially opposite each other
    for i in range(NUM_PIXELS // 2):
        opposite_index = i + NUM_PIXELS // 2
        
        pixels[i] = white  
        pixels[opposite_index] = white 
        
        pixels.show()
        time.sleep(delay)
        
        pixels[i] = dim_white
        pixels[opposite_index] = dim_white
    
    # Ensure all LEDs are off before exiting the function
    pixels.show()

def tag_read_light_effect():
    move_light_effect()


# Main loop
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is not None:
        tag_key = detect_tag(uid)
        if tag_key is not None:
            print(f"Tag {tag_key} detected. {rfid_tags[tag_key]['message']}")
            if tag_key == 1 or tag_key == 3:  # Blue tag 1
                print("sent tag ", tag_key)
                client.send_message("/4/multitoggle/2/1", 1.0)  # increase intensity
            elif tag_key == 2 or tag_key == 4:  # Blue tag 2
                client.send_message("/4/multitoggle/2/2", 1.0)  # decrease intensity
            elif tag_key == 6 or tag_key == 7:
                print("crickets")
                client.send_message("/4/multitoggle/2/3", 1.0)  # crickets
            elif tag_key == 5:
                print("mario")
                client.send_message("/4/multitoggle/2/7", 1.0)  # mario
            fadein_light_effect()
            tag_read_light_effect()
            move_light_effect()
            fadeout_light_effect()
        else:
            print(f"Unknown tag detected with UID: {uid}")
            uid_hex = " ".join(format(x, '02x') for x in uid)
            print(f"Tag UID: {[hex(byte) for byte in uid]}".replace("'", ""))  # print(f"Tag UID: {uid_hex}")
            client.send_message("/4/multitoggle/2/8", 1.0)  # error
            fadeout_light_effect()
    time.sleep(0.1)
