####################################################################################################################
# IMPORTS
import PygameController

from Cockpit import Cockpit
from TelloMK1 import TelloMK1


# Initialize Tello Instance
tello = TelloMK1()

# Initialize the Keyboard Controller with the tello instance
cockpit = Cockpit(tello)

# Run the main thread
PygameController.pygame_init()
PygameController.run(cockpit)
