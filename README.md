# MVGeneratorWeb

This project is a website to generate a Music Video for an input music.

Click on the caption below for a demo video.
[![Demo](http://img.youtube.com/vi/XFnFXVnM4Us/0.jpg)](https://youtu.be/XFnFXVnM4Us)

## Requirements :
* websockets
* from [YoutubeMVGenerator](https://github.com/leihuayi/YoutubeMVGenerator) :
    * Python 3.5.6
    * Librosa
    * Pyscenedetect
    * Opencv
    * Msaf
    * ACRCloud Python SDK

## Structure

The website is hosted on a serverA, while the generation algorithm takes place on a serverB.
Therefore a websocket is used in order to transmit data between serverA and serverB :
1. A user gives a MP3 file clicks on a button "Generate a video !" on the website.
2. The mp3 file is sent over the websocket to serverB.
3. serverB runs an algorithm to generate a video
4. When serverB is done, it sends back the video .mp4 file to the websocket client
5. The user received the video through the website.


* `front/` folder contains the website code : html, css, js websocket client, hosted on serverA
* `websocket_server.py` is the websocket server, hosted on serverB
* `YoutubeMVGenerator/` folder containts the MV generation algorithm, hosted on serverB
