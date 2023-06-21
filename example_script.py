# Example script for running the different modules together.

from subprocess import run

# Specify the path where both the mp4 and folder containing jsons are located.
video_path = ''

# Specify the name of the video that was the input for videopipe.
# Should be same as the folder name containing the jsons as well as
# the name of the jsons without the task postfix.
v_name = 'Making_of_Rijksmuseum_[Be7Yq5lBbcA]'

# Specify the task postfix for the json.
task= '_face_detection_datamodel'

# Specify the output filename for the video.
output_filename = 'fd'

# Specify the name of the input mp4.
# If the input filename is left empty, it will be set to
# the same as the v_name field.
input_filename = 'rijksmuseum'

run(['python3', 'videopipe_viz/face_detection.py', video_path, v_name, task, output_filename, input_filename])

task = '_text_detection_datamodel'
output_filename = 'fd_td'
input_filename = 'fd'

run(['python3', 'videopipe_viz/text_detection.py', video_path, v_name, task, output_filename, input_filename])

task = '_shot_boundaries_datamodel'
output_filename = 'fd_td_sd'
input_filename = 'fd_td'

run(['python3', 'videopipe_viz/shot_detection.py', video_path, v_name, task, output_filename, input_filename])
