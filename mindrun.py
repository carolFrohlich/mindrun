from psychopy import visual, core, event, gui, data
import math
import time

#python tcp_send_1d.py -infile=test.1D -tcphost=127.0.0.1 -tcpport=8000 -delay=0.5

#instructions for each type of experiment
#TODO: find a better way to store instructions
instructions = {
    'demo': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, \nsed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation\n ullamco laboris nisi ut aliquip ex ea commodo consequat.',
    'feedback': "The goal of this task is to make your character run using your own brain activity.\n\nOn the bottom center of the screen there will be instructions to let you know who is playing the game.\n\nWhen the instructions say 'You Run', focus your attention to make your character run. \n\nWhen the instructions say 'Free Run' you may rest quietly with your eyes open and watch the game.",
    'nofeedback': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, \nsed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation\n ullamco laboris nisi ut aliquip ex ea commodo consequat.'
}

#design file
design = { 'demo': 'demo.csv',
           'feedback': 'dev.csv',
           'nofeedback': 'dev.csv' }
fake_data = 'fake_data.csv'

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


while True:
    #--- TCPIP RECV - edited below to include IP address and TCP port in dialogue
    # Store info about the experiment session
    expName = u'Mindrun'
    expInfo = {'Participant':'', 'Session':'001','IP Address':'', 'TCP Port':'8000', 'Type (Demo, Feedback, No Feedback)': 'Demo            '}
    dlg = gui.DlgFromDict(dictionary=expInfo, title=expName, order=['Participant','Session','IP Address','TCP Port', 'Type (Demo, Feedback, No Feedback)'])
    if dlg.OK == False: core.quit()  # user pressed cancel
    expInfo['date'] = data.getDateStr()  # add a simple timestamp
    expInfo['expName'] = expName


    #resolve type of experiment
    experiment = expInfo['Type (Demo, Feedback, No Feedback)'].replace(' ', '').lower()

    if experiment in ['demo', 'feedback', 'nofeedback']:
        break
    else:
        error_dlg = gui.Dlg(title="Error")
        error_dlg.addText('Error. Experiment type '+  experiment + ' not valid.')
        error_dlg.show()
        if error_dlg.OK == False: core.quit()


instruction_txt = instructions[experiment] 

log_file = open(expInfo['Participant'] + expInfo['date'] +'.csv','wb')


############### show instructions while waiting for 10s ###############
#win = visual.Window([800,600])
win = visual.Window(fullscr=True)

instructionsClock = core.Clock()
text_instruct = visual.TextStim(win=win, name='text_instruct', text=instruction_txt, height=0.085, color='white', font='Arial')

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


while show_instructions:

    if event.getKeys(keyList=['escape','q']):
        quit()

    if LUMINA == 1:
        lumina_dev.poll_for_response()
        while lumina_dev.response_queue_size() > 0:
            response = lumina_dev.get_next_response()
            if response["pressed"]:
                #print "Lumina received: %s, %d"%(response["key"],response["key"])
                text_instruct.setAutoDraw(False)
                show_instructions = False
    else:
        time.sleep(3)
        text_instruct.setAutoDraw(False)
        show_instructions = False

print 'lumina ok'
 


##################### instructions finish, we are connected #####################

#start fixation screen
fixation_clock = core.Clock()
fix_stim = visual.TextStim(win=win, name='fixation', text="+", font='Arial', height=0.8, color='white')

fix_stim.setAutoDraw(True)
win.flip()


# read design file
import csv
csvfile = open(design[experiment] , 'rb')
content = csv.reader(csvfile, delimiter=',')
blocks  = []
content.next()
for row in content:
     blocks.append((row[0], int(row[1])))


#set up screen
mov = visual.MovieStim(win, 'mindrun.mp4', size=[300,450], flipVert=False, flipHoriz=False, loop=True)

text = visual.TextStim(win=win, name='text', text=u"'User'\r\n", font=u'Arial', pos=[0, -0.8], height=0.2, color=u'orange')


#set up clock and score
clock = core.Clock()
global_clock = core.Clock()
block_index = 0
score = 0.0
running = False

#use fake data or real data?
fake_run = False
if experiment == 'demo' or experiment == 'nofeedback':
    fake_run = True
    csvfile = open(fake_data , 'rb')
    content = csv.reader(csvfile, delimiter=',')
    fake_blocks  = []
    content.next()
    for row in content:
         fake_blocks.append((row[0], int(row[1])))


    fake_index = 0
    fake_block = None
    fake_clock = core.Clock()



score_text = visual.TextStim(win=win, name='text', text=u"0", font=u'Arial', pos=[0, 0.7], height=0.2, color=u'orange')

data=[]
block = None


while True:
    
    block = blocks[block_index]
    #get data from fake file or socket

    if fake_run:
        fake_block = fake_blocks[fake_index]
        if fake_clock.getTime() >= fake_block[1]:
            fake_index += 1
        if fake_index >= len(fake_blocks): #if fake file ends, read file again
            fake_index = 0

        #run or not?
        if fake_block[0] == 'run':
            data = 1
        else:
            data = -1


    else:
        try:
            #######################################
            #use this code when working with real data
            #######################################
            # data = conn.recv(BUFFER_SIZE)
            # tcp_data=str(data.split('\000')[0])
            # if tcp_data != '\000' and tcp_data != "" and "nan" not in tcp_data.lower():

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

            #log_file.write(str(data)+'\n') 

        except socket.error as ex:
            data = float(0.0)

    
    if block[0] == 'fixation':
    	fix_stim.setAutoDraw(True)

    elif block[0] == 'user':
        
        text.text = 'You Run'
        if data < float(0):
            mov.pause()
            #global_clock.pause()
            running = False

        elif data > float(0):
            mov.play()
            running = True

    elif block[0] == 'button':
        text.text = 'Press button'
        mov.pause()
        running = False

    else:
        text.text = 'Free Run'


    #calculate score score
    if running:
        bonus = global_clock.getTime() / 600.0
        score += 0.1 + bonus

    #change block (user or free)
    if clock.getTime() >= block[1]:

        #if last block was fixation
        if block[0] == 'fixation':
            score_text.setAutoDraw(True)
            text.setAutoDraw(True)
            fix_stim.setAutoDraw(False)

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
    if block[0] != 'fixation':
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
your_score = visual.TextStim(win=win, name='yourscore', text=u"Your score is", font=u'Arial', pos=[0, 0.5], height=0.2, color=u'orange')
your_score.setAutoDraw(True)

score_text = visual.TextStim(win=win, name='score', text=str(int(score)), font=u'Arial', height=0.8, color=u'orange')
score_text.setAutoDraw(True)

thanks = visual.TextStim(win=win, name='thanks', text=u"Thank you", font=u'Arial', pos=[0, -0.5], height=0.2, color=u'orange')
thanks.setAutoDraw(True)

win.flip()
thanks_clock = core.Clock()

#start thanks loop
while thanks_clock.getTime() <= 30.0:
    if event.getKeys(keyList=['escape','q']):
        quit()
    fix_stim.setAutoDraw(True)


#wrap up
quit()