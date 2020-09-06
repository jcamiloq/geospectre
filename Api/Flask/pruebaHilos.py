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
wavelenghtsLista = []
script_dir = os.path.dirname(__file__)
print(script_dir)
rel_path = '\\testy\cult2\wavevis.txt'
wav = os.path.join(script_dir+rel_path)
print(wav)
with open(wav, "r") as wavevis:
    for line in wavevis:
        line = line[:-4]
        wavelenghtsLista.append(line)