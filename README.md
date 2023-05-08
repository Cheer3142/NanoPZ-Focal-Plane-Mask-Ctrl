# Focal Plane Mask Control Using Nano-Piezo Actuator

The size of the mask can be varied by increasing/decreasing the force applied on the prism by the lens. 

![Mask_increasing_pressure.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/aee7c168-858b-49a0-b31b-7128555a174d/Mask_increasing_pressure.png)

EvWaCo Mini Prototype

![EvWaCo_mini.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/4747ee76-371d-470e-ab1d-541e3ed8230d/EvWaCo_mini.png)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f15e0682-3de2-4f56-a299-d0d4eb3f8151/Untitled.png)

The Nano-Piezo actuator (Ultra-High Resolution Motion System)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/8b781af2-dc7c-4e30-b163-afbf6b3ed025/Untitled.png)

The Point Grey Camera Model: GS3-PGE-23S6M-C (GigE camera)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/039a70f5-3dac-4c5d-b9e4-53818d62ec74/Untitled.png)

![Mask_control.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/cb26577c-bc97-4aa6-a198-b1aa63c2fc96/Mask_control.png)

Add pseudo-code of Matt’s algorithm: input, output

1. Set up variables for image processing, including the path to the image file, the size of a box to crop the image, and whether to use geometric
2. Begin a loop that continually checks for new files in the specified path
3. Load the most recent file in the path and apply a median filter to reduce noise
4. Find the darkest pixel (minimum light intensity) to determine the center
5. Ravel the image to apply a curve fit
6. Calculate the distances of all pixels from the center of the image
7. Calculate the full-width half maximum (FWHM) of the image and plot it on a graph

Main Objective:

The field to test and develop the sub-system before implementation in the EvWaCo prototype. 

![PZA_App.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/0275a2d7-bbc3-461f-9647-36f43ac1d8d3/PZA_App.png)

Problem statement:

There is an unknown delay when the command is sent to the actuator, and when this command can be seen by the camera. 

 

Critical Issues:

Firstly for the camera, I found that whenever re-opens it will need to force the camera to be on the same subnet. I learn the effects of some camera parameters such as exposure time if I use it too high the image will be saturated or if it is too low we might not see the object. Found that it can be possible that some frame data was incomplete and lost. Secondly, about the actuator, I found that whenever the user moves the actuator to any position after removing the power supply it will revert to zero. The user can move the actuator in two ways, one is to send the wanted position and the next is to set the speed. But sometimes the actuator does not move to the desired position and stops during the move. The last one is the prism can break if we set the speed to level 6.

I think the hardest problem that I am working with is the high delay between each frame of an image. The causes of this issue can be several, such as the camera parameters or image grabbing method. Moreover, this issue will need to be tested multiple times to find the solution and need to find the maximum expected latency.

Possible solutions:

The actuator does not record the latest position after the power is off, so I try to compensate for the position by having the offset value as a below chart.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/cb266c0c-8e6d-4c2b-a550-1ef19af68306/Untitled.png)

Drawbacks:
