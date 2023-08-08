#### Spindle Major/Minor Axis Plots
### Name: Manuela Richter
### Date 11/2021
#
# This script reads and applies a threshold to spindle images and measures 
# major/minor axis lengths as a proxy for spindle width/height (in control spindles).
# 
# Requires:
    # - folder(s) in a <directory> containing TIF files of spindles rotated and cropped so pole-pole axis is roughly left to right
        # - subfolders for each <dataset>
    # - <savingDirectory> to save plots
# Returns:
    # - swarm plot of all major axes measured with each dataset
    # - swarm plot of all minor axes measured with each dataset
    # - scatter plot of major vs. minor axes with all datasets
    
#%% Import useful packages
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy import stats
from skimage import io, filters, measure
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops, regionprops_table
from skimage.morphology import closing, square
from skimage.color import label2rgb

#from scikit bc their minor_axis_length code is buggy
import math

pixelToMicron = 10.5/100 #scope 1 pixel to micron ratio
colors = ["gray","tab:blue"]

# Figure appearance
size = [3,4]
plt.rc('font', size=22)          # controls default text sizes
plt.rc('axes', titlesize=22)     # fontsize of the axes title
plt.rc('axes', labelsize=22)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=22, color='black')    # fontsize of the tick labels
plt.rc('ytick', labelsize=22, color='black')    # fontsize of the tick labels
plt.rc('legend', fontsize=22)    # legend fontsize
plt.rc('figure', titlesize=22)

#%% Threshold & save images

# subfolder names for different conditions
datasets = ["PtK_GFP-tub","PtK_GFP-tub_mCh-p50"]

# directory to save exported plots, data, and stats
savingDirectory = "/Users/manuela/Desktop/Box Sync/p50_paper/fig1_length/plots/"

data_major, data_minor, data_coords = [],[],[]
for dataset in datasets:
    
    # directory where data is located. Data is TIF files of spindles rotated and cropped so pole-pole axis is roughly left to right
    directory = "/Users/manuela/Desktop/Box Sync/p50_paper/fig1_length/BDEFGS3S4-StaticLengths/data/"+dataset+"/processed_images/rotated/cropped/"
    
    cells = os.listdir(directory)
    cells.remove('thresholded')
    # cells.remove('jpeg')
    try:
        cells.remove('.DS_Store') #sometimes a hidden file sneaks its way into the folder... it's a mystery
    except ValueError:
        pass
    
    major_axes, minor_axes, coordinates = [],[],[]
    for cell in cells:
        print(cell)
        image = io.imread(directory+cell)
        
        #test all thresholding filters to pick the best one (I'm using Otsu)
        # from skimage.filters import try_all_threshold
        # fig, ax = try_all_threshold(image, figsize=(10, 8), verbose=False)
        # plt.show()
        
        #Code below adapted from scikit
        
        # apply threshold
        thresh = threshold_otsu(image)
        bw = closing(image > thresh, square(3))
        plt.imsave(directory+'thresholded/thresholded_'+cell.replace('.tif', '.jpg'), bw)
        
        # label image regions
        label_image = label(bw)
        # to make the background transparent, pass the value of `bg_label`,
        # and leave `bg_color` as `None` and `kind` as `overlay`
        image_label_overlay = label2rgb(label_image, colors= ["magenta"], image=image, bg_label=0)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(image_label_overlay)
        
        for region in regionprops(label_image):
            # take regions with large enough areas
            if region.area >= 8000:
                #draw ellipse 
                y0, x0 = region.centroid
                orientation = region.orientation
                x2 = x0 - math.sin(orientation) * 0.5 * region.major_axis_length
                y2 = y0 - math.cos(orientation) * 0.5 * region.major_axis_length
                x1 = x0 + math.cos(orientation) * 0.5 * region.minor_axis_length
                y1 = y0 - math.sin(orientation) * 0.5 * region.minor_axis_length

                # plots the major and minor axes
                ax.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
                ax.plot((x0, x2), (y0, y2), '-r', linewidth=2.5)
                ax.plot(x1, y1, '.b', markersize=15)
                ax.plot(x2, y2, '.w', markersize=15)
                ax.plot(x0, y0, '.g', markersize=15)
            
                minr, minc, maxr, maxc = region.bbox
                bx = (minc, maxc, maxc, minc, minc)
                by = (minr, minr, maxr, maxr, minr)
                ax.plot(bx, by, '-b', linewidth=2.5)
                
                major = region.major_axis_length
                minor = region.minor_axis_length
                # print(major)
                # print(minor)
                # print(region.area)
                major_axes.append(major * pixelToMicron)
                minor_axes.append(minor * pixelToMicron)
                coordinates.append([[x0,y0],[x2, y2],[x1,y1]])
        
                ax.set_axis_off()
                plt.tight_layout()
                
                # plt.imsave(directory+'thresholded/axes_drawn/axes_'+cell.replace('.tif', '.jpg'), bw)
                plt.savefig(directory+'thresholded/axes_drawn/axes_'+cell.replace('.tif', '.jpg'), bbox_inches='tight')
                plt.show()
        
    data_major.append(major_axes)
    data_minor.append(minor_axes)
    data_coords.append(coordinates) #centroid coordinates, a major axis point coordinate, a minor axis point coordinate


