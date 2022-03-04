# FastAPIWebSocketExample
This repository includes examples how to stream sensor data via FastAPI/WebSockets.
A fake data generator can be used to create artificial IMU data.
To stream real sensor data, this visualisation could be added to the flight data
recorder implementation at http://github.com/jaluebbe/GPSTracker .
Alternatively, the fake data generator could be used as template for another
implementation.

Visualisation examples with JS generated fake data can be found at https://jaluebbe.github.io/FastAPIWebSocketExample/ .

## Building bird.js (optional)
The content of src/index.js is packed to dist/bird.js which will include all requirements from the three.js library.
To build bird.js, you need npm (nodejs) installed. Then call
```
npx webpack
```
and install webpack on request.


## Using docker compose to start all processes
```
docker compose up
```
If you don't want to use docker, you may use the Dockerfiles as guide how to
start the fake data generator and the backend. Additionally, a running instance
of Redis is required.
You could use miniforge to create your environment by calling:
```
conda env create -f environment.yml
```
If you want to start the web interface on your local computer only, just call
```
uvicorn main:app --port 8080
```
from the backend folder.
