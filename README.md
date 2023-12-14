# Dependencies:
python 3.8+  
Vispy  
PyQt5  
numpy  
pandas
scipy

With python and pip installed, navigate to the directory containing requitements.txt, open the terminal and type:
    pip install --user -r requirements.txt
This will install all of the required libraries.
Now, in the same terminal, navigate to the src directory:
   cd src
and run the python module main.py:
  python main.py

If there is an error saying that "python" or "pip" is an unknown command, it is likely that you have not updated your PATH variable to include the path to the python binary.


# Data:
By default, subject directories are expected to be located at *../data/VR-S1/Hand*, relative to the
main.py module.  
This may be changed via **File**->**Subject directory...** . Select the directory containing the separate
subject directories, eg. P01, P02, etc

By default, object input files are expected to be located at *../data/VR-S1/Objects*, relative to the
main.py module.  
This may be changed via **File**->**Object directory...**

# Use:
## ADDING PLOTS:
Plots are added via the "Add Patch" button at the top of the left panel. This opens a dialog to
specify the plot parameters.

The dropdown at the top of this new dialog window allows the user to input either a custom
trajectory specification (default), a preset trajectory specification, or an object specification.

### Custom trajectory:
This window is divided into three columns. Most options should be self explanatory, less intuitive
ones are described below.
Once the appropriate plot parameters are set, click "Add trajectory" to plot the data. Note that if
many subjects are to be plotted, this may take several seconds to complete.

The first column contains options for selecting which subjects' data to plot.
***NOTE***: If no subject labels are present in the "Select" dropdown or "Custom Group" lists, this indicates
that an incorrect location for the subject data has been set, and should be adjusted as above.

To select a custom set of subjects, first select the "Custom group" toggle, then click the "Create
group" button. This will open a new dialog window with two lists. The left list contains all
subjects to be used in the current plot (empty by default), and the right list contains all
available subjects. 
Subjects maybe added into the current plot by dragging their label from the right list to the left
list. Multiple subjects may be select at once by holding "ctrl" or "shift" while clicking on
labels, and then dragging for right to left as usual.

The second column contains what selection criteria to apply to the dataset. Congruency and/or congruency of
previous trial may be selected using the radio buttons, or any available criteria (including congruency) may be selected using the "Set custom criteria" button.
If the selection criteria eliminates all possible trials, then no data will be plotted.

The third column contains options for plotting averages and transformation of the data. To plot the
mean average of all plotted trials, check the "Plot mean trajectory" checkbox.
Transformations allow the data to with either a left or right target to be mirrored.
Total normalisation allows all trajectories to be transformed to originate from the same start
point (0, 0, 0).
"Per subject" normalisation allows for all subjects' first trajectory to originate from the same start point while
all subsequent trajectories to originate relative to that start point.

### Preset trajectory:
This window allows for multiple patches to be quickly added using common configurations.
Presets may be selected from the list in the first column.
Currently there is only one preset, which has congruent trials to be plotted left in one colour, while the
incongruent trials are plotted right in another colour. Subject selection and colours may be
adjusted as in the previous window.

### Object input:
This window allows data files to be loaded which specify parameters for one or more objects.
Firstly, the "Select input file" is used to choose a file.
Once a valid input file is selected, the "Add object" button will be enabled to press and add the
objects.


## EDITING PLOTS:
After a patch (plot or object) has been added. Its label will be visible in the list in the left
panel of the main window, and the plot itself will be visible in the right panel.

Individual plots may have their colour changed or be deleted by double clicking on the label, which
opens a new dialog window with these options.
