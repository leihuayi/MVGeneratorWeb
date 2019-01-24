import asyncio
import websockets
import uuid
import tempfile
import argparse

#from YoutubeMVGenerator.code.generate_mv import main as gen

currentSlot = ''

@asyncio.coroutine
def slot(websocket, path):
    print('open socket')
    global currentSlot
    if currentSlot != '':
        yield from websocket.close()
        return

    currentSlot = str(uuid.uuid4())
    print('sending UUID')
    yield from websocket.send(currentSlot)
    print('receiving audio')
    audioBinFile = yield from websocket.recv()
    print('got audio')

    autoTempDir = tempfile.mkdtemp('temp_audio')
    videoTempDir = tempfile.mkdtemp('temp_video')

    audioFilePath = '{}/{}.mp3'.format(autoTempDir, currentSlot)
    videoFilePath = '/home/hbarraud/Downloads/foucault.mp4'
    #videoFilePath = '{}/{}.mp4'.format(videoTempDir, currentSlot)
    print('writting audio file')
    with open(audioFilePath, "wb") as file:
        audioBinFile = bytearray(audioBinFile.encode())
        file.write(audioBinFile)
    print('written audio file')

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
    yield from websocket.close()

start_server = websockets.serve(slot, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
