import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backend_bases import MouseButton
import matplotlib.cm as cm
from pathlib import Path
import os
import glob
from astropy.io import fits
import json
import time
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
import time 

'''
mask_image[0,:]     # horizontal line   (x)
mask_image[:, 0]    # vertical line     (y)
'''

print(os.getcwd())
def sample():
    files = list(filter(os.path.isfile, glob.glob(str(path/'*'))))
    files.sort(key=lambda x: os.path.getmtime(x))
    return files

def gen_iterate(alist):
    while 1:
        for j in alist:
            yield j

def on_click(event):
    global h_select, v_select, fname, zoom_mode
    if event.button == MouseButton.LEFT and event.inaxes == ax[1]:
        v_select = int(event.xdata)
        h_select = int(event.ydata)
        #print(f'Clicked at x = {v_select}, y = {h_select}')
        fname       = ''
        zoom_mode   = False
    # print(event)
    
def on_zoom(event):
    global box_x1, box_y1, box_x2, box_y2, fname, zoom_mode
    if event.button == MouseButton.RIGHT and event.inaxes == ax[1]:
        if zoom_mode:
            zoom_mode = False
            box_x1, box_y1 = int(event.xdata), int(event.ydata)
        else:
            box_x2, box_y2 = int(event.xdata), int(event.ydata)
            zoom_mode = True
            # Swap values if necessary to ensure box_x1 < box_x2 and box_y1 < box_y2
            if box_x1 is not None:
                if box_x2 < box_x1:
                    box_x1, box_x2 = box_x2, box_x1
                if box_y2 < box_y1:
                    box_y1, box_y2 = box_y2, box_y1
            # Print the selected box coordinates
            print(f'Selected box: ({box_x1}, {box_y1}) - ({box_x2}, {box_y2})')
            fname = ''

def on_key(event):
    global mem_flag, fname, pause
    #print('you pressed', event.key, event.xdata, event.ydata)
    if event.key == 'm':
        #print('m', mem_flag)
        mem_flag    = not mem_flag
        fname       = ''
    if event.key == 'z':
        pause       = not pause
            
# Open log file
with open('../log.txt') as json_file:
    data = json_file.read()
js = json.loads(data)

# Path assign
path  = Path(js['Path'])

if js['Path'] == "":
    os.chdir(os.path.dirname(__file__) + '/../_sample')
    print('/_sample')
else:
    print("Targeted Path:", path)
print(os.getcwd())

# Initialize variables 
try:
    h_select = js['Hline']
    v_select = js['Vline']
except:
    h_select = 100
    v_select = 100
fname = ''
cmap  = js['cmap']

# Color Iterate
col_lst = ['r', 'g', 'b', 'c', 'm', 'k']
col_ele = gen_iterate(col_lst)

# add Subplot and on click handler 
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
box_x1, box_y1, box_x2, box_y2 = 0, 0, None, None
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('button_press_event', on_zoom)
fig.canvas.mpl_connect('key_press_event', on_key)
mem_flag  = True
zoom_mode = True
pause     = False
#plt.style.use('fivethirtyeight')
#exit()


