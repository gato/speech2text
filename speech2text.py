# importing libraries 
import os 
from util.duration import duration_str
from process.process import process
import click
import time

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

    start_time = time.perf_counter()

    if output == None:
        output = os.path.splitext(input)[0] + '.txt'

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
    
    process(input, output, silence_length, silence_thresh, temp_dir, padding, language, ambient_noise, keep_temporary, silent, max_workers)

    print('Done in {}!'.format(duration_str(start_time, time.perf_counter()))) if not silent else None
  
if __name__ == '__main__': 
    speech2text()