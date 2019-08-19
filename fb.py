import facebook
import os
import subprocess
from PIL import Image
import time
import numpy as np
from skimage import img_as_float

def mse(imageA, imageB):
    err = np.sum(((img_as_float(imageA) - img_as_float(imageB)) ** 2))
    width, height = imageA.size
    err /= float(width*height)
    return err

def extractFrames():
    print("FPS of the video during extraction?")
    fps = int(input())
    print("Place the video file in the corresponding folder.\nPress enter when you are ready to continue.")
    input()

    # Find the video file
    for file in os.listdir(folderName):
        if file.endswith(".mkv"):
            filePath = os.path.join(folderName, file)
    filePathReal = "\"{}\""
    filePathReal = filePathReal.format(filePath)

    # Build and execute ffmpeg command
    cmd = "ffmpeg -i {} -vf fps={} {}/%6d.png"
    cmd = cmd.format(filePathReal, fps, folderName)
    subprocess.call(cmd, shell=True)
    print("Finished extraction")


def bestOf():
    # "Best-of" Tool

    # Get strength from the user
    print("What level would you like to run the progam at?")
    print("Enter a number between 0.0 and 100.0, 0.0 being no frames deleted")
    strength = float(input())
    files = os.listdir(folderName)
    for file in list(files):
        if file.endswith(".mkv") | file.endswith(".txt"):
            files.remove(file)
    os.chdir(folderName)
    img2 = Image.open(files[0])
    for x in range(1,len(files)):
        img1 = img2
        img2 = Image.open(files[x])
        diff = mse(img1, img2)
        diffString = "Frame #{} and #{}. Diff Value: {}"
        diffString = diffString.format(x, x+1, diff)
        if diff < (strength*1.2)/1000.0:
            os.remove(files[x-1])
        #print(diffString)
    os.chdir("../../")


def burstUpload():
    # Determine the intent of the burst upload from the user.
    timeBetweenBursts = 0.0
    print("How many pictures would you like to upload in one burst?")
    picsPerBurst = int(input())
    print("How many bursts would you like to upload?")
    burstAmount = int(input())
    if burstAmount > 1:
        print("How much time between each burst, in hours?(e.g. 0.5, 1, 2)")
        timeBetweenBursts = float(input())

    # Read the current frames to upload
    textfile = "lastframeuploaded.txt"
    files = os.listdir(folderName)
    for file in list(files):
        if file.endswith(".mkv") | file.endswith(".txt"):
            files.remove(file)
    os.chdir(folderName)
    frameAmount = len(files)
    if not (os.path.exists(textfile)):
        currentFrame = frameAmount+1
        confirmText = "You are about to start upload from frame {}. Press enter to confirm."
        confirmText = confirmText.format(frameAmount)
        print(confirmText)
        input()
    else:
        lastFrameFile = open(textfile, "r")
        currentFrame = int(lastFrameFile.read())
        lastFrameFile.close()
        confirmText = "You are about to start upload from frame {}. Press enter to confirm."
        confirmText = confirmText.format(currentFrame-1)
        print(confirmText)
        input()

    lastPicFlag = False
    for y in range(burstAmount):
        for x in range(currentFrame-2, currentFrame-2-picsPerBurst, -1):
            # Update text file
            lastFrameFile = open("lastframeuploaded.txt", "w")
            lastFrameFile.write(str(x+1))
            lastFrameFile.close()

            fbMessage = "Book {} | Ep. {} - {} - Frame {} out of {}"
            fbMessage = fbMessage.format(season, episode, episodeTitle, x+1, frameAmount)
            print(fbMessage)
            print("Uploading frame.. don't close program.")
            graph.put_photo(image=open(files[x], 'rb'), message=fbMessage)
            print("Uploaded!")
            currentFrame -= 1
            if x == 0:
                lastPicFlag = True
                break
        if lastPicFlag == True:
            print("Last frame of the episode uploaded.")
            break
        if y == burstAmount-1:
            break
        waitingString = "Waiting {} hour(s)."
        waitingString = waitingString.format(timeBetweenBursts)
        print(waitingString)
        time.sleep(int(timeBetweenBursts*3600))

    os.chdir("../../")


