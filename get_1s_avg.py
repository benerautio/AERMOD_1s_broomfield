#Reads aermod.out and writes path average to a csv file
import os

def run(sim_times,van_path,first):
    hour = []
    conc = []
    with open('../AERMOD_paths/'+van_path+'/AERMOD/aermod.out','r') as big:
        ls = big.readlines()

        for i in range(0, len(ls)):
            if ls[i].split() == ['**', 'CONC', 'OF', 'CH4', 'IN', 'MICROGRAMS/M**3', '**']:
                hour.append(int(ls[i-6].split()[9]))
                conc.append(ls[i+6].split()[2:])

    sum_c = 0.0
    keep_track = []
    total_rec = 0

    for t in range(0,len(hour)):
        cur_t = hour[t]
        total_rec = len(conc[t])
        for c in conc[t]:
            val = float(c)
            sum_c = sum_c+val
        
        keep_track.append((cur_t,sum_c,total_rec))
        sum_c = 0.0

    res = []
    conc_sum = 0.0
    rec_sum = 0

    for i in range(0,int(len(keep_track)/12)):
        for r in keep_track:
            if r[0] == i+1:
                conc_sum = conc_sum+float(r[1])
                rec_sum = rec_sum+int(r[2])
        res.append((i+1,conc_sum,rec_sum))
        conc_sum = 0.0
        rec_sum = 0

    avgs = []

    for hr in res:
        avg = hr[1]/hr[2]
        avgs.append((str(hr[0]),str(avg)))

    if first == True:
        mode = 'w'
        header = 'D,T,C\n'
    else: 
        mode = 'a'
        header = ''
        
    with open('../results/1s_'+van_path+'_results.csv',mode) as f:
        lines = []
        lines.append(header)

        for i in range(0,len(sim_times)):
            date = sim_times[i][:8].replace(' ','/')
            time = sim_times[i][9:]
            data = (date,time,avgs[i][1])
            st = ','.join(data) + '\n'
            lines.append(st)

        f.writelines(lines)

