import asyncio
import websockets
import uuid
import tempfile
import argparse
import sys

#from YoutubeMVGenerator.code.generate_mv import main as gen

currentSlot = ''

@asyncio.coroutine
def slot(websocket, path):
    
    # Opening socket : send UUID
    print('open socket')
    global currentSlot
    if currentSlot != '':
        print('Closing websocket')
        yield from websocket.close()
        return

    currentSlot = str(uuid.uuid4())
    print('sending UUID')
    yield from websocket.send(currentSlot)

    # If receive audio
    print('waiting for audio file ....')
    try :
        audioBinFile = yield from websocket.recv()
        print('got audio')

    except websockets.exceptions.ConnectionClosed as e:
        print(e)
        print('Payload length exceeds size limit ( > 1048576 bytes). Closing websocket')
        currentSlot = ''
        return

    autoTempDir = tempfile.mkdtemp('temp_audio')
    videoTempDir = tempfile.mkdtemp('temp_video')

    audioFilePath = '{}/{}.mp3'.format(autoTempDir, currentSlot)
    videoFilePath = '{}/{}.mp4'.format(videoTempDir, currentSlot)
    print('writting audio file ....')
    with open(audioFilePath, "wb") as file:
        audioBinFile = bytearray(audioBinFile)
        file.write(audioBinFile)
    print('audio file written !')

    args = argparse.Namespace()
    args.input = audioFilePath
    args.output = videoFilePath
    args.genre = ''
    #gen(args)

    print('sending video file')

    yield from websocket.send("Sending...")
    with open(videoFilePath, "rb") as file:
        video = file.read()
        print("video is %d bytes" % len(video))
        yield from websocket.send(video)
    print('sent video file')

    currentSlot = ''
    print('Closing websocket')
    yield from websocket.close()
    return

start_server = websockets.serve(slot, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
