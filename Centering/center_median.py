from matplotlib.markers import MarkerStyle
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from astropy.io import fits
from scipy.ndimage.filters import median_filter
from scipy.stats import binned_statistic
import os,shutil
from pathlib import Path
import time
import glob
from scipy import interpolate
import cv2

def twoD_Gaussian(xdata_tuple, A, x0, y0, sig_x, sig_y,offset):
    x, y = xdata_tuple                                                                                                                   
    inner = (x-x0)**2/(2*sig_x**2) + (y-y0)**2/(2*sig_y**2)
    g = offset+ A*np.exp(-inner)                           
    return g.ravel()

def count_v(arr):
    unique, c = np.unique(arr, return_counts = True)
    print(dict(zip(unique, c)))

def save_fit(im, name = 'xxx'):
    hdu = fits.PrimaryHDU(mask_c)
    hdu.writeto('Mask_C\OB{}.fits'.format(loops), overwrite=True)
        
#if true the shrink correction will be geometic, otherwise it will com from the fit
#*******# mathematical stretch #*******#
ev_angle_deg = 47
shrink = 1/np.cos(np.deg2rad(ev_angle_deg))
geometric_shrink = False 
#**************************************#

#path = Path("/home/evwaco/Documents/Mask_images")
path = Path(r"C:\Users\Optics Lab 2\Documents\Cheer\NanoPZ v0\Dump")
#path = Path(r"C:\Users\Optics Lab 2\Documents\Cheer\NanoPZ v0\Mask_images (copy)")

#only important for the first loop
loops = 0


##fig,axis = plt.subplots(1,2,figsize=(12,4.5))
bbox_args = dict(boxstyle="square", fc="lightsteelblue",ec='tab:blue')
bbox_args2 = dict(boxstyle="square",fc="navajowhite",ec="tab:orange")

