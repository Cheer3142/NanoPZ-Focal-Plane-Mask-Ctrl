from rotpy.system import SpinSystem
from rotpy.camera import CameraList
from astropy.io import fits
import time 
import os
import numpy as np

def release_cam():
    if cam.is_streaming():
        cam.end_acquisition()
    if cam.is_init():
        cam.deinit_cam()
    cam.release()
    
system = SpinSystem()
cameras = CameraList.create_from_system(system, update_cams=True, update_interfaces=True)
if cameras.get_size():
    cam = cameras.create_camera_by_serial("14273946")   #camera = cameras.create_camera_by_index(0)
else:
    print("No Camera")
    exit()



#--- Setting the exposure to reach saturation ---# Unused
th_val = 0.9                # Saturation level

#--- Saving a sequence ---#
seq_path = r"C:\Users\Optics Lab 2\Documents\Cheer\NanoPZ v0\Dump" # Path to save the file. Update accordingly.
if not os.path.exists(seq_path): os.mkdir(seq_path)
seq_name = "img"            # Name of the files. Update accordingly.
seq_nb = 1000                # Number of frames to save. Update accordingly.
timewait = 0.1             # Tine to wait for the configuration to be applied

# Defining the parameters
modeStr = 'Continuous'      # {0: 'Continuous', 1: 'SingleFrame', 2: 'MultiFrame'}
pixelformat = "Mono16"      # {'Mono8': 0, 'Mono16': 1, 'RGB8Packed': 2}
gainvalue = 23.99
# Fits file header (Header-Data Unit)
header = fits.Header()
header['BITPIX'] = 16       # 16-bit data need to refer to the pixel format
header['NAXIS'] = 2         # 2D image

# Nodemap of Camera
nodemap = cam.get_tl_dev_node_map()
ip = nodemap.get_node_by_name('GevDeviceAutoForceIP')
ip.execute_node()


if ip.is_done():
    time.sleep(1)
    cameras = CameraList.create_from_system(system, update_cams=True, update_interfaces=True)
    cam = cameras.create_camera_by_serial("14273946")
    cam.init_cam()
    cam.camera_nodes.PixelFormat.set_node_value_from_str(pixelformat, verify=True)  
    cam.deinit_cam()
    cam.init_cam()
    ExposureTime = float(cam.camera_nodes.ExposureTime.get_min_value())
    max_width = cam.camera_nodes.Width.get_max_value()
    max_height = cam.camera_nodes.Height.get_max_value()
    print("Initialize parameters of the camera....")
else:
    print("Spinnaker: Camera is on a wrong subnet")
    exit()
#exit()
# Setting the initial parameters of the camera (full frame) cam.camera_nodes.PixelFormat.get_node_value_as_str()

cam.camera_nodes.AcquisitionMode.set_node_value_from_str(modeStr, verify=True)
cam.camera_nodes.ExposureAuto.set_node_value_from_str('Off', verify=True)
cam.camera_nodes.ExposureMode.set_node_value_from_str('Timed', verify=True)
cam.camera_nodes.ExposureTime.set_node_value_from_str("{}".format(ExposureTime+30000), verify=True)
cam.camera_nodes.AcquisitionFrameRate.set_node_value_from_str('6', verify=True)

cam.camera_nodes.GainAuto.set_node_value_from_str("Off", verify=True)
cam.camera_nodes.Gain.set_node_value(gainvalue, verify=True)
cam.camera_nodes.OffsetX.set_node_value(0, verify=True)
cam.camera_nodes.OffsetY.set_node_value(0, verify=True)
cam.camera_nodes.Width.set_node_value(max_width, verify=True)
cam.camera_nodes.Height.set_node_value(max_height, verify=True)

cam.begin_acquisition()
for seq in range(1, seq_nb+1, 1):
    successful = False
    while not successful:        
        try:
            # Acquiring the image
            frame = cam.get_next_image(timeout=5)
            print("Exposure time:", cam.camera_nodes.ExposureTime.get_node_value_as_str())
            time.sleep(timewait)            
            # Saving the image frame.save_png('{}\img{}.png'.format(seq_path, i))
            a = frame.get_image_data()
            img_lst = []
            for i in range(0, len(a), 2):
                val = a[i] << 8 | a[i+1]
                img_lst.append(val)            
            #data = np.frombuffer(a, dtype=np.uint16).reshape(max_height, max_width).
            data = np.array(img_lst).reshape(max_height, max_width)
            # create a FITS HDU (Header-Data Unit) with the data and header
            hdu = fits.PrimaryHDU(data, header)
            hdu.writeto('{}\img{}.fits'.format(seq_path, seq), overwrite=True)

            frame.release()
            print("Saving frame ", seq, " / ", seq_nb)
            successful = True            
        except ValueError as e:
            frame.release() #print("Image lost")
release_cam()





