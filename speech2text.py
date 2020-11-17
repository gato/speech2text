# importing libraries 
import speech_recognition as sr 
import os 
from pydub import AudioSegment 
from pydub.silence import split_on_silence 
import sys
from concurrent.futures import ThreadPoolExecutor

import progress
import click
import time

def process_chunck(chunk, current_chunk, base_filename, temp_dir, ambient_noise, keep_temporary, silence, language):

    audio_chunk = silence + chunk + silence 

    # the name of the newly created chunk 
    filename = os.path.join(temp_dir, '{}.{:08d}.wav'.format(base_filename, current_chunk))

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
        return rec

    # catch any errors. 
    except sr.UnknownValueError: 
        # nothing was recognized in this chunk
        return None

    except sr.RequestError as e: 
        sys.stderr.write('Requests are failing. Please check your internet connection\n')
        raise RuntimeError('Requests are failing. Please check your internet connection')

    finally:
        if not keep_temporary:
            os.remove(filename)

def count_done(futures):
    done = 0
    for future in futures:
        if future.done():
            done += 1
    return done

# a function that splits the audio file into chunks 
# and applies speech recognition 
@click.command()
@click.option('--silence-length', '-l', default=700, help='consider silence anything longer than <silence-length> ms. default 700 ms.')
@click.option('--silence-thresh', '-t', default=-40, help='consider silent if quiter than <silence-length> dBFS. default -40')
@click.option('--temp-dir', '-T', type=click.Path(), default='./tmp', help='path to store temporary files')
@click.option('--padding', '-p', default=100, help="how much silence to add at both ends so it doesn't seem abruptly sliced. default 100ms")
@click.option('--language', '-L', default='en-US', help='language to use for speech recognition. default en-US')
@click.option('--ambient-noise', '-n', is_flag=True, help="try to adapt listening to ambient noise")
@click.option('--keep-temporary', '-k', is_flag=True, help="do not remove temporary audio files (debugging)")
@click.option('--silent', '-s', is_flag=True, help="do not print anything on screen")
@click.option('--max-workers', '-m', default=os.cpu_count(), help='number of concurrent conversions. default {}'.format(os.cpu_count()))
@click.argument('input')
@click.argument('output', required=False)
def speech2text(input, output, silence_length, silence_thresh, temp_dir, padding, language, ambient_noise, keep_temporary, silent, max_workers): 

    base_filename, file_extension = os.path.splitext(input)
    if output == None:
        output = base_filename + '.txt'

    summary='''
Speech to Text process
Input File           : {}
Output File          : {}
Language             : {}
Silence Length       : {} ms.
Silence Threshold    : {} dBFS
Padding              : {} ms.
Adapt to Noise       : {} 
Keep temporary files : {}
Max Workers          : {}
    '''
    print(summary.format(
        input, 
        output,
        language,
        silence_length,
        silence_thresh,
        padding,
        ambient_noise,
        keep_temporary,
        max_workers
        )
    ) if not silent else None
    
    # open the audio file stored in file system
    speech = AudioSegment.from_file(input) 
  
    print('Splitting (this could take a while...)') if not silent else None
    # split track where silence is <silence-lenght> ms. or bigger
    chunks = split_on_silence(speech, 
        # must be silent for at least <silence-lenght> ms. 
        min_silence_len = silence_length, 
        # consider it silent if quieter than <silence-thresh> dBFS 
        silence_thresh = silence_thresh,
    ) 
    total = len(chunks) 

    # create temporary dir if it doesn't exist
    try: 
        os.mkdir(temp_dir) 
    except(FileExistsError): 
        pass
  
    # Create <padding> ms silence chunk 
    silence = AudioSegment.silent(duration = padding) 
    futures = []
    with ThreadPoolExecutor(max_workers = max_workers) as executor:
        # process each chunk 
        for i, chunk in enumerate(chunks): 
            futures.append(
                executor.submit(
                    process_chunck, 
                    chunk, 
                    i, 
                    base_filename, 
                    temp_dir, 
                    ambient_noise, 
                    keep_temporary, 
                    silence, 
                    language
                )
            )
        while True:
            done = count_done(futures) 
            progress.printProgressBar(done, total, prefix='Converting:') if not silent else None
            if done == total:
                break
            time.sleep(.5)

    print('\nSaving...') if not silent else None
    with open(output, 'w+') as f:
        for text in map(lambda f: f.result(), futures):
            if text != None:
                f.write('{}.\n'.format(text)) 
    print('Done!') if not silent else None
  
if __name__ == '__main__': 
    speech2text()