def uploadFrames():
    # Get some data from the user.
    print("How many frames would you like to upload?")
    amountOfFrames = int(input())
    print("How much time between each upload, in hours?(e.g. 0.5 1 2)")
    timeBetweenUpload = float(input())

    # Read the current frame to upload
    textfile = "lastframeuploaded.txt"
    files = os.listdir(folderName)
    for file in list(files):
        if file.endswith(".mkv") | file.endswith(".txt"):
            files.remove(file)
    os.chdir(folderName)
    frameAmount = len(files)
    if not (os.path.exists(textfile)):
        currentFrame = frameAmount + 1
        confirmText = "You are about to start upload from frame {}. Press enter to confirm."
        confirmText = confirmText.format(frameAmount)
        print(confirmText)
        input()
    else:
        lastFrameFile = open(textfile, "r")
        currentFrame = int(lastFrameFile.read())
        lastFrameFile.close()
        confirmText = "You are about to start upload from frame {}. Press enter to confirm."
        confirmText = confirmText.format(currentFrame - 1)
        print(confirmText)
        input()

    for x in range(currentFrame - 2, currentFrame - 2 - amountOfFrames, -1):
        # Update text file
        lastFrameFile = open("lastframeuploaded.txt", "w")
        lastFrameFile.write(str(x + 1))
        lastFrameFile.close()

        fbMessage = "Book {} | Ep. {} - {} - Frame {} out of {}"
        fbMessage = fbMessage.format(season, episode, episodeTitle, x + 1, frameAmount)
        print(fbMessage)
        print("Uploading frame.. don't close program.")
        graph.put_photo(image=open(files[x], 'rb'), message=fbMessage)
        print("Uploaded!")
        currentFrame -= 1
        if x == 0:
            print("Last frame of the episode uploaded.")
            break
        waitingString = "Waiting {} hour(s)."
        waitingString = waitingString.format(timeBetweenUpload)
        print(waitingString)
        time.sleep(int(timeBetweenUpload*3600))

    os.chdir("../../")


#Create File Structure
if not(os.path.exists("Files")):
    os.mkdir("Files")

#Main Menu
folderName = ""
menuInput = -1
#Set up Facebook credentials
graph = facebook.GraphAPI(
        access_token="EAASR6zwVCOIBAEoZCzkE7qKs9FgxMGbTTsyOASdai2aoZAJevYqOSi3VKuy8ZAhNcOKI3y0cVDit188uKYCFmZBgS8Yt8dqTXHTsqYm3xrbMqwSRsm0CH7ZCauZBQZBtoKt5X5hcANQhWTZCPRqofPcZCUZCZAhF0KILC1wzMRo0ZA7dZCZCd1puDreUqE",
        version="3.1")
while int(menuInput) != 0:
    print("What would you like to do?")
    print("1. Extract Frames")
    print("2. Upload Frames")
    print("3. Run Best-Of")
    print("4. Burst Upload")
    print("0 to quit")
    print("Enter number: ")
    menuInput = input()
    if int(menuInput) == 0:
        break
    print("\nEnter season number:")
    season = input()
    print("Enter episode number:")
    episode = input()
    folderName = "Files/S{}E{}"
    folderName = folderName.format(season, episode)

    # Check if the folder already exists
    if not (os.path.exists(folderName)):
        os.mkdir(folderName)

    episodeTitleFile = "{}/episodetitle.txt"
    episodeTitleFile = episodeTitleFile.format(folderName)
    if not os.path.exists(episodeTitleFile):
        print("This episode hasn't been titled yet. What is the title?")
        episodeTitle = input()
        episodeTitleFile2 = open(episodeTitleFile, "w")
        episodeTitle = episodeTitleFile2.write(episodeTitle)
        episodeTitleFile2.close()
    else:
        episodeTitleFile2 = open(episodeTitleFile, "r")
        episodeTitle = episodeTitleFile2.read()
        episodeTitleFile2.close()
    if int(menuInput) == 1:
        extractFrames()
    if int(menuInput) == 2:
        uploadFrames()
    if int(menuInput) == 3:
        bestOf()
    if int(menuInput) == 4:
        burstUpload()