import random

def random_file(name, total_seconds):
    f = open(name,'wb')
    f.write('state,time\n')

    #amount of time the file covers
    time = 0

    while time < total_seconds:        

        t = random.randint(2,8)
        f.write('run,'+str(t)+'\n')
        time += t

        t = random.randint(2,8)
        f.write('stop,'+str(t)+'\n')
        time += t

    f.close()