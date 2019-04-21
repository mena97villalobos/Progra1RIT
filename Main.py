import math
import os
import re
import unicodedata
import time

stopWords = [""]
lista_frecuencias = []
lista_pesos = []
lista_doc = []
lista_size = []
lista_normas = []
dic_vocabulario = {}
avg_size = 0
norma_q = 0
dic_ni = {}
prefijo = ""
Salida = ""
archivo_html = ""
consulta = ""
dic_consulta = {}
num_inicio = 0
num_fin = 0
N = 0
# html
inicio_tabla = "<html><head>" \
               "<style>" \
               "div.container{width: 100%; border: 1px solid gray;} " \
               "header, footer{padding: 1em; color: white; background-color: black; clear: left; text-align: center;}"\
               "table#t01 tr:nth-child(even){background-color: #eee;} " \
               "table#t01 tr:nth-child(odd){background-color:#fff;} " \
               "table#t01 th{background-color: black; color: white;} " \
               "article {padding: 1em; overflow: hidden;} " \
               "table {width:100%;} " \
               "table, th, td {border: 1px solid black; border-collapse: collapse;} " \
               "th, td{padding: 5px; text-align: left;}" \
               "</style>" \
               "</head><header> " \
               "<title>TP1 RIT</title> " \
               "<h1> Tarea Programada 1 RIT </h1> " \
               "<h2> Escalafón</h2></header><body>" \
               "<article><table id=\"t01\">" \
               "<tr><th>Posición</th><th>Ruta</th><th>Fecha de Creación</th><th>Tamaño</th>" \
               "<th>Descripción</th><th>Similitud</th></tr>"
fin_tabla = "</table></article></body></html>"


def revisar_directorio(path):
    doc = []
    with os.scandir(path) as i:
        for entry in i:
            if entry.is_file():
                doc += [entry.path]
            else:
                doc += revisar_directorio(entry.path)
    return doc


def stopwords(file):
    global stopWords
    try:
        archivo = open(file, "r")
        contenido = archivo.read()
        stopWords += contenido.split("\n")
        return True
    except:
        print("Archivo de stopwords no existe")
        return False


