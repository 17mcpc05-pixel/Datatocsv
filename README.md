# A multi-sensor dataset with annotated activities of daily living recorded in a residential setting

This readme file relates accompanies the dataset assets outlined in the paper:  

> A multi-sensor dataset with annotated activities of daily living recorded in a residential setting, Emma L. Tonkin, Michael Holmes, Hao Song, Niall Twomey, Tom Diethe, Meelis Kull, Miquel Perello Nieto, Massimo Camplani, Sion Hannuna, Xenofon Fafoutis, Ni Zhu, Przemysław R. Woznowsk, Gregory J. L. Tourte, Rául Santos-Rodrıguez, Peter A. Flach, and Ian Craddock

This work expands on the earlier work (cited below) by releasing the private labels that were not publicly available.  

> Niall Twomey, Tom Diethe, Meelis Kull, Hao Song, Massimo Camplani, Sion Hannuna, Xenofon Fafoutis, Ni Zhu, Pete Woznowski, Peter Flach, and Ian Craddock. _The SPHERE Challenge: Activity Recognition with Multimodal Sensor Data_. 2016.

This dataset was updated on 2022-11-03 with extensive additional data, as well as being reorganised to facilitate accessibility and reusability. 

## Introduction

The task of this challenge is to predict aspects the activities of residents within a smart home based only on observed sensor data. Sensor data are obtained from the following three sensing modalities:

* A wrist-worn accelerometer
* Video + Depth (RGB-D)
* Passive environmental presence sensors

The data and file formats are described in the following sections.

## Data Records

Much of what is found in this section can also be found in Section 3 in the paper titled "A multi-sensor dataset with annotated activities of daily living recorded in a residential setting."

This dataset provides three views of the data: `raw`, `sphere-challenge-2016` and `sphere-challenge-complete-2022`, each of which can be found under the `data` directory, and are described below: 

1. The `raw` view consists of the full, complete and un-shuffled data (in interval and tabular form) and labels. 
2. `sphere-challenge-2016` is a replication of the SPHERE Challenge that took part in ECML 2016, but with more consistent cross-modality naming conventions and activity/location labels of the test set. Train and test data are created in such a way that every user from the test set can be found in the train set. The data for this view was shuffled and randomly sliced in order to force the participants of the challenge to learn activity and location recognition models rather than memorising the script. 
3. Finally, the `sphere-challenge-complete-2022` has preserved the train and test splits from the SPHERE Challenge and the sequences are provided in un-sliced format. This means there are fewer sequences in this view, but each sequence is long (approximately 30 mins). 

