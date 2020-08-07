#Runs AERMOD using a shell script and Calculates 1s path average from aermod.out
import get_1s_avg
import subprocess
import os

def run(sim_times, first, van_path):

    try:
        os.chdir('../AERMOD_paths/'+van_path+'/AERMOD/')
    except FileNotFoundError:
        print(van_path+' path does not exist')
    print("\nRunning AERMOD for "+sim_times[0]+' to '+sim_times[-1]+'\n')
    subprocess.call(['sh','run_1s_aermod.sh'])

    print("\nAERMOD Done\n")

    print('\nCalculating path averages...\n')
    os.chdir('../../../python_path_simulation')
    get_1s_avg.run(sim_times,van_path,first)
    print('\nDone calculating path averages for '+sim_times[0]+' to '+sim_times[-1]+', results are in the results folder.\n')


    






