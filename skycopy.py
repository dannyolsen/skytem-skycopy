import os, sys, threading, cursor, json
#import threading
#import cursor
#import json

import functions #py file with my functions

from time import sleep
from colorama import Fore, init
init()

from art import text2art

##################################################################################################
print(text2art('SkyCopy'))
print('-------------------------------------------------------------')
print('Version 1.6 - 4th of June 2024 - Danny Olsen (dol@skytem.com)')
print('-------------------------------------------------------------\n')
print('This program will copy all helivideos to specified folder.\n')
##################################################################################################

print("Updates:")
print("1. Autoadjust for time difference - UTC -> Local time")
print("2. Program will always copy files to the directory where the .exe files is located")
print("3. Auto finding video split - make sure you have a full flight on the SD card for this to be correct!!")

"""
Play audiofile


from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import which
#audio = AudioSegment.from_file(r'audio\skycopy1.5.m4a')

# Set the path to ffmpeg if it's not in the system PATH
AudioSegment.converter = which("ffmpeg")

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        #base_path = sys._MEIPASS
        base_path = os.getcwd()
        print(base_path)
    except Exception:
        #base_path = os.path.abspath(".")
        base_path = os.getcwd()

    return os.path.join(base_path, relative_path)

# Load your m4a file
audio_file_path = resource_path(r'audio\skycopy1.5.m4a')
audio = AudioSegment.from_file(audio_file_path, format="m4a")
# Play the audio file
play(audio)
"""


###### TEST VARIABLE ######
testing = False #Testing will run with preset source and destination - False with run program as production code
###########################

#region Set destination dir and source dir
if testing == True:
    #path_settings = os.path.join(os.getcwd(), 'skycopy_settings.json')
    path_settings = os.path.join(r'C:\Users\dol\Desktop\SkyCopyTest','skycopy_settings.json') #where the settings file need to go

    if os.path.exists(path_settings) == False:
        data = {    "source_mov": r'C:\Users\dol\Desktop\SkyCopyTest\source', 
                    "destination_mov": r'C:\Users\dol\Desktop\SkyCopyTest\destination'}

        #path_settings = data['destination_mov']

        with open(path_settings, 'w') as f:
                json.dump(data, f)
    
    else:
        with open(path_settings) as f:      #loading existing settings file into program
            data = json.load(f)
    
    os.chdir(os.path.normpath(r'C:\Users\dol\Desktop\SkyCopyTest'))

else:
    path_settings           = os.path.join(os.getcwd(), 'skycopy_settings.json')

    if os.path.exists(path_settings) == True:
        with open(path_settings) as f:
            data = json.load(f) 

        if functions.get_sd_driveletter() != 'na':    #hvis der bliver fundet en sti til sd kort
            drive_autodetect = True
            data['source_mov'] = os.path.normpath(functions.get_sd_driveletter())
            
            """with open(path_settings, 'w') as f:
                json.dump(data, f)"""

        elif functions.get_sd_driveletter() == 'na' and 'source_mov' not in data:
            print('{}Program was unable to determine SD drive letter automatically - please do it manually!{}\n'.format(Fore.YELLOW, Fore.RESET))
            data['source_mov'] = input('What is the path to the mov files on the SD card?: ')

            with open(path_settings, 'w') as f:
                json.dump(data, f)
    
    else:
        print("skycopy_settings.json not found")
        print("Provide source and destination lib. This only has to be done once.")
        print("After initial setup changes can be made in the skycopy_settings.json file\n")

        if functions.get_sd_driveletter() == 'na':
            source_mov  = input('What is the path to the mov files on the SD card?: ')

            if not os.path.exists(source_mov):
                print("Source path does not exist")
            else:
                print("Source path found - continueing")
        else:
            source_mov  = os.path.normpath(functions.get_sd_driveletter())     
        
        #destination_mov = input('Where do you want this program to sort the mov files to?: ')
        destination_mov = os.getcwd()

        # Take input from user in the format of hh:mm:ss
        #time_str = input("Enter video split time in hh:mm:ss format: ")
        time_str = functions.longest_mov_duration(source_mov)

        # Split the input string into hours, minutes, and seconds
        hours, minutes, seconds = map(int, time_str.split(':'))


        print("Timedelta usually should be set to 0, but if the videos end up in the wrong folders you can use timedelta to compensate for this")
        timedelta = functions.hours_offset_utc_local()   #timedelta will add this amount of hours to the date modified end up in the right folder - this was an issue in AU 10109

        data = {"source_mov"       : source_mov, 
                "destination_mov"  : destination_mov,
                "videosplit" : { 
                    "hh" : hours,
                    "mm" : minutes,
                    "ss" : seconds
                    },
                "timedelta" : timedelta    
                }

        with open(path_settings, 'w') as f:
            json.dump(data, f)



#endregion

###### MAIN PROGRAM #####
data = functions.setup_video_lengths(path_settings, **data)

print('Copying from {} to {}'.format(data['source_mov'], data['destination_mov']))

t_copy = threading.Thread(target=functions.sort_files_in_folder, kwargs=(data))
t_copy.start()
sleep(0.1)

dest_start_end_size = functions.copy.get_dest_start_end_size(data['destination_mov'], data['source_mov'])
while t_copy.is_alive() == True:
    sleep(0.2)
    cursor.hide()
    status = functions.copy.progress(data['destination_mov'], data['source_mov'], dest_start_end_size)
    print(f"Overall progress {status}%   ", end='\r')

copy_progress = 100.0

mov_copied = True

if mov_copied == True:
    print(r'{}{}% copied{}'.format(Fore.GREEN, copy_progress, Fore.RESET), end='             ')
    print()

functions.label_and_remove(data['destination_mov'], data)

d = input("Do you want to delete the content of the SD card? (y/n): ")
if d == 'y':
    functions.delete_sd(data['source_mov'])

input(f"{Fore.GREEN}PRESS ENTER TO QUIT PROGRAM{Fore.RESET}")   #this is so the user has a chance to read the terminal info before the windows closes