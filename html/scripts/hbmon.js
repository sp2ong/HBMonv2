         var sock = null;
         var ellog = null;
         
         window.onload = function() {
            var wsuri;
            
            ellog = document.getElementById('log');
            
            bridge_table = document.getElementById('bridge');
            main_table = document.getElementById('main');
            masters_table = document.getElementById('masters');
            opb_table = document.getElementById('opb');
            peers_table = document.getElementById('peers');
            
            wsuri = (((window.location.protocol === "https:") ? "wss://" : "ws://") + window.location.hostname + ":9000");
            
            if ("WebSocket" in window) {
               sock = new WebSocket(wsuri);
            } else if ("MozWebSocket" in window) {
               sock = new MozWebSocket(wsuri);
            } else {
               if (ellog != null) {
               log("Browser does not support WebSocket!");}
            }
            
            if (sock) {
               sock.onopen = function() {
                  if (ellog != null) {
                  log("Connected to " + wsuri);}
               }
               sock.onclose = function(e) {
                  if (ellog != null) {
                  log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");}
                  sock = null;
                  bridge_table.innerHTML = "";
                  main_table.innerHTML = "";
                  masters_table.innerHTML = "";
                  opb_table.innerHTML = "";
                  peers_table.innerHTML = "";
               }
               sock.onmessage = function(e) {
                   var opcode = e.data.slice(0,1);
                   var message = e.data.slice(1);
                   if (opcode == "b") {
                       Bmsg(message);
                   } else if (opcode == "c") {
                       Cmsg(message);                   
                   } else if (opcode == "i") {
                       Imsg(message);         
                   } else if (opcode == "o") {
                       Omsg(message);         
                   } else if (opcode == "p") {
                       Pmsg(message);         
                   } else if (opcode == "l") {
                      if (ellog != null) { 
                       log(message);}
                   } else if (opcode == "q") {
                       log(message);
                       bridge_table.innerHTML = "";
                       main_table.innerHTML = "";
                       masters_table.innerHTML = "";
                       opb_table.innerHTML = "";
                       peers_table.innerHTML = "";
                   } else {
                       log("Unknown Message Received: " + message);
                   }
               }
            }
         };

         function Bmsg(_msg) {bridge_table.innerHTML = _msg;};  
         function Cmsg(_msg) {masters_table.innerHTML = _msg;};
         function Imsg(_msg) {main_table.innerHTML = _msg;};
         function Omsg(_msg) {opb_table.innerHTML = _msg;};
         function Pmsg(_msg) {peers_table.innerHTML = _msg;};

         function log(_msg) {
            ellog.innerHTML += _msg + '\n';
            ellog.scrollTop = ellog.scrollHeight;};         
