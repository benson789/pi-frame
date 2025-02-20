import argparse
import os
import multiprocessing
import time
import threading
import RPi.GPIO as GPIO
import subprocess
from utils.actions.prompt_to_image import prompt_to_image
from utils.actions.load_workflow import load_workflow
from api.api_helpers import clear
import glob
import psutil
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys
from inky.auto import auto
import gpiod
import gpiodevice
from gpiod.line import Bias, Direction, Edge
import shutil

def create_parser():
    parser = argparse.ArgumentParser(description="Pi-Frame Daemon")
    parser.add_argument("-ws", "--whisper-server", default="192.168.0.10", metavar="[whisper-host]", help="Whisper host running on port 43001")
    parser.add_argument("-cw", "--comfy-workflow", default="workflow", metavar="[workflow-name]", help="Pre-installed ComfyUI Workflow to use for image gen")
    parser.add_argument("-d", "--dir", default=".", metavar="[path]", help="Working directory for images and transcripts")
    parser.add_argument("-t", "--time", default="5", metavar="[minutes]", help="Duration of Listen Loop (minutes)")
    return parser

def listen_thread():
    stamp = time.strftime("%Y%m%d_%H%M%S")
    filename = "/home/ben/pi-frame/output/transcripts/transcribe-"+stamp+".txt"

    record = [ "/usr/bin/arecord", "-f", "S16_LE", "-c1", "-r", "16000", "-t", "raw", "-D", "default" ]
    nc = [ "/usr/bin/nc", "192.168.0.10", "43001" ]

    rp = subprocess.Popen(record, stdout=subprocess.PIPE)
    np = subprocess.Popen(nc, stdin=rp.stdout, stdout=subprocess.PIPE, text=True)
    for line in iter(np.stdout.readline, ''):
        with open(filename, "a") as outputfile:
            outputfile.write(line)

def countdown(seconds):
    while seconds > 0:
        #print("timer: "+str(seconds))
        time.sleep(1)
        seconds -= 1

def gen_and_display():
    global PROMPT
    print("Gen image")
    list_of_prompts = glob.glob('/home/ben/pi-frame/output/transcripts/*.txt')
    if len(list_of_prompts) < 1:
        shutil.copyfile('/home/ben/pi-frame/output/default.txt', '/home/ben/pi-frame/output/transcripts/default.txt')
        promptfile = '/home/ben/pi-frame/output/transcripts/default.txt'
    else:
        promptfile = max(list_of_prompts, key=os.path.getctime)

    with open(promptfile, 'r') as file:
    	prompt = file.read()

    workflow = load_workflow('/home/ben/pi-frame/workflows/fluxschnell.json')
    print("prompt: "+prompt)
    if len(prompt) > 0:
        prompt_to_image(workflow, prompt, '', save_previews=True)

    imagefiles = glob.glob('/home/ben/pi-frame/output/images/*.png')
    if len(imagefiles) < 1:
        shutil.copyfile('/home/ben/pi-frame/output/default.png', '/home/ben/pi-frame/output/images/default.png')
        imagefile = '/home/ben/pi-frame/output/images/default.png'
    else:
        imagefile = max(imagefiles, key=os.path.getctime)

    prep_image(imagefile, promptfile)

    if PROMPT:
        image = Image.open(imagefile+"-prompt.png")
    else:
        image = Image.open(imagefile)

    inky = auto()
    inky.set_image(image, saturation="0.6")
    inky.show()
    print("Display image")

def prep_image(imagefile, promptfile):
    global PROMPT
    background = Image.open(imagefile)
    mute = False
    icons = {"refresh": Image.open("/home/ben/pi-frame/images/refresh35.png"), "text": Image.open("/home/ben/pi-frame/images/text35.png"), "save": Image.open("/home/ben/pi-frame/images/save35.png")}
    if mute:
        icons["mic"] = Image.open("/home/ben/pi-frame/images/mute35.png")
    else:
        icons["mic"] = Image.open("/home/ben/pi-frame/images/mic35.png")
    h = 45
    strip = Image.new("RGBA", (40, 480), (0,0,0,0))
    for icon in icons:
        if icon == "mic":
            if mute:
                icons[icon].paste("red", icons[icon])
            else:
                icons[icon].paste("green", icons[icon])
        elif icon == "text":
            if PROMPT:
                icons[icon].paste("green", icons[icon])
            else:
                icons[icon].paste("white", icons[icon])
        else:
            icons[icon].paste("white", icons[icon])
        imagecopy = icons[icon].copy()
        imagecopy.putalpha(220)
        icons[icon].paste(imagecopy, icons[icon])
        strip.paste(icons[icon], (0,h), icons[icon])
        h += 120

    background.paste(strip, (5, 0), strip)

    if PROMPT:
        with open(promptfile, 'r') as file:
            intext = file.read()
        textstring = intext.replace("\n", "")
        promptlist = textwrap.wrap(textstring, width=115)
        prompttxt = ""
        for prompt in promptlist:
            prompttxt += prompt + "\n"
        promptbg = Image.new("RGBA", (800, 480), (0,0,0,0))
        draw = ImageDraw.Draw(promptbg)
        draw.rounded_rectangle((80, 35, 750, 435), fill="white", radius=15)
        pbgcopy = promptbg.copy()
        pbgcopy.putalpha(60)
        promptbg.paste(pbgcopy, promptbg)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        draw.text((95, 50),prompttxt,(255,255,255),font=font)
        background.paste(promptbg, (0,0), promptbg)
        background.save(imagefile+"-prompt.png")
    else:
        background.save(imagefile)

def main():
    global PROMPT
    print("prompt: "+str(PROMPT))
    if 'parser' not in locals():
        parser = create_parser()
        args = parser.parse_args()
        mins = args.time

    timerSeconds = int(mins) * 60
    # gen and display latest image
    genThread = multiprocessing.Process(target=gen_and_display)
    genThread.start()

    print("Starting listen loop for "+mins+" minutes or input")
    listenThread = multiprocessing.Process(target=listen_thread)
    timerThread = multiprocessing.Process(target=countdown, args=[timerSeconds])
    listenThread.start()
    print("starting countdown")
    timerThread.start()
    while timerThread.is_alive():
        time.sleep(0.2)
        action = False
        for button in BUTTONS:
            state = GPIO.input(button)
            if not state:
                if button == 5:
                    action = "refresh"
                    print(str(button)+" State:"+str(state))
                    time.sleep(0.5)
                if button == 6:
                    action = "prompt"
                    print(str(button)+" State:"+str(state))
                    time.sleep(0.5)
                if button == 16:
                    action = "save"
                if button == 24:
                    action = "mic"
        if action == "refresh":
            break
        if action == "prompt":
            if PROMPT==True:
                print("prompt is enabled, disabling")
                PROMPT=False
            else:
                print("prompt not enabled, enabling")
                PROMPT=True

    print("timer expired, killing listen")
    listenThread.terminate()
    timerThread.terminate()

    PROCNAME = "nc"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

    print("Main thread finished, restarting.")
    main()

BUTTONS = [5,6,16,24]
GPIO.setmode(GPIO.BCM)

for button in BUTTONS:
    GPIO.setup(button, GPIO.IN)
    print(GPIO.input(button))

PROMPT = False

if __name__ == "__main__":
    main()
