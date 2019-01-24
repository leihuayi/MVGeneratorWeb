var saveByteArray = (function () {
    var a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (data, name) {
        var blob = new Blob(data, {type: "octet/stream"}),
            url = window.URL.createObjectURL(blob);
        a.href = url;
        a.download = name;
        a.click();
        window.URL.revokeObjectURL(url);
    };
}());


ws = new WebSocket("ws://127.0.0.1:8765");

ws.binaryType = "blob"

ws.onmessage = function (evt) {
    if (typeof evt.data == "string") {
        console.log(evt.data);
        ws.send("dummy audio file")
    }
  else {
    console.log("received video blob")
    saveByteArray([evt.data], 'video.mp4');
    //window.navigator.msSaveOrOpenBlob("data:application/octet-stream;" + evt.data, '3phase.bkp');
  }
};
