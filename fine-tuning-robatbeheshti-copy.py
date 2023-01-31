import os
import shutil
import fnmatch
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import make_chunks
import re

def prepareDataSet(output_dir, output_allo_dir, output_wave_path, output_text_path, utt_str):
    utt_id = 1

    output_wave = open(output_wave_path, 'w', encoding='utf-8')
    output_text = open(output_text_path, 'w', encoding='utf-8')

    for root_dir, cur_dir, files in os.walk(r'.\\robate beheshti\\Validation'):
        for fname in files:
            if fnmatch.fnmatch(fname, "*_target_*"):
                shutil.copy2(os.path.join(root_dir,fname), os.path.join(output_dir,fname))
                symbols = ['r', 'o', 'b', 'a', 't', 'e', 'b', 'e', 'h', 'e', 'ʃ', 't', 'i']

                content_str = ' '.join(map(str, symbols))
                output_text.write(str(utt_id) + utt_str + content_str +'\n')
                output_wave.write(str(utt_id) + utt_str + os.path.join(output_allo_dir, fname) +'\n')
                utt_id += 1

    output_text.close()
    output_wave.close()

if __name__ == '__main__':
    # output_dir = '.\\allosaurus-master\\robatbeheshti-target\\train'
    # output_allo_dir = '.\\robatbeheshti-target\\train'
    # output_wave_path = '.\\allosaurus-master\\robatbeheshti-target\\train\\wave'
    # output_text_path = '.\\allosaurus-master\\robatbeheshti-target\\train\\text'

    # prepareDataSet(output_dir, output_allo_dir, output_wave_path, output_text_path, 'train ')

    output_dir = '.\\allosaurus-master\\robatbeheshti-target\\validate'
    output_allo_dir = '.\\robatbeheshti-target\\validate'
    output_wave_path = '.\\allosaurus-master\\robatbeheshti-target\\validate\\wave'
    output_text_path = '.\\allosaurus-master\\robatbeheshti-target\\validate\\text'

    prepareDataSet(output_dir, output_allo_dir, output_wave_path, output_text_path, 'validate ')