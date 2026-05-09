import numpy as np

WORKING_DIR = "."

block_height = -45

default_port="/dev/tty.usbmodem101"


# TODO: This section needs to be updated with your calibration
#  2x3 affine matrix for pixel -> robot (X,Y)
M = np.array([
     [6.00650232e-03 ,-4.84214952e-01,  3.80653329e+02 - 4],
     [-4.69079919e-01  ,3.74996755e-03,  1.55349575e+02 - 3]
], dtype=np.float64)
                 
z_above = 90            # safe travel height
z_table = -60           # Z at table contact — raised to prevent suction cup pressing into table
block_height_mm = 10   # block physical thickness
block_length_mm = 20   # block physical length
stack_delta_mm = 10    # extra height when stacking (to avoid collision)
side_offset_mm = 10    # extra XY gap when placing beside

capture_wait_time = 10
camera_index = 0


