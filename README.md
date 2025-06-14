# Segmentation-Tool
This is a pyqt based project for Video and Image Segmentation.
Multi-threading is handled by Qthreads to ensure real-time processing of video. 

Current Features:
 
 Mulit-Class Color Segmentation:
    
[color_space_options.webm](https://github.com/user-attachments/assets/0d967b6d-634c-4968-8207-c25b20f10ae0)

     Color Space Modes:
       
       i.   RGB.
       ii.  HSV.
       iii. LAB.
       iv.  YCrCb.
       v.   YUV.
       vi   LUV.
       
   
 Morphological Operations:
 
    Operation Options:
           
      i.   Erosion.
      ii.  Dilation.
      iii. Opening.
      iv.  Closing.
      v.   Gradient.
      vi.  Top Hat.

Contour Finding:

    Modes:
      i. Outer Contours.
      ii. All Contours
    
    Approximation Options:
      i.   Simple.
      ii.  Full.
      iii. Teh Chin L1.
      iv.  Teh Chin KCOS.
    
    Bounds:
      i.   Bounding Boxes.
      ii.  Rotated Boxes.
      iii. Circle.
      iv.  Elipses.
      v.  Convex Hull.

Background Subtraction:
  
    Modes:
    
     i.  MOG.
     ii. KNN.