#%% major axis swarm plot
sns.set(rc={'figure.figsize':(3,4)})
sns.set(font_scale=2)
sns.set_style("ticks")
sns.set_palette(sns.color_palette(colors))

ax = sns.swarmplot(data=data_major, size=5)

# plot the mean line
sns.boxplot(showmeans=True,
            meanline=True,
            meanprops={'color': 'black', 'ls': '-', 'lw': 2},
            medianprops={'visible': False},
            whiskerprops={'visible': False},
            zorder=10,
            data=data_major,
            showfliers=False,
            showbox=False,
            showcaps=False,
            width=0.25,
            ax=ax)

ax.set(xticks=[])
ax.set(yticks=[10,20,30,40,50])
# plt.savefig(savingDirectory+"AxisLength_Major"+str(datasets)+".png", bbox_inches='tight')
plt.show()

#%% minor axis swarm plot
sns.set(rc={'figure.figsize':(3,4)})
sns.set(font_scale=2)
sns.set_style("ticks")
sns.set_palette(sns.color_palette(colors))

ax = sns.swarmplot(data=data_minor, size=5)

# plot the mean line
sns.boxplot(showmeans=True,
            meanline=True,
            meanprops={'color': 'black', 'ls': '-', 'lw': 2},
            medianprops={'visible': False},
            whiskerprops={'visible': False},
            zorder=10,
            data=data_minor,
            showfliers=False,
            showbox=False,
            showcaps=False,
            width=0.25,
            ax=ax)

ax.set(xticks=[])
ax.set(yticks=[0,10,20,30,40])
# plt.savefig(savingDirectory+"AxisLength_Minor"+str(datasets)+".png", bbox_inches='tight')
plt.show()

#%% Major & minor length same plot
colors = ["black", "white"]
edgecolors = ["black", "tab:blue"]

fig, ax = plt.subplots(figsize = [5,4])
plt.subplot
for dataset in range(len(datasets)):
    splot1 = plt.scatter(data_major[dataset], data_minor[dataset], c=colors[dataset], s =25, alpha = 1, edgecolors=edgecolors[dataset])
# ax.set_xlabel('Major axis length (µm)')
# ax.set_ylabel('Minor axis length (µm)')
plt.xlim([10,50])
plt.ylim([0,40])
plt.xticks(ticks=[10,20,30,40,50])
plt.yticks(ticks=[10,20,30,40])

plt.savefig(savingDirectory+"D-Plot-AxisLength_MinorvsMajor"+str(datasets)+".png", bbox_inches='tight')
plt.savefig(savingDirectory+"D-Plot-AxisLength_MinorvsMajor"+str(datasets)+".pdf", bbox_inches='tight')
plt.show()

#%% Export and save calculated data
for dataset in range(len(data_major)):
    np.savetxt(savingDirectory+"D-Data_SpindleAxesLengths_"+str(datasets[dataset])+".csv", 
               np.transpose([data_major[dataset], data_minor[dataset]]),
               delimiter =", ", 
               header="major_axis_length, minor_axis_length",
               fmt ='% s')

#%% Export and save stats
pmaj = stats.ttest_ind(data_major[0],data_major[1],equal_var=False) #Welch's ttest, compares means of populations with different SDs
pmin = stats.ttest_ind(data_minor[0],data_minor[1],equal_var=False) #Welch's ttest, compares means of populations with different SDs

file = open(savingDirectory+"D-Stats-AxisLength"+str(datasets)+".txt", "w")
file.write("datasets = " + str(datasets) + "\n")
file.write("n_spindles = [" + str(len(data_major[0])) + ", " + str(len(data_major[1])) + "]\n")

file.write("\nMajor Axis\n")
file.write("means = [" + str(np.mean(data_major[0])) +", " +str(np.mean(data_major[1]))+ "]\n")
file.write("std = [" + str(np.std(data_major[0])) +", " +str(np.std(data_major[1]))+ "]\n")# file.write("stds = " + str(stds) + "\n")
file.write("p_major = " + str(pmaj[1]) + "\n")

file.write("\nMinor Axis\n")
file.write("means = [" + str(np.mean(data_minor[0])) +", " +str(np.mean(data_minor[1]))+ "]\n")
file.write("std = [" + str(np.std(data_minor[0])) +", " +str(np.std(data_minor[1]))+ "]\n")# file.write("stds = " + str(stds) + "\n")
file.write("p_minor = " + str(pmin[1]))
file.close()