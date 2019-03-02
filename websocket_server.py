import asyncio
import websockets
import tempfile
import uuid
import argparse
from multiprocessing import Pool, Pipe

from YoutubeMVGenerator.src.generate_mv import main as gen

count = 0
p = Pool(2)

def log_progress(ws):
    while True:
        progress = yield
        print(progress)
        yield from ws.send(progress)

@asyncio.coroutine
def slot(websocket, path):
    global count

    # Opening socket : send number generated videos
    print('open socket')
    yield from websocket.send(str(count))

    while True :
        connectionId = str(uuid.uuid4())

        # If receive audio
        audioBinFile = yield from websocket.recv()
        print('received audio file')

        autoTempDir = tempfile.mkdtemp('temp_audio')
        videoTempDir = tempfile.mkdtemp('temp_video')

        audioFilePath = '{}/{}.mp3'.format(autoTempDir, connectionId)
        videoFilePath = '{}/{}.mp4'.format(videoTempDir, connectionId)

        try:
            print('writting audio file ....')
            with open(audioFilePath, "wb") as file:
                audioBinFile = bytearray(audioBinFile)
                file.write(audioBinFile)
            print('audio file written !')

            args = argparse.Namespace()
            args.input = audioFilePath
            args.output = videoFilePath
            args.genre = ''
            args.data = '/home/sarah/YoutubeMVGenerator/statistics/songs_on_server.csv'

            parent_conn, child_conn = Pipe()
            result_token = p.apply_async(gen, (args, child_conn))

            while not result_token.ready():
                while parent_conn.poll():
                    yield from websocket.send(parent_conn.recv())
                yield from asyncio.sleep(0.5)
                yield from websocket.pong()

            while parent_conn.poll():
                yield from websocket.send(parent_conn.recv())

            if not result_token.successful():
                result_token.get()

            # Send the video file
            print('sending video file')
            yield from websocket.send("Downloading video...\n This might take a while depending on your location")

            with open(videoFilePath, "rb") as file:
                video = file.read()
                print("video is %d bytes" % len(video))
                yield from websocket.send(video)
            print('sent video file')

            # Update generated videos
            count += 1
            with open("count_generated_videos.txt","w") as f:
                f.write(str(count))

        except Exception as e:
            yield from websocket.send("Error : "+str(e))
            print(str(e))


if __name__ == "__main__":
    with open("count_generated_videos.txt","r") as f:
        count = int(f.read())
    start_server = websockets.serve(slot, 'localhost', 8765, max_size=2**27)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
