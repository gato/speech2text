import speech_recognition as sr 
import os 
from pydub import AudioSegment 
from pydub.silence import split_on_silence 
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed, thread

from util.progress import print_progress

def process_chunck(chunk, current_chunk, base_filename, temp_dir, ambient_noise, keep_temporary, language):

    # the name of the newly created chunk 
    filename = os.path.join(temp_dir, '{}.{:08d}.wav'.format(base_filename, current_chunk))

    # export audio chunk and save it
    chunk.export(filename, bitrate ='192k', format ="wav") 

    r = sr.Recognizer() 

    with sr.AudioFile(filename) as source: 
        if ambient_noise:
            r.adjust_for_ambient_noise(source)
        audio_listened = r.listen(source) 

    try: 
        # try converting it to text 
        return r.recognize_google(audio_listened, language=language) 

    # catch any errors. 
    except sr.UnknownValueError: 
        # nothing was recognized in this chunk
        return None

    except sr.RequestError as e: 
        raise RuntimeError('Requests are failing. Please check your internet connection')

    finally:
        if not keep_temporary:
            os.remove(filename)

def process(input, output, silence_length, silence_thresh, temp_dir, padding, language, ambient_noise, keep_temporary, silent, max_workers): 
    # open the audio file stored in file system
    speech = AudioSegment.from_file(input) 
  
    print('Splitting (this could take a while...)') if not silent else None
    # split track where silence is <silence-length> ms. or bigger
    chunks = split_on_silence(speech, 
        # must be silent for at least <silence-length> ms. 
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
    try:
        with ThreadPoolExecutor(max_workers = max_workers) as executor:
            # process each chunk 
            for i, chunk in enumerate(chunks): 
                futures.append(
                    executor.submit(
                        process_chunck, 
                        silence + chunk + silence, 
                        i, 
                        os.path.basename(os.path.splitext(input)[0]), 
                        temp_dir, 
                        ambient_noise, 
                        keep_temporary, 
                        language
                    )
                )
            print_progress(0, total, prefix='Converting:') if not silent else None
            for i, future in enumerate(as_completed(futures)):
                if future.exception():
                    # if exception was not handled abort as conversion won't be able to complete
                    executor._threads.clear()
                    thread._threads_queues.clear()                
                    raise future.exception()

                print_progress(i+1, total, prefix='Converting:') if not silent else None
    except Exception as e:
        sys.stderr.write('\nError: Canceling execution: {}\n'.format(e))
        sys.exit(1)

    print('\nSaving...') if not silent else None
    with open(output, 'w+') as f:
        for text in map(lambda f: f.result(), futures):
            if text != None:
                f.write('{}.\n'.format(text)) 
