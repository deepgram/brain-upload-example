# brain-upload-example
A simple system for uploading files

### Installation
    git clone https://github.com/deepgram/brain-upload-example.git
    cd brain-upload-example
    pip install -e .

### Usage example
To upload a file in a directory:
    cd some/directory/somewhere
    brainupload -u my.userid -t my.token -s https://mycustom-brain.deepgram.com -f somefile.wav


To upload all files in a directory, go to that directory and run:

    brainupload -u my.userid -t my.token -s https://mycustom-brain.deepgram.com
Get the token and userid from the 'api' link in on your brain instance! Files will appear in the 'My Files' page of brain instance you uploaded to.

