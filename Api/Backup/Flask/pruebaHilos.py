import time
# numeroCapturasAsincronas = 5
# tiempo = 100
# intervaloCapturasAsincronas = 1
# i = 0
# capturas = 0
# while i<numeroCapturasAsincronas:
#     # print("al inicio i:%s" %(i))
#     if tiempo >= intervaloCapturasAsincronas:
#         start_time_A = time.time()
#         capturas += 1
#         # time.sleep(1)
#         # data, c, d, f, sumaCapturado= capturaVueloApi(a, n, data, i)
#         # if f == "T":
#         #     errorCalGlobal = "T"
#         #     data['errorCal'] = "T"
#         # if c == "T":
#         #     errorCapturaGlobal = "T"
#         #     data['errorCapturaV'] = "T"
#         # if d =="T":
#         #     errorBdGlobal = "T"
#         #     data['errorBd'] = "T"
#         # print(c +" " + d)
#         print("dentro del if tiempo:%s" %(i))
#         i = i+1
#     else:
#         pass
#         # print("dentro del else i:%s" %(i))
#     end_time_A = time.time()
#     tiempo = end_time_A - start_time_A
# print(capturas)
with open("D:/Tesis/Code/Api/Flask/tmp/misioncmd.txt", 'w') as file_:
    print(" Write mission to file")
    file_.write("output")