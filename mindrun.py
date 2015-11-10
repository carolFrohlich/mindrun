from psychopy import visual, core, event, gui, data
import math
import time

#python tcp_send_1d.py -infile=test.1D -tcphost=127.0.0.1 -tcpport=8000 -delay=0.5


def quit():
    log_file.close()
    conn.close()
    s.close()
    win.close()
    core.quit()


LUMINA = 0
LUMINA_TRIGGER = 4

## initialize communication with the lumina

if LUMINA == 1:
    import pyxid # to interact with the Lumina box
    import sys

    ## initialize communication with the lumina
    devices=pyxid.get_xid_devices()

    if devices:
        lumina_dev=devices[0]
    else:
        print "Could not find Lumina device"
        sys.exit(1)

    print lumina_dev
    if lumina_dev.is_response_device():
        lumina_dev.reset_base_timer()
        lumina_dev.reset_rt_timer()
    else:
        print "Error: Lumina device is not a response device??"
        sys.exit(1)


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


############### show instructions while waiting for 5 ###############
win = visual.Window([800,600])
instructionsClock = core.Clock()
text_instruct = visual.TextStim(win=win, ori=0, name='text_instruct',
    text="Mussum ipsum cacilds, vidis litro abertis.\n\n'Consetis adipiscings elitis.\n\n'Pra la , depois divoltis porris, paradis. \n\nPaisis, filhis, espiritis santis.",    font='Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

text_instruct.setAutoDraw(True)
show_instructions = True
win.flip()


if LUMINA == 1:
	lumina_dev.clear_response_queue()


#--- start TCPIP RECV 
# initialize TCP socket to receive data
import socket
import select
TCP_IP = expInfo['IP Address'].strip() # use localhost
TCP_PORT = int(expInfo['TCP Port'])   # TCP port number
BUFFER_SIZE = 1024



while show_instructions:
    if LUMINA == 1:
    	print 'waiting for lumina'
        lumina_dev.poll_for_response()
        while lumina_dev.response_queue_size() > 0:
            response = lumina_dev.get_next_response()
            if response["pressed"]:
                print "Lumina received: %s, %d"%(response["key"],response["key"])
                text_instruct.setAutoDraw(False)
                show_instructions = False
    else:
        time.sleep(10)
        text_instruct.setAutoDraw(False)
        show_instructions = False

    print 'lumina ok'
 

#system calls to initialize the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#TCP_IP = ''
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print('Waiting for connection on %s:%s'%(TCP_IP,TCP_PORT))

conn, addr = s.accept()
s.setblocking(0)
conn.setblocking(0)
print 'connection ok'        


##################### instructions finish, we are connected, 30s fixation #####################
fixation_clock = core.Clock()



fix_stim = visual.TextStim(win=win, ori=0, name='fixation',
    text="+",    font='Arial',
    pos=[0, 0], height=0.8, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

fix_stim.setAutoDraw(True)
win.flip()

while fixation_clock.getTime() <= 10.0:
    fix_stim.setAutoDraw(True)

fix_stim.setAutoDraw(False)
win.flip()

##################### start task #####################


# read csv file
import csv
csvfile = open('mindrun.csv', 'rb')
content = csv.reader(csvfile, delimiter=',')
blocks  = []
content.next()
for row in content:
     blocks.append((row[0], int(row[1])))


#set up screen
mov = visual.MovieStim(win, 'mindrun.mp4', size=[320,240],
                       flipVert=False, flipHoriz=False, loop=True)

text = visual.TextStim(win=win, ori=0, name='text',
    text=u"'User'\r\n",    font=u'Arial',
    pos=[0, -0.8], height=0.2, wrapWidth=None,
    color=u'orange', colorSpace=u'rgb', opacity=1,
    alignHoriz='center',depth=-1.0)

text.setAutoDraw(True)


#set up clock and score
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


#start receiving values from socket
while True:
    data=[]
    block = blocks[block_index]

    try:
        #######################################
        #use this code when working with real data

        # data = str(conn.recv(BUFFER_SIZE))

        # tcp_data=data.replace('\000', ''); # remove null byte
        # #print "%s (%s) (%s)" %('tcp_data', tcp_data, tcp_buffer)

        # if tcp_data != '\000' and tcp_data != "" and \
        #     "nan" not in tcp_data.lower():

        #     vals=tcp_data.split(",")
        #     if len(vals) > 1:
        #         data=float(vals[1])
        #     else:
        #         data=float(tcp_data)
        #######################################


        #######################################
        #use this when testing with tcp_send_1d
        data = conn.recv(BUFFER_SIZE)
        data = float(data.split('\n')[0])
        #######################################

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


    #calculate score score
    if running:
        bonus = global_clock.getTime() / 100.0
        score +=0.1 + bonus

    #change block (user or free)
    if clock.getTime() >= block[1]:
        block_index+=1
        clock.reset()

        if block_index < len(blocks) and blocks[block_index][0] == 'free':
            mov.play()
            running = True
        print 'change user'

    #finish movie if we ran all blocks    
    if block_index == len(blocks):
        break

    #update screen
    score_text.text = str(int(score))
    mov.draw()
    win.flip()

    if event.getKeys(keyList=['escape','q']):
        quit()


#finished movie, clean screen
mov.setAutoDraw(False)
text.setAutoDraw(False)
score_text.setAutoDraw(False)

##################### experiment finished, go to thanks screen #####################

#creating text stim
your_score = visual.TextStim(win=win, ori=0, name='your_score',
    text=u"Your score is",    font=u'Arial',
    pos=[0, 0.5], height=0.2, wrapWidth=None,
    color=u'orange', colorSpace=u'rgb', opacity=1,
    alignHoriz='center',depth=-1.0)
your_score.setAutoDraw(True)

score_text = visual.TextStim(win=win, ori=0, name='score',
    text=str(int(score)),    font=u'Arial',
    pos=[0, 0], height=0.8, wrapWidth=None,
    color=u'orange', colorSpace=u'rgb', opacity=1,
    alignHoriz='center',depth=-1.0)
score_text.setAutoDraw(True)

thanks = visual.TextStim(win=win, ori=0, name='thanks',
    text=u"Thank you",    font=u'Arial',
    pos=[0, -0.5], height=0.2, wrapWidth=None,
    color=u'orange', colorSpace=u'rgb', opacity=1,
    alignHoriz='center',depth=-1.0)
thanks.setAutoDraw(True)

win.flip()

thanks_clock = core.Clock()

#start thanks loop
while thanks_clock.getTime() <= 10.0:
    if event.getKeys(keyList=['escape','q']):
        quit()

    fix_stim.setAutoDraw(True)


#wrap up
quit()