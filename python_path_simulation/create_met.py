#Creates met file, Runs AERMET, Runs AERMOD.

import run_aermet
import run_aermod
import change_days

import sys
import os
from os import listdir
from os.path import isfile, join

yr = '2019'
month = {'January':'1','February':'2','March':'3','April':'4',\
    'May':'5','June':'6','July':'7','August':'8','September':'9',\
    'October':'10','November':'11','December':'12'}
date = []
met = []
proc_lines = []
write = []
first_aermet = True
last_aermet = False
first_aermod = True
sim_times = []

onlyfiles = [f for f in listdir('data/') if isfile(join('data/', f))]
dat_file = 'data/'+onlyfiles[0]
van_path = sys.argv[1]

#Read datafile and edit so AERMET can read it
with open(dat_file,'r') as bf:
    bf_list = bf.readlines()

    for line in bf_list:
        date = line.split()
        met = date[5].split(',')
        yr = date[3][2:]
        mth = month[date[2]]
        day = date[1]
        time = line[22:30]
        hr = '  '
        pres = str(float(met[4])*10.0)
        ws = met[2]
        wd = met[3]
        rh = met[5]
        tmp = met[6]
        dew = met[7]

        if int(mth)<10:
            mth = '0'+mth
    
        line_check = yr + ' ' + \
                     mth + ' ' + \
                     day + ' ' + \
                     time + ' ' + \
                     hr + ' ' + \
                     pres + ' ' + \
                     ws + ' ' + \
                     wd + '  ' + \
                     rh + '  ' + \
                     tmp + ' ' + \
                     dew + ' ' + \
                     ' 10\n'

        proc_lines.append(line_check)

sta_end = (bf_list[0][:30],bf_list[-1][:30])
xdate_sta = sta_end[0][19:21]+'/'+month[sta_end[0][7:16]]+'/'+str(int(sta_end[0][4:6]))
xdate_end = sta_end[1][19:21]+'/'+month[sta_end[1][7:16]]+'/'+str(int(sta_end[1][4:6]))
all_days = []
# all_months = []
#if going between different months, there might be a bug

for line in proc_lines:
    all_days.append(line[6:8])
    # all_months.append(line[3:5])

all_days = list(dict.fromkeys(all_days))
# all_months = list(dict.fromkeys(all_months))

#Make sure extract date is correct in stage 1 and stage 2 onsite AERMET input files
path_inp1 = '../AERMOD_paths/'+van_path+'/AERMET/stage1_onsite.inp'
path_inp2 = '../AERMOD_paths/'+van_path+'/AERMET/stage2_onsite.inp'
with open(path_inp1,'r') as chk:
    lines = chk.readlines()
    if lines[5].split()[1] != xdate_sta or lines[5].split()[1] != xdate_end:
        correct_date = lines[5][:11]+xdate_sta+' TO '+xdate_end+'\n'
        lines[5] = correct_date
        with open(path_inp1,'w') as corr1:
            corr1.writelines(lines)
        with open(path_inp2,'r') as corr2:
            lines = corr2.readlines()
        with open(path_inp2,'w') as corr2:
            lines[26] = correct_date
            corr2.writelines(lines)

sta_hr = (int(sta_end[0][21:24])%24)+1
end_hr = (int(sta_end[1][21:24])%24)+1
unk_sta = proc_lines[0]
unk_sta = unk_sta[:21]+'-999.9 -99.99 999  999  -999.9 -999.9  99\n'
unk_end = proc_lines[-1]
unk_end = unk_end[:21]+'-999.9 -99.99 999  999  -999.9 -999.9  99\n'
sta_list = []

cur_hour = int(sta_hr)
prev_hour = cur_hour

#Get starting list of unkown hours
for i in range(1,int(sta_hr)):
    ap = ''
    if i<10:
        ap = '0'
    sta_list.append(unk_sta[:18]+ap+str(i)+unk_sta[20:])

#Begin creating met data files for 1 second time resolution

length = len(proc_lines)

#Data to write to MET file that's read by AERMET
write = sta_list

for i in range(sta_hr, 25):
    ap = ''
    if i<10:
        ap = '0'
    ne = proc_lines[i-int(sta_hr)][:18]+ap+str(i)+proc_lines[i-int(sta_hr)][20:]
    write.append(ne)

#Setup timing system to determine the correct times to use in the simulation vs Actual time
sim_day = 0
cur_day = int(sta_end[0][4:6])
cur_month = month[sta_end[0][7:16]]
cur_year = sta_end[0][19:21]
prev_day = cur_day
skip = False

