import os
import shutil
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import make_chunks
import re

chunk_len = 8 #in seconds
farsdat_to_allosaurus = {'sil':'', 'a':'ɒ', 'aa':'a', 'g':'ɡ', 'q':'ɢ', 'gs':'ʔ', 'j':'d͡ʒ', 'ch':'t͡ʃʲ', 'zh':'ʒ', 'sh':'ʃ', 'kh':'x', 'y':'j'}

def mapFarsdatToAllosaurus(symbols):
    for i in range(len(symbols)):
        res = farsdat_to_allosaurus.get(symbols[i])
        if res is not None:
            symbols[i] = res

def getFileSymbols(filename, make_chunks):
    txt_file = open(filename, "r")
    content = txt_file.read()
    content = content.rstrip().split()

    if(make_chunks):
        symbols = [val for key,val in enumerate(content,1) if key%3==0] #keep every third element, which is a symbol
        start_time = [int(val) for key,val in enumerate(content,1) if key%3==1] #keep every first element, which is the starting time of a symbol

        chuncked_symbols = []
        last_i = 1
        next_div = chunk_len
        for i in range(len(start_time)):
            div = start_time[i]//10000000
            if div >= next_div:
                next_div += chunk_len
                chuncked_symbols.append([val for _,val in enumerate(symbols[last_i-1:i-1],1) if val!='sil'])
                last_i = i
            elif i == len(start_time) - 1:
                chuncked_symbols.append([val for _,val in enumerate(symbols[last_i-1:],1) if val!='sil'])
        
        for i in range(len(chuncked_symbols)):
            mapFarsdatToAllosaurus(chuncked_symbols[i])
        txt_file.close()
        return chuncked_symbols
    else:
        symbols = [val for key,val in enumerate(content,1) if key%3==0 and val!='sil'] #keep every third element, which is a symbol, except 'sil'
        mapFarsdatToAllosaurus(symbols)
        txt_file.close()
        return symbols

def prepareDataSet(file_classifier, output_dir, output_allo_dir, utt_str, percent, make_c=False):
    utt_id = 1

    class_file = open(file_classifier, "r")
    filenames = class_file.read()
    filenames = filenames.rstrip().split()
    filenames = [val for key,val in enumerate(filenames,0) if key%2==0 and key!=0]

    output_wave_path = os.path.join(output_dir,'wave')
    output_text_path = os.path.join(output_dir,'text')
    output_wave = open(output_wave_path, 'w+', encoding='utf-8')
    output_text = open(output_text_path, 'w+', encoding='utf-8')

    wav_dir = '.\\FARSDAT-split\\Wav_FarsDat1'
    pho_dir = '.\\FARSDAT-split\\Phoneme'

    file_count = len(filenames)*percent//100

    if(make_c == False):
        for i in range(file_count):
            #copying audio files
            shutil.copy2(os.path.join(wav_dir,filenames[i]+'.wav'), os.path.join(output_dir,filenames[i]+'.wav'))

            #getting symbols
            file_content = getFileSymbols(os.path.join(pho_dir,filenames[i]+'.lab'), make_c)

            #making text and wave file of the chunk
            content_str = ' '.join(map(str, file_content))
            output_text.write(str(utt_id) + utt_str + content_str +'\n')
            output_wave.write(str(utt_id) + utt_str + os.path.join(output_allo_dir, filenames[i]+'.wav') +'\n')
            utt_id += 1
    else:
        for i in range(file_count):
            #Mapping FARSDAT symbols to allosaurus symbols in chunks
            file_content = getFileSymbols(os.path.join(pho_dir,filenames[i]+'.lab'), make_c) 

            #making wav chunk files
            myaudio = AudioSegment.from_file(os.path.join(wav_dir,filenames[i]+'.wav') , "wav") 
            chunk_length_ms = chunk_len*1000 # pydub calculates in millisec
            chunks = make_chunks(myaudio, chunk_length_ms) #Make chunks of chunk_len seconds

            for j, chunk in enumerate(chunks):
                if j >= len(file_content):
                    continue 

                #Export all of the individual chunks as wav files
                # chunk_name = "{0}-chunk{1}.wav".format(wav_list[i].name.split(".wav", flags=re.IGNORECASE)[0],j)
                chunk_name = "{0}-chunk{1}.wav".format(re.split(".wav", filenames[i], flags=re.IGNORECASE)[0],j)
                chunk.export(os.path.join(output_dir, chunk_name), format="wav")

                #making text and wave file of the chunk
                content_str = ' '.join(map(str, file_content[j]))
                output_text.write(str(utt_id) + utt_str + content_str +'\n')
                output_wave.write(str(utt_id) + utt_str + os.path.join(output_allo_dir, chunk_name) +'\n')
                utt_id += 1

    output_text.close()
    output_wave.close()

if __name__ == '__main__':
    file_classifier = '.\\FARSDAT-split\\HResult-HDecode\\train.txt'
    output_dir = '.\\allosaurus-master\\FARSDAT-parent-c10\\train'
    output_allo_dir = '.\\FARSDAT-parent-c10\\train'
    prepareDataSet(file_classifier, output_dir, output_allo_dir, 'train ', 10, True)

    file_classifier = '.\\FARSDAT-split\\HResult-HDecode\\dev.txt'
    output_dir = '.\\allosaurus-master\\FARSDAT-parent-c100\\validate'
    output_allo_dir = '.\\FARSDAT-parent-c100\\validate'
    prepareDataSet(file_classifier, output_dir, output_allo_dir, 'val ', 100)

    # file_classifier = '.\\FARSDAT-split\\HResult-HDecode\\test.txt'
    # output_dir = '.\\allosaurus-master\\FARSDAT-parent-all\\test'
    # output_allo_dir = '.\\FARSDAT-parent-all\\test'
    # prepareDataSet(file_classifier, output_dir, output_allo_dir, 'test ', 100)
