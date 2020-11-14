# importing libraries 
import speech_recognition as sr 
import os 
from pydub import AudioSegment 
from pydub.silence import split_on_silence 
#from .progress import printProgressBar
import progress
import click
# a function that splits the audio file into chunks 
# and applies speech recognition 
@click.command()
@click.option('--silence-length', '-l', default=700, help='consider silence anything longer than <silence-length> ms. default 700 ms.')
@click.option('--silence-thresh', '-t', default=-40, help='consider silent if quiter than <silence-length> dBFS. default -40')
@click.option('--temp-dir', '-T', type=click.Path(), default='./tmp', help='path to store temporary files')
@click.option('--padding', '-p', default=100, help="how much silence to add at both ends so it doesn't seem abruptly sliced. default 100ms")
@click.option('--language', '-L', default='en-US', help='language to use for speech recognition. default en-US')
@click.option('--ambient-noise', '-n', is_flag=True, help="try to adapt listening to ambient noise")
@click.argument('input')
@click.argument('output')
def speech2text(input, output, silence_length, silence_thresh, temp_dir, padding, language, ambient_noise): 
  
    # open the audio file stored in file system
    summary='''
Speech to Text process
Input File        : {}
Output File       : {}
Language          : {}
Silence Length    : {} ms.
Silence Threshold : {} dBFS
Padding           : {} ms.
Adapt to Noise    : {} 
    '''
    print(summary.format(
        input, 
        output,
        language,
        silence_length,
        silence_thresh,
        padding,
        ambient_noise
        )
    )
    
    base_filename, file_extension = os.path.splitext(input)
    speech = AudioSegment.from_file(input) 
  
    # open a file where we will concatenate and store the recognized text 
    fh = open(output, 'w+') 
    print('Splitting (this could take a while...)')
    # progress.printProgressBar(0, 100, prefix='Splitting :')
    # split track where silence is <silence-lenght> ms. or bigger
    chunks = split_on_silence(speech, 
        # must be silent for at least <silence-lenght> ms. 
        min_silence_len = silence_length, 
        # consider it silent if quieter than <silence-thresh> dBFS 
        silence_thresh = silence_thresh,
        #keep_silence = padding
    ) 
    # create a directory to store the audio chunks. 
    try: 
        os.mkdir(temp_dir) 
    except(FileExistsError): 
        pass
  
    # Create <padding> ms silence chunk 
    chunk_silent = AudioSegment.silent(duration = padding) 

    curr_chunk = 1
    total_chunks = len(chunks) 

    print()
    # process each chunk 
    for chunk in chunks: 
              
        progress.printProgressBar(curr_chunk, total_chunks, prefix='Converting:')
  
        # add silence to beginning and  
        # end of audio chunk. This is done so that 
        # it doesn't seem abruptly sliced. 
        audio_chunk = chunk_silent + chunk + chunk_silent 

        # the name of the newly created chunk 
        filename = os.path.join(temp_dir, '{}.{:08d}.wav'.format(base_filename, curr_chunk))

        # export audio chunk and save it
        audio_chunk.export(filename, bitrate ='192k', format ="wav") 
  
        # create a speech recognition object 
        r = sr.Recognizer() 
  
        # recognize the chunk 
        with sr.AudioFile(filename) as source: 
            if ambient_noise:
                r.adjust_for_ambient_noise(source)
            audio_listened = r.listen(source) 
  
        try: 
            # try converting it to text 
            rec = r.recognize_google(audio_listened, language=language) 
            # write the output to the file. 
            fh.write('{}.\n'.format(rec)) 
  
        # catch any errors. 
        except sr.UnknownValueError: 
            # nothing was recognized in this chunk
            pass
  
        except sr.RequestError as e: 
            print('Could not request results. check your internet connection') 
            exit(1)
  
        curr_chunk += 1
  
    # os.chdir('..')
    print('\nDone!')
  
  
if __name__ == '__main__': 
    speech2text()