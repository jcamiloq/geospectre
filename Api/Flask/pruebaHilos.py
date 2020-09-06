# import concurrent.futures

# def foo(bar):
#     print('hello {}'.format(bar))
#     return 'foo'

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     future = executor.submit(foo, 'world!')
#     return_value = future.result()
#     print(return_value)
import os
from os import path
from file_management import FileManagement
wavelenghtsLista = []
wav = FileManagement.to_relative("/testy/cult2/wavevis.txt")
print(wav)
with open(wav, "r") as wavevis:
    for line in wavevis:
        line = line[:-4]
        wavelenghtsLista.append(line)