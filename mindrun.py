from psychopy import visual, core, event, gui, data
import math
import time

#python tcp_send_1d.py -infile=test.1D -tcphost=127.0.0.1 -tcpport=8000 -delay=0.5


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
    #TODO: I have no idea where socket code should 
    #system calls to initialize the socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

TCP_IP = ''
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print('Waiting for connection on %s:%s'%(TCP_IP,TCP_PORT))

conn, addr = s.accept()
s.setblocking(0)
conn.setblocking(0)
print 'connection ok'        


##################### instructions finish, we are connected, 30s fixation #####################
fixation_clock = core.Clock()

#create window
win = visual.Window(size=(1024, 768),
                    #fullscr=FULL_SCREEN,
                    screen=0,
                    allowGUI=False,
                    allowStencil=False,
                    monitor='testMonitor',
                    color='black',
                    colorSpace='rgb')


fix_stim = visual.Circle(win=win,
    radius=[0.01875,0.025],
    edges=32,
    ori=0,
    name='fix_stim',
    pos=[0, 0],
    lineColor='white',
    fillColor='white',
    lineColorSpace='rgb',
    opacity=1,
    depth=0.0)


fix_stim.setAutoDraw(True)

while fixation_clock.getTime() <= 3.0:
    fix_stim.setAutoDraw(True)

fix_stim.setAutoDraw(False)



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
win = visual.Window([800,600])
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
        data = str(conn.recv(BUFFER_SIZE))
        #TODO: ver o q a ressonancia vai mandar

        tcp_data=data.replace('\000', ''); # remove null byte
        #print "%s (%s) (%s)" %('tcp_data', tcp_data, tcp_buffer)

        if tcp_data != '\000' and tcp_data != "" and \
            "nan" not in tcp_data.lower():

            vals=tcp_data.split(",")
            if len(vals) > 1:
                data=float(vals[1])
            else:
                data=float(tcp_data)

        log_file.write(str(data)+'\n')
        print "Received %s, %f\n"%(tcp_data,data)  

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