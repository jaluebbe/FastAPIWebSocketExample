# FastAPIWebSocketExample
This repository includes examples how to stream sensor data via FastAPI/WebSockets.
A fake data generator can be used to create artificial IMU data.
To stream real sensor data, this visualisation could be added to the flight data
recorder implementation at http://github.com/jaluebbe/GPSTracker .
Alternatively, the fake data generator could be used as template for another
implementation.

Visualisation examples with JS generated fake data can be found at https://jaluebbe.github.io/FastAPIWebSocketExample/ .

## Building bird.js
The content of src/index.js is packed to dist/bird.js which will include all requirements from the three.js library.
To build bird.js, you need npm (nodejs) installed. Then call
```
npx webpack
```
and install webpack on request.

## Running the web interface
```
uvicorn backend:app --host 0.0.0.0 --port 8080
```
