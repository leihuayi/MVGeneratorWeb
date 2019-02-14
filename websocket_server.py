import asyncio
import websockets
import tempfile
import uuid
import argparse

from YoutubeMVGenerator.src.generate_mv import main as gen


def log_progress(ws):
    while True:
        progress = yield
        print(progress)
        yield from ws.send(progress)

@asyncio.coroutine
def slot(websocket, path):
    connectionId = str(uuid.uuid4())

    # Opening socket : send number generated videos
    print('open socket')
    count = 0
    with open("count_generated_videos.txt","r") as f:
        count = f.read()
    yield from websocket.send(count)

    # If receive audio
    audioBinFile = yield from websocket.recv()
    print('received audio file')

    autoTempDir = tempfile.mkdtemp('temp_audio')
    videoTempDir = tempfile.mkdtemp('temp_video')

    audioFilePath = '{}/{}.mp3'.format(autoTempDir, connectionId)
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
    args.data = '/path/to/data/folder/'
    gen(args, log_progress(websocket))

    # Send the video file
    print('sending video file')
    yield from websocket.send("Downloading video...\n This might take a while depending on your location")

    with open(videoFilePath, "rb") as file:
        video = file.read()
        print("video is %d bytes" % len(video))
        yield from websocket.send(video)
    print('sent video file')

    # Update generated videos
    with open("count_generated_videos.txt","w") as f:
        f.write(str(int(count)+1))

    # print('Closing websocket')
    # yield from websocket.close()



if __name__ == "__main__":
    start_server = websockets.serve(slot, 'localhost', 8765, max_size=2**27)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
