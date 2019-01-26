import asyncio
import websockets
import tempfile
import uuid
import argparse

from YoutubeMVGenerator.code.generate_mv import main as gen


@asyncio.coroutine
def slot(websocket, path):
    connectionId = str(uuid.uuid4())

    # Opening socket : send UUID
    print('open socket')

    # If receive audio
    print('waiting for audio file ....')

    audioBinFile = yield from websocket.recv()
    print('got audio')


    autoTempDir = tempfile.mkdtemp('temp_audio')
    videoTempDir = tempfile.mkdtemp('temp_video')

    audioFilePath = '{}/z.mp3'.format(autoTempDir, connectionId)
    videoFilePath = '{}/{}.mp4'.format(videoTempDir, connectionId)
    print('writting audio file ....')
    with open(audioFilePath, "wb") as file:
        audioBinFile = bytearray(audioBinFile)
        file.write(audioBinFile)
    print('audio file written !')

    args = argparse.Namespace()
    args.input = audioFilePath
    args.output = videoFilePath
    args.genre = ''
    gen(args, lambda str: websocket.send(str))

    print('sending video file')

    yield from websocket.send("Sending...")
    with open(videoFilePath, "rb") as file:
        video = file.read()
        print("video is %d bytes" % len(video))
        yield from websocket.send(video)
    print('sent video file')

    print('Closing websocket')
    yield from websocket.close()


start_server = websockets.serve(slot, 'localhost', 8765, max_size=2**27)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
