import os
import os.path, time
import logging
from logging import exception
from pymediainfo import MediaInfo
import shutil
from colorama import Fore, Style, Back

from datetime import datetime

import json

class video:
    def get_ms(filename):
        #length will be returned in ms
        clip_info           = MediaInfo.parse(filename)
        duration_ms         = clip_info.tracks[0].duration
        duration_s          = duration_ms/1000
        minutes_quotient    = int(duration_s//60)
        minutes_remainder   = int(duration_s%60)

        mov_length  = f'{filename} is {minutes_quotient}:{str(minutes_remainder).zfill(2)}'

        return duration_ms

    def get_strLength(filename):
        #length will be returned in human readable format
        clip_info           = MediaInfo.parse(filename)
        duration_ms         = clip_info.tracks[0].duration
        duration_s          = duration_ms/1000
        minutes_quotient    = int(duration_s//60)
        minutes_remainder   = int(duration_s%60)

        mov_length  = f'{filename} is {minutes_quotient}:{str(minutes_remainder).zfill(2)}'

        return mov_length

class copy:
    def log(source_log, destination_log):
        if os.path.exists(source_log) == True:
            try:
                shutil.copytree(source_log, destination_log)
                print('{}Log copy complete!{} \n'.format(Fore.GREEN, Fore.RESET))
                log_copied = True

            except FileExistsError:
                print('LOG NOT copied! - Destination folder already exist')

            except Exception as e:
                print("LOG NOT copied! - source folder was probably empty\n")
                print(e)
        else:
            print(f"{source_log} does not exist - {Fore.RED}log NOT copied...{Fore.RESET}\n")
    
    def get_dest_start_end_size(destination_mov_base, source_mov):
        #returning the start and end size of destination dir
        bytes_per_mb  = 1048576
        bytes_per_gb  = 1073741824
        size_destination        = round(folder_size_recursive(destination_mov_base)/bytes_per_gb,2)
        size_source             = round(folder_size_recursive(source_mov)/bytes_per_gb,2)
        dest_end_size           = size_destination+size_source

        return size_destination, dest_end_size

    def progress(destination_mov_base, source_mov, dest_start_end_size):
        #The destination_mov_base is the folder in which the date-folders are placed
        #The source mov is the folder from which the mov files are being copied
        bytes_per_mb  = 1048576
        bytes_per_gb  = 1073741824

        dest_start_size = dest_start_end_size[0]
        dest_end_size   = dest_start_end_size[1]

        size_destination        = round(folder_size_recursive(destination_mov_base)/bytes_per_gb,1)
        #size_source             = round(folder_size_recursive(source_mov)/bytes_per_gb,1)

        status = round(((size_destination-dest_start_size)/(dest_end_size-dest_start_size))*100,1)

        return status

def get_sd_driveletter():
    path    = '{}:\\DCIM\\100_AIM_'
    dl      = ['d','e','f','g']
    
    for i in dl:
        path_to_check   = path.format(i)
        path_exist      = os.path.exists(path_to_check)

        if path_exist == True:
            break

        else:
            path_exist  == False

    if path_exist == True:
        return path_to_check
    
    else:
        return 'na'

def get_folder_name_from_file(file):
    date_string = (time.ctime(os.path.getmtime(file)))
    date_object = datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y")
    folder      = date_object.strftime("%Y%m%d")

    return folder

def get_folder_name_from_DCIM(path):
    d = []

    entries = os.listdir(path)

    for i in entries:
        date_string     = (time.ctime(os.path.getmtime(path+'\\'+i)))
        date_object     = datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y")
        folder          = date_object.strftime("%Y%m%d")
        d.append(folder)
    
    if d == []:
        return 'na'
    
    else:
        return(max(d))

def label_and_remove(destination_mov, settings):
    m_short                     = int(settings['no_flight'])
    m_prod                      = int(settings['production_flight'])
    m_split_hour                = int(settings['videosplit']['hh'])
    m_split                     = int(settings['videosplit']['mm'])
    m_split_sec                 = int(settings['videosplit']['ss'])-1
    # m_split_hour                = 0
    # m_split                     = 59.1667

    print('From skycopy_settings.json: ')
    print(f'Videos shorter than {m_short} minutes was not be copied to harddrive') #They will be labelled short flights before deletion
    print(f'Videos longer than  {m_short} minutes and shorter than {m_prod} minutes was labelled short flights')
    print(f'Videos longer than  {m_prod}  minutes was labelled production flights\n')

    print(f'Video split is at : {m_split_hour}h{m_split}m{m_split_sec}s or above')

    ms_min_short_flight         = m_short*60*1000
    ms_min_prod_flight          = m_prod*60*1000
    ms_prod_flight_split_length = m_split_hour*3600*1000 + m_split*60*1000 + m_split_sec*1000

    entries_n     = os.listdir(destination_mov) #get list of files in dir
    entries_n   = [n for n in entries_n if n.isdigit()]

    for n in sorted(entries_n):
        no_flight_number            = 0
        short_flight_number         = 0
        prod_flight_number          = 0

        if os.path.exists(os.path.join(destination_mov,n,'DCIM')):
            subdir = 'DCIM'

        else:
            subdir = ''
            
        entries_i   = os.listdir(os.path.join(destination_mov,n,subdir))

        flag_prod_flight    = False
        prod_flight_number  = 0
        for i in sorted(entries_i):
            path_i = os.path.join(destination_mov,n,subdir,i)

            filename, file_extension = os.path.splitext(i)

            if file_extension == '.MOV':
                try:
                    ms = video.get_ms(path_i)
                    logging.info("ms for {} is {}".format(i,ms))

                    if ms < ms_min_short_flight:
                        if flag_prod_flight != True:
                            no_flight_number += 1
                            text            = '_no_flight'
                            flight_number   = no_flight_number
                        
                        else:
                            pass

                        flag_prod_flight = False

                    elif ms >= ms_min_short_flight and ms < ms_min_prod_flight:
                        if flag_prod_flight != True:
                            short_flight_number += 1
                            text            = '_short_flight'
                            flight_number   = short_flight_number
                        
                        else:
                            pass

                        flag_prod_flight = False

                    elif ms >= ms_min_prod_flight and ms < ms_prod_flight_split_length:
                        if flag_prod_flight != True:
                            prod_flight_number += 1
                            text            = '_production'
                            flight_number   = prod_flight_number
                        
                        else:
                            pass

                        flag_prod_flight = False

                    elif ms >= ms_prod_flight_split_length:
                        if flag_prod_flight != True:
                            prod_flight_number += 1
                            text            = '_production'
                            flight_number   = prod_flight_number
                        
                        else:
                            pass

                        flag_prod_flight = True    
                    
                    if text in i:
                        pass            #if filed already named - do nothing
                    
                    else:
                        old_name    = path_i
                        i_split     = path_i.split('.',2)    #split filename in two by seperator .
                        new_name    = f'{i_split[0]}{text}{flight_number}.{i_split[1]}'

                        os.rename(old_name, new_name)

                except Exception as e:
                    path = os.path.join(destination_mov,n,subdir,i)
                    os.remove(path)
                     
                    print(f'{Fore.RED}{i} is corrupt - file deleted...{Fore.RESET}')

            else:
                #os.remove(f'{destination_mov}\\{i}') #REACTIVATE FOR PRODUCTION
                #print(f'{i} - not .mov file')
                pass
 
        print(f'{Fore.YELLOW}{prod_flight_number} registered production flights in {n}{Fore.RESET}')

def del_noflights(destination_mov):
    print()
    #print("Removing no_flight videos")

    entries_n       = os.listdir(destination_mov) #get list of files in dir
    entries_n       = [n for n in entries_n if n.isdigit()]

    rm_counter = 0
    for n in entries_n:
        # LABEL AND REMOVE

        if os.path.exists(os.path.join(destination_mov,n,'DCIM')):
            subdir = 'DCIM'

        else:
            subdir = ''

        entries_i   = os.listdir(os.path.join(destination_mov,n,subdir))

        for i in entries_i:
            #path_i = destination_mov+'\\'+n+'\\'+'DCIM\\'+i
            path_i = os.path.join(destination_mov,n,subdir,i)
            if 'no_flight' in i:
                os.remove(path_i)
                print(f'{i} removed in {n}')
                rm_counter += 1

    if rm_counter > 0:
        print()      
        print(f'{Fore.YELLOW}{rm_counter} short flight files removed from target{Fore.RESET}\n')

def delete_sd(mov_path):
    some_files_where_removed = False

    entries = os.listdir(mov_path)

    print("Removing mov files from source library\n")
    for n in entries:
        f = os.path.join(mov_path,n)
        os.remove(os.path.join(f))
        print(f"{f} removed")
    
def sort_files_in_folder(**data):
    entries = os.listdir(data['source_mov'])
    for i in entries:
        src_file        = os.path.join(data['source_mov'],i)
        date_folder     = get_folder_name_from_file(src_file)
        dest_file       = os.path.join(data['destination_mov'],date_folder,i)
        target_folder   = os.path.join(data['destination_mov'],date_folder)
        gopro_no        = i.split('.',1)[0]
        
        if os.path.exists(target_folder) == False:
            os.makedirs(target_folder)

        entries_target = os.listdir(target_folder)
        gopro_no_exists = False
        for y in entries_target:
            if gopro_no in y:
                gopro_no_exists = True
                break
            else:
                pass

        try:
            video_length_s = video.get_ms(src_file)/1000/60

        except:
            video_length_s = 0

        filename, file_extension = os.path.splitext(i)

        if video_length_s == 0:
            print(f'{i} not copied - file corrupt')
            continue

        elif file_extension != '.MOV':
            print(f"{i} not copied - not .mov file")
            continue

        elif video_length_s < int(data['no_flight']):
            print(f'{i} not copied - no_flight video')
            continue

        elif gopro_no_exists:
            print("{0}{1} not copied - exists on target already{2}".format(Fore.LIGHTBLACK_EX, i, Fore.RESET))
            continue

        elif os.path.exists(target_folder) and not gopro_no_exists:
            #get list of files in dir
            shutil.copyfile(src_file, dest_file)

        else:
            print(f"{src_file} not copied - unknown reason")
            pass

def folder_size_recursive(path):
    bytes_per_mb  = 1048576
    bytes_per_gb  = 1073741824

    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += folder_size_recursive(entry.path)

    return total

def setup_video_lengths(path_settings, **data):
    if 'no_flight' not in data or 'production_flight' not in data: 
        print("Define values for the skycopy_settings.json - this only has to be done one time/n")
        #nf = input('Do not copy videos under x minutes (recommended 10 mins): ')
        #pf = input('Label videos over x minutes as production_flights (recommended 30 mins): ')

        nf = 10
        pf = 30
        print(f'Videos between {nf} and {pf} minutes will be labelled short_flights')
    
        data["no_flight"] = nf
        data["production_flight"] = pf

        with open(path_settings, 'w') as f:
            json.dump(data, f)

    else:
        pass
        
    nf = data['no_flight']
    pf = data['production_flight']

    print('Current settings are : ')
    print(f'Delete videos under {nf} minutes')
    print(f'Label videos over {pf} minutes as production flights')
    print()
    print('{}If you want to change settings - edit skycopy_settings.json{}'.format(Fore.YELLOW, Fore.RESET))

    return data

if __name__ == '__main__':
    print(get_sd_driveletter())


