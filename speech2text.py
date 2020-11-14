# importing libraries 
import speech_recognition as sr 
import os 
from pydub import AudioSegment 
from pydub.silence import split_on_silence 
import click
# a function that splits the audio file into chunks 
# and applies speech recognition 
@click.command()
@click.option('--silence-length', '-l', default=700, help='consider silence anything longer than <silence-length> ms. default 700 ms.')
@click.option('--silence-thresh', '-t', default=-40, help='consider silent if quiter than <silence-length> dBFS. default -40')
@click.option('--temp-dir', '-T', type=click.Path(), default='./tmp', help='path to store temporary files')
@click.option('--padding', '-p', default=100, help="how much silence to add at both ends so it doesn't seem abruptly sliced. default 100ms")
@click.option('--language', '-L', default='en-US', help='language to use for speech recognition')
@click.option('--ambient-noise', '-n', is_flag=True, help="try to adapt listening to ambient noise")
@click.argument('input')
@click.argument('output')
def speech2text(input, output, silence_length, silence_thresh, temp_dir, padding, language, ambient_noise): 
  
    # open the audio file stored in 
    # the local system as a wav file. 
    print('Converting {} using {}'.format(input, language))
    #filename, file_extension = os.path.splitext(input)
    song = AudioSegment.from_file(input) 
  
    # open a file where we will concatenate   
    # and store the recognized text 
    fh = open(output, "w+") 

    print("cortando archivo {} {}".format(silence_length, silence_thresh))          
    # split track where silence is 0.5 seconds  
    # or more and get chunks 
    chunks = split_on_silence(song, 
        # must be silent for at least 0.5 seconds 
        # or 500 ms. adjust this value based on user 
        # requirement. if the speaker stays silent for  
        # longer, increase this value. else, decrease it. 
        min_silence_len = silence_length, 
  
        # consider it silent if quieter than -16 dBFS 
        # adjust this per requirement 
        silence_thresh = silence_thresh #25 #-16
    ) 
    print(" se crearon {} partes".format(len(chunks)))
    # create a directory to store the audio chunks. 
    try: 
        os.mkdir(temp_dir) 
    except(FileExistsError): 
        pass
  
    # move into the directory to 
    # store the audio files. 
    os.chdir(temp_dir) 
  
    # Create 10ms silence chunk 
    chunk_silent = AudioSegment.silent(duration = padding) 

    i = 0
    total = len(chunks)
    # process each chunk 
    for chunk in chunks: 
              
        print("processing {} de {}".format(i+1, total))
  
        # add 0.5 sec silence to beginning and  
        # end of audio chunk. This is done so that 
        # it doesn't seem abruptly sliced. 
        audio_chunk = chunk_silent + chunk + chunk_silent 
  
        # export audio chunk and save it in  
        # the current directory. 
        # print("saving chunk{0}.wav".format(i)) 
        # specify the bitrate to be 192 k 
        audio_chunk.export("./chunk{0}.wav".format(i), bitrate ='192k', format ="wav") 
  
        # the name of the newly created chunk 
        filename = 'chunk'+str(i)+'.wav'
  
        # print("Processing chunk "+str(i)) 
  
        # get the name of the newly created chunk 
        # in the AUDIO_FILE variable for later use. 
        file = filename 
  
        # create a speech recognition object 
        r = sr.Recognizer() 
  
        # recognize the chunk 
        with sr.AudioFile(file) as source: 
            # remove this if it is not working 
            # correctly. 
            if ambient_noise:
                r.adjust_for_ambient_noise(source)
            audio_listened = r.listen(source) 
  
        try: 
            # try converting it to text 
            rec = r.recognize_google(audio_listened, language=language) 
            # write the output to the file. 
            fh.write("{}.\n".format(rec)) 
  
        # catch any errors. 
        except sr.UnknownValueError: 
            print("Could not understand audio") 
  
        except sr.RequestError as e: 
            print("Could not request results. check your internet connection") 
  
        i += 1
  
    os.chdir('..') 
  
  
if __name__ == '__main__': 
    speech2text()