def normalizar(string):
    string = string.lower()
    string = string.replace('ñ', '\001')
    string = ''.join(c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn')
    string = string.replace("[\\p{InCombiningDiacriticalMarks}]", "")
    string = string.replace('\001', 'ñ')
    return string


def limpiar_contenido(path, identificador):
    global stopWords, dic_ni
    string_frec = "<ID>" + str(identificador) + "</ID>"
    string_descrip = "<ID>" + str(identificador) + "</ID>"
    string_word_size = "<ID>" + str(identificador) + "</ID>"
    f = open(Salida + "/" + prefijo + "_FC.txt", "a+")
    f2 = open(Salida + "/" + prefijo + "_DES.txt", "a+")
    f3 = open(Salida + "/" + prefijo + "_SIZE.txt", "a+")
    dic_frecuencias = {}
    # Expresiones regulares
    puntos = "\.\w+"
    puntos = re.compile(puntos)
    puntos2 = "(\w+\.)+\w+"
    puntos2 = re.compile(puntos2)
    descripcion = "(DESCRIPCIÓN)(\s*)((.|\s){1,200})"
    descripcion = re.compile(descripcion)
    #
    archivo = open(path, "r")
    file_size = str(os.path.getsize(path))
    creation = str(time.ctime(os.path.getctime(path)))
    string_descrip += "<Size>" + file_size + "</Size>" + "<Creación>" + creation + "</Creación>"
    contenido = archivo.read()
    archivo.close()
    contenido = re.sub("(\s*)\xad(\n*)(\s*)", "", contenido)
    contenido = re.sub("\.{2,}", " ", contenido)
    contenido = re.sub("\.\s", " ", contenido)
    contenido = re.sub("\s+", " ", contenido)
    try:
        descripcion = descripcion.findall(contenido)[0]
        string_descrip += "<Descripción>" + descripcion[2] + "</Descripción>\n"
    except:
        string_descrip += "<Descripción>" + "--NO POSEE DESCRIPCIÓN--" + "</Descripción>\n"
    contenido = normalizar(contenido)
    contenido = re.sub("[^a-z0-9\n\s.]", " ", contenido)
    contenido = contenido.split(" ")
    string_word_size += "<Size>" + str(len(contenido)) + "</Size>\n"
    index = 0
    contenido = list(sorted([i for i in contenido if i not in stopWords]))
    for i in contenido:
        remplazo = i
        if puntos.match(i):
            remplazo = i.replace(".", "")
            contenido[index] = remplazo
        if puntos2.match(i):
            nuevos = i.split(".")
            contenido += nuevos
            for j in nuevos:
                try:
                    dic_frecuencias[j] += 1
                except:
                    dic_frecuencias[j] = 1
                    try:
                        dic_ni[j] += 1
                    except:
                        dic_ni[j] = 1
        else:
            try:
                dic_frecuencias[remplazo] += 1
            except:
                dic_frecuencias[remplazo] = 1
                try:
                    dic_ni[remplazo] += 1
                except:
                    dic_ni[remplazo] = 1
        index += 1
    string_frec += "<NumTerminos>" + str(len(dic_frecuencias)) + "</NumTerminos>"
    string_frec += "<Pares>" + str(dic_frecuencias) + "</Pares>\n"
    f.write(string_frec)
    f2.write(string_descrip)
    f3.write(string_word_size)
    f.close()
    f2.close()
    f3.close()
    return dic_frecuencias


def crear_coleccion(path, num_arch):
    global Salida, prefijo
    f = open(Salida + "/" + prefijo + "_CO.txt", "w")
    path = os.path.abspath(path)
    f.write("<Nombre>" + os.path.basename(path) + "</Nombre>" +
            "<Directorio>" + path + "</Directorio>" +
            "<Numero_Doc>" + str(num_arch) + "</Numero_Doc>" + "\n")
    f.close()


def crear_pesos(frecuencias, identificador):
    global dic_ni, N
    f = open(Salida + "/" + prefijo + "_PE.txt", "a+")
    string_pesos = "<ID>" + str(identificador) + "</ID>" + "<NumTerminos>" + \
                   str(len(frecuencias)) + "</NumTerminos>" + "<Pesos>{"
    norma = 0
    for key, value in frecuencias.items():
        if not value > N/2:
            peso = round((1 + math.log2(value)) * (math.log2(N / dic_ni[key])), 4)
            norma += (peso * peso)
            string_pesos += "\'" + key + "\'" + ": " + str(peso) + ", "
    string_pesos += "}</Pesos><Norma>" + str(round(math.sqrt(norma), 4)) + "</Norma>\n"
    f.write(string_pesos)
    f.close()


def analizar(documentos):
    global lista_frecuencias, N, dic_ni
    doc_file = ""
    identificador = 1
    for doc in documentos:
        doc_file += "<ID>" + str(identificador) + "</ID>" + "<Path>" + doc + "</Path>\n"
        frecuencias = limpiar_contenido(doc, identificador)
        lista_frecuencias += [frecuencias]
        identificador += 1
    for i in range(0, N):
        crear_pesos(lista_frecuencias[i], i + 1)
    f = open(Salida + "/" + prefijo + "_DO.txt", "w")
    f.write(doc_file)
    f.close()
    f = open(Salida + "/" + prefijo + "_VO.txt", "w")
    f.write(str(dic_ni))
    f.close()


def obtener_datos(identificador):
    global prefijo
    # Expresiones regulares para extraer datos
    descripcion_re = "(<Descripción>)((.|\s)*)(<\/Descripción>)"
    descripcion_re = re.compile(descripcion_re)
    size_re = "(<Size>)(\d*)(</Size>)"
    size_re = re.compile(size_re)
    creacion_re = "(<Creación>)(\w+\s\w+\s+\d+\s.+\s\d{4})(<\/Creación>)"
    creacion_re = re.compile(creacion_re)
    #
    string_id = "<ID>" + str(identificador) + "</ID>"
    des = ""
    size = ""
    creacion = ""
    f = open(Salida + "/" + "TEST" + "_DES.txt", "r")
    line = f.readline()
    while line:
        if string_id in line:
            des += descripcion_re.findall(line)[0][1]
            size += size_re.findall(line)[0][1]
            creacion += creacion_re.findall(line)[0][1]
            break
        line = f.readline()
    f.close()
    return des, size, creacion


def cargar_pesos():
    global lista_pesos, lista_normas, prefijo
    lista_pesos = []
    lista_normas = []
    f = open(Salida + "/" + prefijo + "_PE.txt", "r")
    pesos_re = "(<Pesos>)(.)*(<\/Pesos>)"
    pesos_re = re.compile(pesos_re)
    norma_re = "(<Norma>)(\d*\.+\d*)(</Norma>)"
    norma_re = re.compile(norma_re)
    line = f.readline()
    while line:
        pesos = pesos_re.search(line).group()
        pesos = pesos.replace("<Pesos>", "")
        pesos = pesos.replace("</Pesos>", "")
        pesos = eval(pesos)
        norma = norma_re.search(line).group()
        norma = norma.replace("<Norma>", "")
        norma = norma.replace("</Norma>", "")
        norma = float(norma)
        lista_pesos += [pesos]
        lista_normas += [norma]
        line = f.readline()
    f.close()


def cargar_doc():
    global lista_doc
    lista_doc = []
    f = open(Salida + "/" + prefijo + "_DO.txt", "r")
    identificacion = 1
    line = f.readline()
    while line:
        id_aux = "<ID>" + str(identificacion) + "</ID><Path>"
        line = line.replace(id_aux, "")
        line = line.replace("</Path>", "")
        lista_doc += [line]
        line = f.readline()
        identificacion += 1
    f.close()


def cargar_frec():
    global lista_frecuencias, prefijo
    lista_frecuencias = []
    f = open(Salida + "/" + prefijo + "_FC.txt", "r")
    frec_re = "(<Pares>)(.)*(<\/Pares>)"
    frec_re = re.compile(frec_re)
    line = f.readline()
    while line:
        frec = frec_re.search(line).group()
        frec = frec.replace("<Pares>", "")
        frec = frec.replace("</Pares>", "")
        frec = eval(frec)
        lista_frecuencias += [frec]
        line = f.readline()
    f.close()


def cargar_sizes():
    global lista_size, avg_size, N
    lista_size = []
    f = open(Salida + "/" + prefijo + "_SIZE.txt", "r")
    identificacion = 1
    line = f.readline()
    while line:
        id_aux = "<ID>" + str(identificacion) + "</ID><Size>"
        line = line.replace(id_aux, "")
        line = int(line.replace("</Size>", ""))
        lista_size += [line]
        avg_size += line
        line = f.readline()
        identificacion += 1
    N = identificacion
    avg_size /= identificacion
    f.close()


def cargar_vocabulario():
    global prefijo, dic_vocabulario
    f = open(Salida + "/" + prefijo + "_VO.txt", "r")
    dic_vocabulario = eval(f.read())


def similitud_vec(doc_id):
    global dic_consulta, lista_normas, lista_pesos, norma_q
    similitud = 0
    pesos_actuales = lista_pesos[doc_id - 1]
    for key, value in dic_consulta.items():
        try:
            similitud += value * (pesos_actuales[key])
        except:
            continue
    similitud /= (lista_normas[doc_id - 1] * norma_q)
    return similitud


def transformar_consulta():
    global consulta, dic_vocabulario, N
    consulta = re.sub("(\s*)\xad(\n*)(\s*)", "", consulta)
    consulta = re.sub("\.{2,}", " ", consulta)
    consulta = re.sub("\.\s", " ", consulta)
    consulta = normalizar(consulta)
    consulta = re.sub("[^a-z0-9\n\s.]", " ", consulta)
    consulta = re.sub("\s+", " ", consulta)


def calcular_pesos_consulta():
    global consulta, norma_q
    norma_q = 0
    consulta = consulta.split(" ")
    for i in consulta:
        try:
            frec = dic_vocabulario[i]
            peso = round((1 + math.log2(frec)) * (math.log2(N / frec)), 4)
            dic_consulta[i] = peso
            norma_q += (peso * peso)
        except:
            dic_consulta[i] = 0
    norma_q = math.sqrt(norma_q)


def obtener_rangos(size):
    global num_inicio, num_fin
    if num_inicio > size:
        return -1, -1
    elif num_fin + 1 > size:
        return num_inicio, size
    else:
        return num_inicio, num_fin + 1


def idf(q_i):
    global dic_vocabulario, N
    try:
        n = dic_vocabulario[q_i]
        aux = N - n + 0.5
        aux /= n + 0.5
        return math.log2(aux)
    except:
        return 0


def similitud_bm25(identificador):
    global consulta, lista_frecuencias, avg_size, lista_size, lista_normas, stopWords
    frecuencias = lista_frecuencias[identificador-1]
    suma = 0
    norma = lista_normas[identificador-1]
    consulta = [i for i in consulta if i not in stopWords]
    for i in consulta:
        idf_qi = idf(i)
        try:
            fqd = frecuencias[i]
        except:
            fqd = 0
        suma += idf_qi * ((2.5 * fqd)/(fqd + (1.5 * (norma / avg_size))))
    return suma


def vectorial_main():
    global lista_doc
    lista_similitudes = []
    identificador = 1
    for _ in lista_doc:
        lista_similitudes += [[identificador, similitud_vec(identificador)]]
        identificador += 1
    lista_similitudes = sorted(lista_similitudes, key=lambda doc_sim: doc_sim[1])
    lista_similitudes = lista_similitudes[::-1]
    rango = obtener_rangos(len(lista_similitudes) - 1)
    if rango[0] == -1 and rango[1] == -1:
        return []
    else:
        return lista_similitudes[rango[0]:rango[1]]


def bm25():
    global lista_doc
    lista_similitudes = []
    identificador = 1
    for _ in lista_doc:
        lista_similitudes += [[identificador, similitud_bm25(identificador)]]
        identificador += 1
    lista_similitudes = sorted(lista_similitudes, key=lambda doc_sim: doc_sim[1])
    lista_similitudes = lista_similitudes[::-1]
    rango = obtener_rangos(len(lista_similitudes) - 1)
    if rango[0] == -1 and rango[1] == -1:
        return []
    else:
        return lista_similitudes[rango[0]:rango[1]]


def crear_html(escalafon):
    global lista_doc, inicio_tabla, fin_tabla
    posicion = 1
    string_html = inicio_tabla
    for i in escalafon:
        identificador = i[0]
        similitud = i[1]
        info = obtener_datos(identificador)
        path = lista_doc[identificador - 1]
        fila = "<tr>" \
               "<th>" + str(posicion) + "</th>" \
               "<th>" + path + "</th>" \
               "<th>" + info[2] + "</th>" \
               "<th>" + info[1] + "</th>" \
               "<th>" + info[0] + "</th>" \
               "<th>" + str(similitud) + "</th></tr>"
        string_html += fila
        posicion += 1
    string_html += fin_tabla
    f = open(Salida + "/" + archivo_html, "w")
    f.write(string_html)
    f.close()


def imprimir_ayuda():
    print("********************************************************************************")
    print("* Creado por Bryan Mena 2016112933 Tarea Programada 1 RIT                      *")
    print("* Para analizar una colección el formato del comando es el siguiente:          *")
    print("* generar Stopwords Directorio Prefijo                                         *")
    print("* Stopwords: Path al archivo de stopwords                                      *")
    print("* Directorio: Path a la colección que se desea analizar                        *")
    print("* Prefijo: Prefijo usado en los archivos generados                             *")
    print("********************************************************************************")
    print("* Para buscar en una colección el formato del comando es el siguiente:         *")
    print("* buscar Modalidad NumInicio  NumFin  Prefijo  ArchivoHTML  Consulta           *")
    print("* Modalidad: Tipo de consulta que se usará para crear el escalafón (vec | bm25)*")
    print("* NumInicio / NumFin: Rango de posiciones que seran incluidas en el escalafón  *")
    print("* Prefijo: Prefijo usado por los archivos generados en los que se desea buscar *")
    print("* ArchivoHTML: Nombre del archivo HTML de salida                               *")
    print("* Consulta: Lista de terminos que forman la consulta                           *")
    print("********************************************************************************\n")


def main():
    global prefijo, N, num_inicio, num_fin, archivo_html, consulta
    print("Ingrese un comando o -h para ayuda")
    while True:
        comando = input()
        if "generar" in comando:
            comando = comando.split(" ")
            comando.pop(0)
            if not stopwords(comando[0]):
                pass
            else:
                comando.pop(0)
                prefijo = comando[-1]
                documentos = revisar_directorio(comando[0])
                N = len(documentos)
                crear_coleccion(comando[0], N)
                analizar(documentos)
        elif "buscar" in comando:
            comando = comando.split(" ")
            comando.pop(0)
            num_inicio = int(comando[1])
            num_fin = int(comando[2])
            prefijo = comando[3]
            archivo_html = comando[4]
            consulta = " ".join(comando[5:])
            cargar_pesos()
            cargar_frec()
            cargar_sizes()
            cargar_doc()
            cargar_vocabulario()
            transformar_consulta()
            if comando[0] == "vec":
                calcular_pesos_consulta()
                escalafon = vectorial_main()
                crear_html(escalafon)
            elif comando[0] == "bm25":
                consulta = consulta.split(" ")
                escalafon = bm25()
                crear_html(escalafon)
            else:
                print("Comando invalido")
        elif "-h" == comando:
            imprimir_ayuda()
        else:
            print("Comando invalido")
        print("Salir?(Y/N): ", end="")
        salir = input()
        if salir.lower() == "y":
            break


if __name__ == '__main__':
    Salida = os.getcwd() + "/Salida"
    os.makedirs(Salida, exist_ok=True)
    main()
