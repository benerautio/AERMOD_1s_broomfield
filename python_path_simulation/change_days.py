#Various methods to fix met file indexing when changing days

#Must change the day of previous entries in these files, or else AERMOD will count them as missing 
#due to time discontinuities. This function accomplishes this
def fix_sfc_pfl(year, month, day, path):
    year = str(int(year))
    month = str(int(month))
    with open('../AERMOD_paths/'+path+'/AERMET/SFC/sfc_for_aermod.SFC','r') as sfc:
        sfc_lines = sfc.readlines()
        with open('../AERMOD_paths/'+path+'/AERMET/PFL/pfl_for_aermod.PFL','r') as pfl:
            pfl_lines = pfl.readlines()
            for i in range(1, len(sfc_lines)):
                sfc_lines[i] = ' '.join([year,month])+' '+str(day)+sfc_lines[i][8:]
            for i in range(0, len(pfl_lines)):
                pfl_lines[i] = ' '.join([year,month])+' '+str(day)+pfl_lines[i][9:]

    with open('../AERMOD_paths/'+path+'/AERMET/SFC/sfc_for_aermod.SFC','w') as sfc:
        sfc.writelines(sfc_lines)
        #print(sfc_lines)
    with open('../AERMOD_paths/'+path+'/AERMET/PFL/pfl_for_aermod.PFL','w') as pfl:
        pfl.writelines(pfl_lines)

#creating met lines to append to existing met for when a new day is iterated through the onsite met file
def new_day(k,length,proc_lines, unk_end):
    ret = []
    if k+24>length:
        for i in range(k,length):
            ap = ''
            if (i-k+1)<10:
                ap = '0'
            ret.append(proc_lines[i][:18]+ap+str(i-k+1)+proc_lines[i][20:])
        for j in range(len(ret),25):
            ap = ''
            if (i-k+1)<10:
                ap = '0'
            ret.append(unk_end[:18]+ap+str(j-len(ret)+1)+unk_end[20:])
    else:
        for i in range(k,k+24):
            ap = ''
            if (i-k+1)<10:
                ap = '0'
            ret.append(proc_lines[i][:18]+ap+str(i-k+1)+proc_lines[i][20:])
    return ret


    