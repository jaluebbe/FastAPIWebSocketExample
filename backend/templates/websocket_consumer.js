var ws = new WebSocket("ws://{{my_host}}:{{my_port}}/ws/imu");
ws.onmessage = function(event) {
    let message = JSON.parse(event.data);
    if(typeof processMessage === "function") {
        processMessage(message);
    }
}
