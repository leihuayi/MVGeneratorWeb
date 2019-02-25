var ws;

var app = new Vue({
    el: '#app',
    data: {
      count: 0,
      modal: '',
      error: '',
      hascanceled: false
    },
    methods : {
      sendFile : function() {
          var file = document.getElementById('upload_audio').files[0];
          var reader = new FileReader();
          var rawData = new ArrayBuffer();

          reader.loadend = function() {

          }

          reader.onload = function(e) {
              rawData = e.target.result;
              ws.send(rawData)
              console.log("File "+file.name+" has successfully been transferred.")

              var modal = document.getElementById('modal-generate-info');
              var instance = M.Modal.getInstance(modal);
              
              app.hascanceled = false;
              instance.open();
              app.modal = '(0/4) Sending audio file...';
          }

          reader.readAsArrayBuffer(file);
          
      },
      cancelGeneration : function() {
        this.hascanceled = true
        console.log("Video generation cancelled by user.")
      }
    }
  })

M.AutoInit();
connectServer()

  function connectServer() {
    ws = new WebSocket("ws://TODO_ADRESS/backend/");

    ws.binaryType = "blob";

    var modal = document.getElementById('modal-generate-info');
    var instance = M.Modal.getInstance(modal);

    ws.onmessage = function (evt) {
        if (typeof evt.data == "string") {
          if (evt.data == parseInt(evt.data, 10)) {
            app.count = evt.data
          }
          else {
            if (evt.data.substring(0,5) == "Error") {
              instance.close();
              app.error = evt.data
            }
            else {
              app.modal = evt.data
            }
          } 
        }
        else {
          console.log("received video blob")
          if (!app.hascanceled){
            instance.close();
            saveByteArray([evt.data], 'music_video.mp4');
            app.count = (parseInt(app.count)+1).toString()
          }
        }
    };

    ws.onerror = function(e) {
        instance.close();
        app.error = 'The generation function is currently down, thank you for your understanding.'
    }

}

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

                