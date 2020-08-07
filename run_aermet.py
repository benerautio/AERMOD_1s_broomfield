import subprocess
import pathlib
import os

sfc_file = pathlib.Path("../SFC/sfc_for_aermod.SFC")
pfl_file = pathlib.Path("../PFL/pfl_for_aermod.PFL")

#This grabs the correct entry from the met data that was just run through AERMET, and puts it in a SFC and PFL file
#to run through AERMOD. It also determines if there is enough extraced data to run AERMOD (24 entries). It also runs if it 
#hits EOF of the data file.
def __extract(cur_hour,sim_day,first,last):
    with open('../SFC/1S_AERMOD_SURFACE.SFC','r') as sfc:
        lines = sfc.readlines()
        entry = lines[cur_hour+(sim_day*24)]
        header = lines[0]

        if sfc_file.exists() and first == False:
            with open('../SFC/sfc_for_aermod.SFC','r') as f:
                hr = len(f.readlines())
            if hr == 25:
                hr = 0
                with open('../SFC/sfc_for_aermod.SFC','w') as f:
                    first_lines = [header,entry[:12]+' 1'+entry[15:]]
                    f.writelines(first_lines)
            else:
                with open('../SFC/sfc_for_aermod.SFC','a') as f:
                    f.write(entry[:12]+' '+str(hr)+entry[15:])

        else:
            with open('../SFC/sfc_for_aermod.SFC','w') as f:
                first_lines = [header,entry[:12]+' 1'+entry[15:]]
                f.writelines(first_lines)

    with open('../PFL/1S_AERMOD_PROFILE.PFL','r') as pfl:
        lines = pfl.readlines()
        entry = lines[cur_hour-1+(sim_day*24)]

        if pfl_file.exists() and first == False:
            with open('../PFL/pfl_for_aermod.PFL','r') as f:
                hr = len(f.readlines())+1
                if hr == 24:
                    ret = True
                else:
                    ret = False
            if hr == 25:
                hr = 0
                with open('../PFL/pfl_for_aermod.PFL','w') as f:
                    f.write(entry[:8]+'  1  '+entry[15:])
            else:
                with open('../PFL/pfl_for_aermod.PFL','a') as f:
                    f.write(entry[:8]+'  '+str(hr)+'  '+entry[15:])
                    if last == True:
                        ret = True
        else:
            with open('../PFL/pfl_for_aermod.PFL','w') as f:
                f.write(entry[:8]+'  1  '+entry[15:])
                ret = False

    os.chdir('../../../../python_path_simulation/')
    return ret

#Runs 3 stages of AERMET by calling a shell script
def run(write, cur_time, cur_hour, van_path, first, last, sim_day,skip):

    try:
        os.chdir('../AERMOD_paths/'+van_path+'/AERMET/broomfield')
    except FileNotFoundError:
        print(van_path+' path does not exist')

    print('Writing Met Data for: '+ cur_time)
    with open('met_data_1s/data.met','w') as f:
        f.writelines(write)

    if skip == False:
        #Redirects stdout from AERMET to bit bucket because there is a lot
        FNULL = open(os.devnull, 'w')
        print('Running AERMET for '+cur_time+'...')
        subprocess.call(['sh','./run_3_stages.sh'],stdout=FNULL)
        print('AERMET Done')

        print('Extract data for current hour...\n')

        #Write to PFL and SFC for input to aermod
        ret = __extract(cur_hour,sim_day,first,last)

    else:
        ret = __extract(cur_hour,sim_day,first,last)

    return ret