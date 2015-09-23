from psychopy import visual, core, event, gui, data
import math

#python tcp_send_1d.py -infile=test.1D -tcphost=127.0.0.1 -tcpport=8000 -delay=0.5


#--- TCPIP RECV - edited below to include IP address and TCP port in dialogue
# Store info about the experiment session
expName = u'net_text'  # from the Builder filename that created this script
expInfo = {'Participant':'', 'Session':'001','IP Address':'127.0.0.1  ', 'TCP Port':'8000'}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName, order=['Participant','Session','IP Address','TCP Port'])
if dlg.OK == False: core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
#--- TCPIP RECV 


log_file = open(expInfo['Participant'] + expInfo['date'] +'.csv','wb')

#--- start TCPIP RECV 
# initialize TCP socket to receive data
import socket
import select
TCP_IP = expInfo['IP Address'].strip() # use localhost
TCP_PORT = int(expInfo['TCP Port'])   # TCP port number
BUFFER_SIZE = 1024


# system calls to initialize the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print('Waiting for connection on %s:%s'%(TCP_IP,TCP_PORT))

conn, addr = s.accept()
s.setblocking(0)
conn.setblocking(0)

import csv
csvfile = open('mindrun.csv', 'rb')
content = csv.reader(csvfile, delimiter=',')
blocks  = []
content.next()
for row in content:
     blocks.append((row[0], int(row[1])))

win = visual.Window([800,600])
mov = visual.MovieStim(win, 'mindrun.mp4', size=[320,240],
                       flipVert=False, flipHoriz=False, loop=True)



text = visual.TextStim(win=win, ori=0, name='text',
    text=u"'User'\r\n",    font=u'Arial',
    pos=[0, -0.8], height=0.2, wrapWidth=None,
    color=u'orange', colorSpace=u'rgb', opacity=1,
    alignHoriz='center',depth=-1.0)

text.setAutoDraw(True)



clock = core.Clock()
global_clock = core.Clock()
block_index = 0
score = 0.0
score_size = 0.2
running = True

score_text = visual.TextStim(win=win, ori=0, name='text',
    text=u"0",    font=u'Arial',
    pos=[0, 0.7], height=score_size, wrapWidth=None,
    color=u'orange', colorSpace=u'rgb', opacity=1,
    alignHoriz='center',depth=-1.0)

score_text.setAutoDraw(True)

while True:
    data=[]
    block = blocks[block_index]

    try:
        data = conn.recv(BUFFER_SIZE)
        data = float(data.split('\n')[0])
        log_file.write(str(data)+'\n')
    except socket.error as ex:
        data = float(0.0)
    

    if block[0] == 'user':
        text.text = 'User'
        if data < float(0):
            print 'pause', data, clock.getTime()
            mov.pause()
            #global_clock.pause()
            running = False

        elif data > float(0):
            print 'play', data, clock.getTime()
            mov.play()
            running = True

    else:
        text.text = 'Free run'


    #calc score
    if running:
        bonus = global_clock.getTime() / 100.0
        score +=0.1 + bonus

    if clock.getTime() >= block[1]:
        block_index+=1
        clock.reset()

        if block_index < len(blocks) and blocks[block_index][0] == 'free':
            mov.play()
            running = True
        print 'change user'

    if block_index == len(blocks):
        break

    score_text.text = str(int(score))
    mov.draw()
    win.flip()

    if event.getKeys(keyList=['escape','q']):
        log_file.close()
        conn.close()
        s.close()
        win.close()
        core.quit()


log_file.close()
conn.close()
s.close()
core.quit()