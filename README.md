# VisualAnalyzer
VisualAnalyzer is a light assistant tool for image processing researchers. Besides, this cross-platform software is open scource. This program is copyright of Kyongson Jon & Jun Liu (2021) in Northeast Normal University. All rights reserved.
    VisualAnalyzer is able to kindly analyze the different suites of resultant images, by zooming-in, comparing, saving the ROI and its container with/without frame.
The images to be analyzed are assumed to:
1) be of equal size (e.g., 256x256, 1024x968, ...), 
2) have identical filename as of other directories. 

 Steps to use this program: 
 
1) Select several directories in which contains some images to analyze. 
2) Select a ground truth (i.e., a directory of ground-truth images) directory.
3) Click 'Analyze' button. When you click 'Next' button, the best candidate is saved in 'best' sub-folder, logging in 'best_log.txt' file.
4) You can select interesting regions and the zoomed-in patches will be shown continuously. Whenever pressing 'backspace' key, the previous state is reverted.
5) It is also possible to save the current patches and those containers with/without highlighted rectangle, by right-clicking in any image region and go through the 'save as' procedure.
6) Customizing the highlighting color and line-width is available by clicking setting.
7) the file name of the saved cropped image is with bottom-left and up-right coordinates.

# Usage
switch to the fold VisualAnalyzer, open terminal, input python main.py or python3 main.py, then press Enter

# Further exploration:
If you are latex user and need to display the zoom-in part in the corresponding image, we strongly recommend you to use ZoomInPortion tookkit. It is also available in github.  https://github.com/junliumath/ZoomInPortion

If you have any trouble using this program, please contact us via quanjx046@nenu.edu.cn or liuj292@nenu.edu.cn.
