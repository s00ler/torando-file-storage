# tornado web pdf file storage

## Installation
```
git clone https://github.com/s00ler/tornado-file-storage.git
cd path/to/cloned/rep/
pip3 install -r requirements.txt
```
### Important: requires poppler package.
For OS X users:
```
brew install poppler
```
More info on poppler install can be found at https://github.com/Belval/pdf2image.

## Usage
```
cd path/to/cloned/rep/
```
Change something in config.ini if you are aware of what you are doing.
```
python3 main.py
```
Open your browser and go to (use port value specified in config.ini, 8181 by default):
```
localhost:port
```
Also, server is started on my droplet at http://178.62.247.47:8181, so you can use it, unless it is stopped for some reason.
