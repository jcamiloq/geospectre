# import concurrent.futures

# def foo(bar):
#     print('hello {}'.format(bar))
#     return 'foo'

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     future = executor.submit(foo, 'world!')
#     return_value = future.result()
#     print(return_value)
listaComandos = []
with open("tmp/asd.txt", 'w') as file_:
    print(" Write mission to file")
    file_.write("output")
with open("tmp/asd.txt", "r") as m:
    for line in m:
        listaComandos.append(line)
print(listaComandos)
print(listaComandos[0][0:-2])