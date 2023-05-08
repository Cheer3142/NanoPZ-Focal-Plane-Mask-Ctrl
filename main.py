import AppClass
import sys, os
#sys.path.insert(0, r'C:\Users\Optics_Lab_010\Desktop\Project\NanoPiezo\Anjelie img')
from maskAnalysis7_files_mod import *
import matplotlib.pyplot as plt
import numpy as np
import csv


FWHM_lst = []
Position_lst = []
old_FWHM = None
old_position = None
path = Path(r"C:\Users\Optics Lab 2\Documents\Cheer\NanoPZ v0\Dump")
method = 1
##path = Path(r"C:\Users\Optics Lab 2\Documents\Cheer\NanoPZ v0\Mask_images (copy)")

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)

def running_task(loops, ):
    global min_val
    global old_position, old_FWHM
    global mask_gauss
    
    # src_files = os.listdir(path)
    #create a list of the files
    files = list(filter(os.path.isfile, glob.glob(str(path/'*'))))

    try:
        if len(files)>1:
            #select most recently created file
            files.sort(key=lambda x: os.path.getctime(x))
            mask_image = fits.open(path / files[-loops%len(files)])[0].data
            
            
            if method:
                #filter out noise and guess centre of mask 
                median_filter_image = median_filter(mask_image,size=3)
                y0,x0 = np.where(median_filter_image == np.min(median_filter_image))
                # print(np.min(median_filter_image))
                y0,x0 = y0[len(y0)//2],x0[len(y0)//2]
                box_size = 120
                #crop image
                mask_psf = mask_image[y0-box_size:y0+box_size,x0-box_size:x0+box_size]
            else:
                threshold = 20000
                mask_c = (mask_image > threshold).astype(np.uint8)*255
                itemindex = np.where(mask_c == 0)
                yc, xc = np.median(itemindex, axis=1).astype(int)
                box_size = 120
                mask_psf = mask_image[yc-box_size:yc+box_size,xc-box_size:xc+box_size]
            
            
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

            ####FWHM
            half_maximum = (median_val-min_val_centre)/2 + min_val_centre
            interpolation = interpolate.interp1d(dist_binned_intensity,dist_bin)
            HWHM = interpolation(half_maximum)
            FWHM = HWHM*2
            
            #cv2.imshow('Mask Image', mask_psf)
            app.update_FWHM(np.round(FWHM, 2))
            app.update_image(mask_gauss)
            FWHM_lst.append(FWHM)
            Position_lst.append(0)   
            
            if app.call_param():
                try:                
                    current_position_call = float(app.call_param()[1].get().replace("b'", '').replace("'", '')) # current_position
                    if old_FWHM != FWHM or old_position != current_position_call:                
                        FWHM_lst.append(FWHM)
                        Position_lst.append(current_position_call)
                        print(FWHM, current_position_call)
                        old_position = current_position_call
                        old_FWHM = FWHM
                    app.update_FWHM(np.round(FWHM, 2)) 
                    app.update_image(mask_gauss)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print('*', end='')
        app.after(200, running_task, loops+1)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        app.after(500, running_task, loops)
        
def plot_a():
    # add figure and par    
    figure, host = plt.subplots(figsize=(8,5))
    par = host.twinx()

    # add label
    host.set_xlabel("Iteration")
    host.set_ylabel("FWHM")
    par.set_ylabel("Current Position")

    # Ploting
    p1, = host.plot([num for num in range(len(FWHM_lst))], FWHM_lst, color = 'g', linestyle = 'dashed',
                   marker = 'o',label = "FWHM")
    p2, = par.plot([num for num in range(len(FWHM_lst))], Position_lst, color = 'm', linestyle = 'solid',
                   marker = 'o',label = "Actuator Position")
    lns = [p1, p2]
    host.legend(handles=lns, loc='best')
    #plt.title('Report', fontsize = 16)
    plt.grid()
    plt.show()

if __name__ == "__main__":
    print(">> Main Start")
    app = AppClass.NanoPZ()
    running_task(0)
    app.mainloop()
    #plot_a()
    '''
    if app.call_param():
        with open("Output.csv", 'w', newline = '') as f:
            writer = csv.writer(f)
            for i in range(len(FWHM_lst)):
                writer.writerow([i+1, FWHM_lst[i], Position_lst[i]])

               
        # add figure and par    
        figure, host = plt.subplots(figsize=(8,5))
        par = host.twinx()

        # add label
        host.set_xlabel("Iteration")
        host.set_ylabel("FWHM")
        par.set_ylabel("Current Position")

        # Ploting
        p1, = host.plot([num for num in range(len(FWHM_lst))], FWHM_lst, color = 'g', linestyle = 'dashed',
                       marker = 'o',label = "FWHM")
        p2, = par.plot([num for num in range(len(FWHM_lst))], Position_lst, color = 'm', linestyle = 'solid',
                       marker = 'o',label = "Actuator Position")
        lns = [p1, p2]
        host.legend(handles=lns, loc='best')
        #plt.title('Report', fontsize = 16)
        plt.grid()
        plt.show()
    '''   
    























