# Image Processor Service
**Service for generation video of all possible combinations of blocks of video, audio, text and voice**
Examples:
- https://drive.google.com/file/d/10pm0mGV-b_AMTf_RIO00R-ewBD5S4LwA/view?usp=share_link
- https://drive.google.com/file/d/1EEIkt_OF4xgeb8H-gm1cgku6NaMOQWk9/view?usp=share_link
- https://drive.google.com/file/d/13jKdedG5dKzTW01Y2w6Z7LbOJA2db94k/view?usp=share_link
---

# Stack

* **Python 3.12+**
* **Docker & Docker Compose**
* **FastAPI**
* **RabbitMQ**
* **FFmpeg**
* **ElevenLabs API**
* **Google Drive API**

---

## Architecture

Core logic is based on Consumer-Producer Pattern: 

1. **API Layer (FastAPI)**: Receives and validates requests, then publishes messages to RabbitMQ.
2. **Message Broker (RabbitMQ)**: Maintains the queue of video processing tasks.
3. **Worker Service (MediaService)**: Consumes tasks, downloads assets, and manages the FFmpeg lifecycle.
4. **Storage Layer**: Uses temporary local storage (/tmp) for intermediate fragments and Google Drive for final file delivery.

---

## Setup and Execution

### Prerequisites
* Linux (Pop!_OS / Ubuntu) or macOS.
* Make
* Docker
* Python 3.11+ or uv.
---

### 0. Get client_secret.json
To get the `client_secret.json` file, follow these steps:
1. Go to Google Cloud Console.
2. Create a new project or select an existing one.
3. Create an OAuth consent screen if you haven't already.
4. Navigate to APIs & Services > Credentials.
5. Create credentials by selecting OAuth client ID, configuring consent
6. Download the `client_secret.json` file and put in root directory of your project.

### 1. Initialization
Run the setup command to create the virtual environment and install dependencies.
```bash
make setup
```

### 2. Start project
```bash
make up
```
**After about 30 sec app will be ready to use on: http://localhost:8000"
### 3. Rebuild project (if needed)
```bash
make rebuild
```
**Check logs for any errors or issues.**



### Possible Issues and Weaknesses in system

---


- **Errors**: While API validate user's API token and auth flow, there is no guarantee that all messages to process successfully (save to Google Drive) due to bad audio/video urls, third-party API failure etc.
- **Problems**:
  1. Processing some videos can take a long time. This could be fixed with more CPU or GPU power and changing ffmpeg settings in code. Possible solutions includes caching some files, we can store dictionary of url to file path on disk, if we hit the same URL again, we can just return the existing file instead of processing it again, but we can't hold files too long in memory because it could cause memory overflow.
  2. Another problem is that failed message which failed due to network or third-party API failure will not be retried, and possible solution is to add a retry mechanism for failed messages

### New tools:

---

- **FFmpeg**: New tool for me for processing audios, videos, concatenating them
- **Google Drive API, Eleven Labs API**: third party APIs used in project.

### Conclusion:

---


That was interesting test assignment, where I've learned a new image processing library and tool(ffmpeg) and practice once again Consumer-Producer architecture, FastAPI and docker usage.