for k in range(0,length):

    if k>0:
            first_aermet = False
    if k == length-1:
            last_aermet = True

    #Can keep appending data if there is enough ahead of the buffer
    if k+(24-cur_hour)+1 < length:

        cur_hour = int(write[(sim_day*24)+cur_hour-1][9:11])+1

        #keep correct positioning if a new hour passes
        if prev_hour != cur_hour:
            if prev_hour == 24 and cur_hour == 1:
                write = write+change_days.new_day(k+1,length,proc_lines,unk_end)
                sim_day = sim_day + 1
                skip = False
            else:
                #If new hour passes but not a new day, don't need to run AERMET again because hour is in correct spot
                skip = True

            #Make sure the datafile doesn't skip hours, exit if it does
            if cur_hour != (prev_hour%24)+1:
                sys.exit('Exiting script, Met data is not continuous at '+'/'.join([cur_year,cur_month,str(cur_day)])+' '+cur_time)

            prev_hour = cur_hour
        else:
            skip = False

        #track time of the day and hour
        cur_time = write[(sim_day*24)+cur_hour-1][9:17]
        cur_day = int(write[(sim_day*24)+cur_hour-1][6:8])

        #Keep track of current days, add new day to met file if there is a new one
        if cur_day != prev_day:
            cur_year = write[(sim_day*24)+cur_hour-1][0:2]
            cur_month = write[(sim_day*24)+cur_hour-1][3:5]
            prev_day = cur_day
            change_days.fix_sfc_pfl(cur_year,cur_month,cur_day,van_path)

        #Keep track of real times being simulated
        sim_times.append(write[(sim_day*24)+cur_hour-1][:17])

        #Check if there is enough data to through AERMET to run AERMOD, and run it if there is
        if run_aermet.run(write, cur_time, cur_hour, van_path, first_aermet, last_aermet, sim_day,skip):
            if k-23 != 0:
                first_aermod = False
            run_aermod.run(sim_times, first_aermod, van_path)
            sim_times = []

        #Iterate through datafile
        write.pop(0)
        write.append(proc_lines[k+(24-cur_hour)+1][:18]+'24'+proc_lines[k+(24-cur_hour)+1][20:])

        #make sure indexing is correct in the met file
        for hr in range(0,24*(1+sim_day)):
            ap = ''
            if (hr%24)+1 < 10:
                ap = '0'
            write[hr] = write[hr][:6]+all_days[int(hr/24)]+write[hr][8:18]+ap+str((hr%24)+1)+write[hr][20:]

    #Start appending missing values if there isn't enough data ahead of the buffer
    else:

        cur_hour = int(write[(sim_day*24)+cur_hour-1][9:11])+1

        if prev_hour != cur_hour:
            if prev_hour == 24 and cur_hour == 1:
                write = write+change_days.new_day(k+1,length,proc_lines,unk_end)
                sim_day = sim_day + 1
                skip = False
            else:
                skip = True

            if cur_hour != (prev_hour%24)+1:
                sys.exit('Exiting script, Met data is not continuous at '+'/'.join([cur_year,cur_month,str(cur_day)])+' '+cur_time)

            prev_hour = cur_hour
        else:
            skip = False

        cur_time = write[(sim_day*24)+cur_hour-1][9:17]
        cur_day = int(write[(sim_day*24)+cur_hour-1][6:8])

        if cur_day != prev_day:
            cur_year = write[(sim_day*24)+cur_hour-1][0:2]
            cur_month = write[(sim_day*24)+cur_hour-1][3:5]
            prev_day = cur_day
            change_days.fix_sfc_pfl(cur_year,cur_month,cur_day,van_path)
            
        sim_times.append(write[(sim_day*24)+cur_hour-1][:17])

        # #Check if there is enough data to run AERMOD, and run it if there is
        if run_aermet.run(write, cur_time, cur_hour, van_path, first_aermet, last_aermet, sim_day, skip):
            if k-23 != 0:
                first_aermod = False
            run_aermod.run(sim_times, first_aermod, van_path)
            sim_times = []
        
        write.pop(0)
        write.append(unk_end[:18]+'24'+unk_end[20:])

        #make sure indexing is correct in the met file
        for hr in range(0,24*(1+sim_day)):
            ap = ''
            if (hr%24)+1 < 10:
                ap = '0'
            write[hr] = write[hr][:6]+all_days[int(hr/24)]+write[hr][8:18]+ap+str((hr%24)+1)+write[hr][20:]