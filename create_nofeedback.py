import random

def random_file(name, total_seconds):
    f = open(name,'wb')
    f.write('state,time\n')

    #amount of time the file covers
    time = 0
    run_first = random.choice([True, False])

    while time < total_seconds:        
        if run_first:
            t = random.randint(2,30)
            f.write('run,'+str(t)+'\n')
            time += t

            t = random.randint(2,30)
            f.write('stop,'+str(t)+'\n')
            time += t
        else:
            t = random.randint(2,30)
            f.write('stop,'+str(t)+'\n')
            time += t

            t = random.randint(2,30)
            f.write('run,'+str(t)+'\n')
            time += t

    f.close()