def animate(i):
    global fname, box_x1, box_y1, box_x2, box_y2, mem_flag, pause, zoom_mode
    files = list(filter(os.path.isfile, glob.glob(str(path/'*.fits'))))
    files.sort(key=lambda x: os.path.getmtime(x))
    start_time = time.time()
    try:
        if fname == files[-1] or pause:
            pass
        else:
            image = fits.open(path / files[-1])
            mask_image = image[0].data
            mask_image = mask_image[710-200:710+200,1007-200:1007+200]
            image.close()
            mask_image_copy = mask_image.copy()
        
            # Clear plot
            ax[0].cla()
            ax[1].cla()
            ax[2].cla()

            ### Plotting ###
            if zoom_mode and box_y2 is not None:
                # Mark Box on Axis 1
                rect = matplotlib.patches.Rectangle((box_x1, box_y1), abs(box_x1-box_x2), abs(box_y1-box_y2), 
                                    linewidth=1, edgecolor='r', facecolor='none')
                ax[1].add_patch(rect)
                mask_image_zoom = mask_image[box_y1:box_y2+1, box_x1:box_x2+1]

                # Histrogram Plot
                '''
                ax[0].hist(mask_image_zoom.flatten(), bins=100, color=next(col_ele))
                ax[0].set_title('Histogram')
                ax[0].set_xlabel("Pixel Value")
                ax[0].set_ylabel("Number of Pixels")
                ax[0].set_yscale('log')
                '''
                
                # Zoom Image Display

                yh = np.mean(mask_image_zoom, axis=0)
                yv = np.mean(mask_image_zoom, axis=1)
                xh = np.arange(len(yh))  # Use np.arange() instead of list comprehension
                xv = np.arange(len(yv))  

                diffh = int(yh.max() - yh.min())
                diffv = int(yv.max() - yv.min())

                if xh[-1]*3 > xv[-1]:
                    ax[0].plot(xh, yh, color=next(col_ele), linestyle='dashed', marker='.', label='Horizontal line')
                    ax[0].set_title('Horizontal Box (ȳ from {} to {})'.format(box_y1, box_y2))
                    ax[0].set_xlabel("Pixel Location")
                    ax[0].set_ylabel("Pixel Value")

                    ax[2].hist(mask_image_zoom.flatten(), bins=100, color=next(col_ele))
                    ax[2].set_title('Histogram')
                    ax[2].set_xlabel("Pixel Value")
                    ax[2].set_ylabel("Number of Pixels")
                    ax[2].set_yscale('log')
                else:
                    ax[2].plot(xv, yv, color=next(col_ele), linestyle='dashed', marker='.', label='Horizontal line')
                    ax[2].set_title('Vertical Box (x̄ from {} to {})'.format(box_x1, box_x2))
                    ax[2].set_xlabel("Pixel Location")
                    ax[2].set_ylabel("Pixel Value")

                    ax[0].hist(mask_image_zoom.flatten(), bins=100, color=next(col_ele))
                    ax[0].set_title('Histogram')
                    ax[0].set_xlabel("Pixel Value")
                    ax[0].set_ylabel("Number of Pixels")
                    ax[0].set_yscale('log')
                #ax[2].set_box_aspect(1)
                
                
                #box_x1, box_y1, box_x2, box_y2 = None, None, None, None
            else:
                yh = mask_image[h_select, :] 
                yv = mask_image[:, v_select]
                xh = np.arange(len(yh))  # Use np.arange() instead of list comprehension
                xv = np.arange(len(yv))

                # Min Max Differential
                diffh = mask_image[h_select, :].max() - mask_image[h_select, :].min()
                diffv = mask_image[:, v_select].max() - mask_image[:, v_select].min()
                
                # Mark Line on Copy image
                mask_image_copy[h_select, :] = 0
                mask_image_copy[:, v_select] = 0

                # Plot Horizontal and Vertical Line
                ax[0].plot(xh, yh, color = next(col_ele), linestyle = 'dashed',
                               marker = '.', label= 'Horizontal line = {}'.format(h_select))
                ax[0].set_title('Horizontal line@{} ({})'.format(h_select, diffh))
                ax[0].set_xlabel("Pixel Location Along X")
                ax[0].set_ylabel("Pixel Value")
                #ax[0].legend(loc='lower left')
                ax[2].plot(xv, yv, color = next(col_ele), linestyle = 'dashed',
                               marker = '.', label= 'Vertical line = {}'.format(v_select))
                ax[2].set_title('Vertical line@{} ({})'.format(v_select, diffv))
                ax[2].set_xlabel("Pixel Location Along Y")
                ax[2].set_ylabel("Pixel Value")
                #ax[2].legend(loc='lower left')
                ax[2].set_box_aspect(1)

                box_x2, box_y2 = None, None          
            ax[1].imshow(mask_image_copy, cmap=cmap) # cm.get_cmap('Spectral')
            mem_char = ' (M)' if mem_flag else '' 
            ax[1].set_title(files[-1].split('\\')[-1]+mem_char)
            #fig.tight_layout()
            if mem_flag: fig.savefig('../_Dump/'+ ''.join(str(i) for i in time.localtime()[:6]) +'.png')
            
            fname = files[-1]
    except Exception as e:
        print('.', end='')
    #print('----- {} s -----'.format(time.time()-start_time))   

ani = FuncAnimation(plt.gcf(), animate, interval=100)
##plt.tight_layout()
plt.show()
#plt.get_current_fig_manager().window.mainloop()