The data provided in the `sphere-challenge-2016` and `sphere-challenge-complete-2022` views are provided in dense, CSV format (ie, raw interval data are not provided), and the code that produces these views can be found in texttt{main.py

All processed data are marked with unique codes (each recording will be referred to as a 'sequence folder'). Timestamps are re-based to be relative to the start of the sequences, i.e., each sequence always starts from `t = 0`. However, individual CSV files begin with an offset that reflects the time between the timestamp at which the sequence began and the datetime at which the first subsequent data point was generated: for example, accelerometer data may begin some milliseconds following `t = 0`, while video data, which is event-driven, may begin long after `t = 0` or not appear in a certain sample at all.

Each sequence folder contains the following files for sensor data: 

- `pir.csv` and/or `pir_raw.csv`
- `acceleration.csv`
- `rssi.csv`
- `rgbd_hall.csv`
- `rgbd_living.csv`
- `rgbd_kitchen.csv`
- `meta.json`

And a set of files for the annotations with the following name formats: 

- `activity.csv`
- `location.csv`
- `per_ann_activity_*.csv` and/or `activity_*_raw.csv`
- `per_ann_location_*.csv` and/or `location_*_raw.csv`

Here `*` will be a positive integer indicating corresponding annotator. That is, having two files as `per_ann_activity_1.csv` and `per_ann_activity_2.csv` means there are two different annotators for the activity labels. The `activity.csv` and `location.csv` files contain the merged ground-truth from all annotators. 



### DATA FILES

Figures showing examples of each data sequence can be found in the accompanying paper. 

#### `pir_raw.csv`

This file contains the start time and duration for all PIR sensors in the smart environment. PIR sensors are located in the following nine rooms: `bath`, `bed1`, `bed2`, `hall`, `kitchen`, `living`, `stairs`, `study`, `toilet`. The columns of this CSV file are:

 - `start`: the start time of the PIR sensor (relative to the start of the sequence)
 - `end`: the end time of the PIR sensor (relative to the start of the sequence)
 - `name`: the name of the PIR sensor being activated (from the `./assets/pir_locs.json` list)
 - `index`: the index of the activated sensor from the texttt{pir_locations

Note, the PIR sensors can be noisy (i.e. the sensors can trigger due to causes other than from people) as they are based on infra-red technologies, which can be affected by strong natural light. 

#### `pir.csv` 

This file contains the PIR data processed and sampled at a 0.1s period (for `raw` views) or 1.0s (for the `sphere-challenge-2016` and `sphere-challenge-complete-2022` views). The file consists of dense binary data for each PIR location (`bath`, `bed1`, `bed2`, `hall`, `kitchen`, `living`, `stairs`, `study` and `toilet`) and one supplementary column containing time.

#### `acceleration.csv` 

The acceleration file consists of four columns:

 - `t`: this is the time of the recording (relative to the start of the sequence)
 - `x`, `y`, `z`: these are the acceleration values recorded on the x/y/z axes of the accelerometer. 

#### `rssi.csv`
            
The RSSI file consists of five columns:

 - `t`: this is the time of the recording (relative to the start of the sequence)
 - `kitchen`, `living`, `study`, `stairs`: these specify the RSSI signal as received by each access point. Empty values indicate that the access point did not receive the packet. 

#### `rgbd.csv` 

The following sixteen columns are found in the `rgbd_hallway.csv`, `rgbd_kitchen.csv` and `rgbd_living.csv` files:

 - `t`: The current time (relative to the start of the sequence)
 - `centre_2d_x`, `centre_2d_y`: The x- and y-coordinates of the centre of the 2D bounding box. 
 - `bb_2d_br_x`, `bb_2d_br_y`: The x and y coordinates of the bottom right (br) corner of the 2D bounding box 
 - `bb_2d_tl_x`, `bb_2d_tl_y`: The x and y coordinates of the top left (tl) corner of the 2D bounding box
 - `centre_3d_x`, `centre_3d_y`, centre_3d_z: the x, y and z coordinates for the centre of the 3D bounding box
 - `bb_3d_brb_x`, `bb_3d_brb_y`, `bb_3d_brb_z`: the x, y, and z coordinates for the bottom right back (brb) corner of the 3D bounding box
 - `bb_3d_flt_x`, `bb_3d_flt_y`, `bb_3d_flt_z`: the x, y, and z coordinates of the front left top (flt) corner of the 3D bounding box. 

### Annotation files 

The following two sets of files need not be used for the challenge, but are included to facilitate users that wish to perform additional modelling of the sensor environment. For example, indoor localisation can be modelled with the `locations.csv` file. 

#### `activity_*_raw.csv`
        
This file provides the individual activities as provided by the annotators. The target variables are the same as for `./assets/activity_labels.csv`. 

The following 20 activities are annotated: `a_ascend`, `a_descend`, `a_jump`, `a_loadwalk`, `a_walk`, `p_bent`, `p_kneel`, `p_lie`, `p_sit`, `p_squat`, `p_stand`, `t_bend`, `t_kneel_stand`, `t_lie_sit`, `t_sit_lie`, `t_sit_stand`, `t_stand_kneel`, `t_stand_sit`, `t_straighten`, `t_turn`.

As before, the prefix `a_` indicates an ambulation activity (i.e., an activity consisting of continuing movement), `p_` annotations indicate static postures (i.e., times when the participants are stationary), and `t_` annotations indicate posture-to-posture transitions. 

The file `activity_*_raw.csv` contains the following four columns:

 - `start`: the start time of the activity (relative to the start of the sequence)
 - `end`: the end time of the activity (relative to the start of the sequence)
 - `name`: the name of the label (from the set of locations found in `./assets/activity_labels.json`)
 - `index`: the index of the label name in `activity_labels`

#### `location_*_raw.csv`

This file provides the annotation labels for room occupancy. The same nine rooms are labelled as seen with the PIR sensor: `bath`, `bed1`, `bed2`, `hall`, `kitchen`, `living`, `stairs`, `study`, `toilet`.
            
The file `location_*_raw.csv` contains the following four columns:

 - `start`: the time a participant entered a room (relative to the start of the sequence)
 - `end`: the time the participant left the room (relative to the start of the sequence)
 - `name`: the name of the room (from the set of locations found in `./assets/location_labels.json`)
 - `index`: the index of the room name starting at 0

#### `activity.csv` and `location.csv`

The `activity.csv` and `location.csv` files contains the aggregated ground-truth from multiple annotators on the activities and locations. As briefly introduced previously, the annotations are separated into a one-second time window. Within each window, the annotated length of each activity from each annotator is calculated, the final ground-truth is given as the normalised total annotated time for every activity (e.g., the rows sum to one). 

The `activity.csv` files are dense CSV with columns corresponding to time and the labels listed in `./assets/activity_labels.json`. Similarly, `location.csv` files are also in dense CSV format, but with columns corresponding to those in `./assets/location_labels.json`.

#### `per_ann_activity_*.csv` and `per_ann_location_*.csv`

These files provide a dense binary CSV file of each annotator for activity and location. Averaging over the set of annotation files will produce the data in the previous section. The columns of `per_ann_activity_*.csv` are the activity labels from `./assets/activity_labels.json`, and the columns of `per_ann_location_*.csv` are the location labels from `./assets/location_labels.json`. 


### METADATA

#### `test_index_lookup.csv` 
This file contains the details needed to convert from the `raw` format to `sphere-challenge-2016` format. 

#### `accel_keys.json`
This file contains the order of the accelerometer axes (i.e. x, y, z)

#### `activity_labels.json`
This file contains all of the activity labels.

#### `activity_weights.json`
The original SPHERE Challenge rewarded the detection of the rarer activities more than others. This file consists of the weights used in the challenge.

#### `ap_locs.json`
This file contains the name of the access points in the house.

#### `location_labels.json`
This file lists all of the rooms found in the house in which the data was collected.

#### `pir_locs.json`
This file contains the locations of the PIR sensors.

#### `rgbd_locs.json`
This file contains the locations of the video sensors.

#### `video_feature_names.json`
This file contains the feature names of the video sensors, and their dimensionalities.

#### `video_feature_strucutre.json `
This file aggregates the RGBD columns based on those 

#### `meta.zip` 
This file contains meta data regarding the sensor names, room names, activity names, all in JavaScript Object Notation (JSON) format. This contains the following files:

#### `supplementary.zip` 
This contains floor-plans of the house, images from the three cameras, and the script used for the training data collection. This contains the following files:

# Use of the data

The data are in platform-independent CSV format, with JSON-formatted metadata. While any operating system can be used to make use of the data, sample code is provided in the Git repository at `https://github.com/IRC-SPHERE/sphere-challenge/` - this code makes use of standard libraries for Python including numpy, pandas, json and matplotlib. 

# Licence

This dataset is released as open data under the CC-BY licence: see `https://creativecommons.org/licenses/by-sa/4.0/` and `https://data.bris.ac.uk/data/licence` for further information. 