if __name__ == '__main__':
    #start interactive mode a create a figure
    plt.ion()
    fig,axis = plt.subplots(1,3,figsize=(17,4.5))
    while True:
        #print('.', end ='')
        time.sleep(0.2)
        # src_files = os.listdir(path)
        #create a list of the files
        files = list(filter(os.path.isfile, glob.glob(str(path/'*'))))
        if len(files)>1:
            #select most recently created file
            files.sort(key=lambda x: os.path.getctime(x))
            mask_image = fits.open(path / files[-loops%200])[0].data
           
            #filter out noise and guess centre of mask 
            median_filter_image = median_filter(mask_image,size=3)
            y0,x0 = np.where(median_filter_image == np.min(median_filter_image))
            y0,x0 = y0[0],x0[0]


            
            threshold = 20000
            mask_c = (mask_image > threshold).astype(np.uint8)*255
            itemindex = np.where(mask_c == 0)
            xc, yc = np.median(itemindex, axis=1).astype(int)
            print(xc, yc)

            # Define the new image size
            new_w, new_h = 960, 600

            # Resize the image to the new size using OpenCV
            mask_c = cv2.resize(mask_c, (new_w, new_h))
            mask_c = (mask_c > 254).astype(np.uint8)*255
            unique, counts = np.unique(mask_c, return_counts=True)
            print(np.asarray((unique, counts)).T)

            # Draw contours on the original image
            mask_c = cv2.cvtColor(mask_c, cv2.COLOR_GRAY2RGB)
            
            img_med = cv2.circle(mask_c, (yc//2, xc//2), radius=0, color=(255, 0, 0), thickness=10)
            img_contours = cv2.circle(mask_c, (x0//2,y0//2), radius=0, color=(255, 0, 255), thickness=10)
            cv2.imshow('Contours', img_contours)
            # Display the result
            
            cv2.waitKey(25)
            y0,x0 = xc, yc
            #cv2.destroyAllWindows()


            
            box_size = 120
            #crop image
            mask_psf = mask_image[y0-box_size:y0+box_size,x0-box_size:x0+box_size]
            #mask_psf = mask_image #no cropping of the image
            max_val = np.max(mask_psf)  
            y_box,x_box = mask_psf.shape

            #define a meshgrid of the cropped image
            x = np.linspace(0, x_box, x_box)
            y = np.linspace(0, y_box, y_box)
            x, y = np.meshgrid(x, y)

            #ravel the image to apply a curve fit
            mask_psf_ravelled = mask_psf.ravel()
            initial_guess = (-max_val,x_box/2,y_box/2,1,1,max_val)
            popt, pcov = curve_fit(twoD_Gaussian, (x, y), mask_psf_ravelled, p0=initial_guess)
            psf_fitted = twoD_Gaussian((x, y), *popt)
            mask_gauss = psf_fitted.reshape(y_box, x_box)  #reshape the fit to 2D
            #extract the variables
            centre_x = popt[1]
            centre_y = popt[2]
            if geometric_shrink!=True:
                shrink = popt[3]/popt[4]
            
            #find the distances to the centre of all the pixels
            indices = np.indices((y_box,x_box))
            y_vals,x_vals = indices[0].ravel(), indices[1].ravel()
            y_dist = (y_vals-centre_y+0.5)*shrink
            x_dist = x_vals-centre_x+0.5
            distances = np.sqrt(x_dist**2+y_dist**2)

            dist_binned_intensity, edges, _ = binned_statistic(distances, mask_psf_ravelled, 'median', bins=80)
            dist_binned_gauss, edges_gauss, _ = binned_statistic(distances, psf_fitted, 'median', bins=40)
            dist_bin = edges+(edges[1]-edges[0])/2   #move to centre of bin
            dist_bin = dist_bin[:-1]

            
            min_val_centre = min(dist_binned_intensity)
            median_val = np.median(mask_image)
            y_lim = round(median_val+500,-3)
            if loops ==0:
                min_val = min_val_centre
            elif min_val>min_val_centre:
                min_val = min_val_centre
                axis[0].clear()
            else:axis[0].clear()

            ####FWHM
            half_maximum = (median_val-min_val_centre)/2 + min_val_centre
            interpolation = interpolate.interp1d(dist_binned_intensity,dist_bin)
            HWHM = interpolation(half_maximum)
            FWHM = HWHM*2 

            
            axis[0].plot(distances,mask_psf_ravelled,marker='.',markersize=2,linewidth=0)
            axis[0].plot(dist_bin, dist_binned_intensity,linewidth = 2) 
            axis[0].plot([0,HWHM],[half_maximum,half_maximum],linewidth=0.8,linestyle='--',color='k',alpha=0.3)
            axis[0].set_ylabel('intensity')
            axis[0].set_xlabel('distance from centre')
            axis[0].set_xlim(-1,30)
            axis[0].set_ylim(1300,y_lim)
            axis[0].annotate( 'Minimum',xy = (23.5,y_lim/2.967),fontsize=9,weight='bold')
            axis[0].annotate( '{}'.format(int(min_val)),xy = (24,y_lim/7.714),bbox=bbox_args,fontsize=12,weight='bold')
            axis[0].annotate( '{}'.format(int(min_val_centre)),xy = (24,y_lim/4.154),bbox=bbox_args,fontsize=12)#,weight='bold')
            axis[0].annotate( 'Current',xy = (18.3,y_lim/4.154),fontsize=10)#,weight='bold')
            axis[0].annotate( 'Overall',xy = (18.3,y_lim/7.714),fontsize=10,weight='bold')
            axis[0].annotate( 'FWHM',xy = (HWHM+1.2,half_maximum-half_maximum/30))
            axis[0].annotate( '{}'.format(np.round(FWHM,2)), xy=(HWHM+5.5,half_maximum-half_maximum/30),bbox=bbox_args2,fontsize=11)
            axis[0].set_title('Mask Profile')
            axis[1].imshow(mask_psf.reshape(y_box, x_box),
                           cmap='gray',
                           vmin = 0,
                           vmax = round(np.median(mask_image)+2000,-3))
            axis[1].set_title('Mask Image')
            axis[2].imshow(mask_gauss,
                           cmap='gray',
                           vmin = 0,
                           vmax = round(np.median(mask_gauss)+2000,-3))
            axis[2].set_title('Mask Fit')
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            loops+=1
            #break

