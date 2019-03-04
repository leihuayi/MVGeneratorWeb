import asyncio
import websockets
import tempfile
import uuid
import argparse
import os
import json
from multiprocessing import Process, Pipe

from YoutubeMVGenerator.src.generate_mv import main as gen

count = 0

def makeTmpFiles():
    connectionId = str(uuid.uuid4())

    autoTempDir = tempfile.mkdtemp('temp_audio')
    videoTempDir = tempfile.mkdtemp('temp_video')

    return ('%s/%s.mp3'%(autoTempDir, connectionId), '%s/%s.mp4'%(videoTempDir, connectionId))


@asyncio.coroutine
def slot(websocket, path):
    global count

    # Opening socket : send number generated videos
    print('open socket')
    yield from websocket.send(str(count))

    args = argparse.Namespace()
    args.data = '/home/sarah/YoutubeMVGenerator/statistics/songs_on_server.csv'
    args.input = ''
    args.output = ''

    while True :
        try:
            # Receive from websocket
            wsString = yield from websocket.recv()
            if len(wsString) > 10:
                print('received audio file ...')
                audioFilePath, videoFilePath = makeTmpFiles()
                with open(audioFilePath, "wb") as file:
                    audioBinFile = bytearray(wsString)
                    file.write(audioBinFile)
                print('audio file written !')
                args.input = audioFilePath
                args.output = videoFilePath
                args.genre = ''

            else :
                args.genre = wsString
                print('received genre')
                if args.input == '' or args.output == '':
                    yield from websocket.send('Error : order in sending info')
                    continue


            parent_conn, child_conn = Pipe()
            proc = Process(target=gen, args=(args, child_conn))
            proc.start()

            while proc.is_alive():
                while parent_conn.poll():
                    yield from websocket.send(parent_conn.recv())
                yield from asyncio.sleep(0.5)
                yield from websocket.pong()

            while parent_conn.poll():
                yield from websocket.send(parent_conn.recv())
            proc.join()

            # Send the video file
            if os.path.exists(videoFilePath):
                genreMissing = False
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
