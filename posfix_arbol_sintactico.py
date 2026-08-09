"""
Laboratorio #3 - Teoría de la Computación, CC2019, UVG

Parte 1: conversión de infix a postfix (Shunting Yard).

Es el algoritmo del Laboratorio #2 (inciso 4), recortado a lo que necesita
este laboratorio: se quitaron los símbolos compuestos y la descripción del
postfix, que eran propios del enunciado anterior.

Sobre este postfix se construye después el árbol sintáctico.

Convenciones de entrada
-----------------------
  |        unión
  .        concatenación (también puede omitirse: "ab" es lo mismo que "a.b")
  *        cerradura de Kleene
  +        una o más repeticiones
  ?        opcional
  ( )      agrupación
  ε o ~    la cadena vacía (el "~" es un alias en ASCII, por comodidad al
           escribir; internamente se guarda siempre como ε)
  \\x       el símbolo x deja de ser operador y pasa a ser parte del alfabeto
           (por ejemplo "\\." es un punto literal, no una concatenación)
"""

try:
    from graphviz import Digraph
except ImportError:
    # Sin la librería el programa igual corre; solo no genera las imágenes.
    Digraph = None

# Las cuatro expresiones del enunciado, con la letra de su inciso.
# El programa lee normalmente el archivo de texto; este diccionario es el
# respaldo por si el archivo no está, y sirve de referencia rápida.
expresiones = {
    "a": "(a*|b*)+",
    "b": "((ε|a)|b*)*",
    "c": "(a|b)*abb(a|b)*",
    "d": "0?(1?)?0*",
}

EPSILON = "ε"
ALIAS_EPSILON = "~"

# Mayor número = mayor precedencia (se aplica primero)
PRECEDENCIA = {
    "*": 3,   # cerradura de Kleene
    "+": 3,   # una o más repeticiones
    "?": 3,   # opcional
    ".": 2,   # concatenación
    "|": 1,   # unión
}

UNARIOS = "*+?"    # van después de su operando
BINARIOS = ".|"    # van en medio de sus dos operandos

ARCHIVO_EXPRESIONES = "expresiones.txt"
CARPETA_IMAGENES = "arboles"

class Nodo:
    def __init__(self, valor, izquierdo=None, derecho=None):
        self.valor = valor
        self.izquierdo = izquierdo
        self.derecho = derecho
        self.posicion = None

    def __repr__(self):
        return f"Nodo({self.valor})"

def es_simbolo(token):
    """
    True si el token es un símbolo del alfabeto y no un operador ni un
    paréntesis de agrupación.
    """
    if token == "(" or token == ")":
        return False
    if token in PRECEDENCIA:
        return False
    return True


def simbolo_legible(token):
    """Quita la barra invertida de un símbolo escapado: '\\(' -> '('."""
    if len(token) == 2 and token[0] == "\\":
        return token[1]
    return token


def tokenizar(expresion):
    """
    Parte la expresión regular en una lista de tokens.

        "(a|b)*"   ->  ['(', 'a', '|', 'b', ')', '*']
        "a\\.b"     ->  ['a', '\\.', 'b']
    """
    tokens = []
    i = 0

    while i < len(expresion):
        caracter = expresion[i]

        if caracter == " ":
            i = i + 1
            continue

        if caracter == "\\":
            # La barra invertida escapa al siguiente caracter: ese caracter
            # deja de ser operador y pasa a ser un símbolo del alfabeto.
            if i + 1 >= len(expresion):
                raise ValueError("La expresión termina en una '\\' suelta")
            tokens.append("\\" + expresion[i + 1])
            i = i + 2
            continue

        if caracter == ALIAS_EPSILON:
            tokens.append(EPSILON)
            i = i + 1
            continue

        tokens.append(caracter)
        i = i + 1

    return tokens


def puede_cerrar(token):
    """True si el token puede ser el final de una subexpresión."""
    if token == ")":
        return True
    if token in UNARIOS:
        return True
    return es_simbolo(token)


def puede_abrir(token):
    """True si el token puede ser el inicio de una subexpresión."""
    if token == "(":
        return True
    return es_simbolo(token)


def agregar_concatenacion(tokens):
    """
    Inserta el operador "." donde la concatenación estaba implícita.

    Va entre dos tokens cuando el de la izquierda cierra una subexpresión y
    el de la derecha abre otra.

        ['a', 'b']            ->  ['a', '.', 'b']
        ['a', '*', '(', 'b']  ->  ['a', '*', '.', '(', 'b']
    """
    resultado = []
    i = 0

    while i < len(tokens):
        if i > 0 and puede_cerrar(tokens[i - 1]) and puede_abrir(tokens[i]):
            resultado.append(".")
        resultado.append(tokens[i])
        i = i + 1

    return resultado


def a_postfix(expresion):
    """
    Convierte la expresión regular a postfix y devuelve la lista de tokens.

    Recorre los tokens de izquierda a derecha con una lista de salida y una
    pila de operadores en espera.
    """
    tokens = agregar_concatenacion(tokenizar(expresion))

    salida = []   # aquí se va armando el resultado
    pila = []     # operadores que todavía están en espera

    for token in tokens:

        if token in UNARIOS:
            # Como van después de su operando, cuando aparecen su operando ya
            # está completo en la salida. Salen de una vez, sin pasar por la
            # pila y sin esperar a nadie.
            salida.append(token)

        elif token in BINARIOS:
            # Sale de la pila todo operador que ya tenga su operando derecho
            # completo. La concatenación y la unión son asociativas por la
            # izquierda, así que también sale el que empata en precedencia.
            while len(pila) > 0 and pila[-1] != "(":
                if PRECEDENCIA[pila[-1]] >= PRECEDENCIA[token]:
                    salida.append(pila.pop())
                else:
                    break
            pila.append(token)

        elif token == "(":
            # El paréntesis que abre es un muro: nada se saca más allá de él.
            pila.append(token)

        elif token == ")":
            while len(pila) > 0 and pila[-1] != "(":
                salida.append(pila.pop())
            if len(pila) == 0:
                raise ValueError("Paréntesis desbalanceados: sobra un ')'")
            pila.pop()   # descarta el "(" que hacía de muro

        else:
            # Es un símbolo del alfabeto: sale directo, nunca espera.
            salida.append(token)

    # Se terminó la expresión, así que se vacía la pila de arriba hacia abajo.
    while len(pila) > 0:
        operador = pila.pop()
        if operador == "(":
            raise ValueError("Paréntesis desbalanceados: sobra un '('")
        salida.append(operador)

    return salida


def postfix_a_texto(postfix):
    """
    Une los tokens del postfix en una sola cadena.

    Si todos los símbolos son de un caracter se pegan sin separador. Si hay
    símbolos de varios caracteres se separan con espacios, porque si no la
    salida sería ilegible.
    """
    separador = ""

    for token in postfix:
        if len(token) > 1:
            separador = " "

    return separador.join(postfix)

def clonar(nodo):
    """Copia profunda del subárbol: nodos nuevos, no referencias compartidas."""
    if nodo is None:
        return None
    return Nodo(nodo.valor, clonar(nodo.izquierdo), clonar(nodo.derecho))


def expandir_unario(token, operando):
    """
    Devuelve el nodo que representa a 'operando' afectado por el token unario.

        r+  ->  r . r*     (el segundo r es una copia, no el mismo objeto)
        r?  ->  ε | r
        r*  ->  se queda igual
    """
    if token == "+":
        # La copia es obligatoria: cada r necesita sus propias posiciones.
        return Nodo(".", operando, Nodo("*", clonar(operando)))

    if token == "?":
        return Nodo("|", Nodo(EPSILON), operando)

    return Nodo(token, izquierdo=operando)


def construir_arbol(postfix):
    """
    Arma el árbol sintáctico a partir del postfix y devuelve su raíz.

    Los operadores "+" y "?" se expanden al vuelo, así que en el árbol
    resultante solo quedan hojas y los operadores "*", "." y "|".
    """
    pila = []
    for token in postfix:
        if token in UNARIOS:
            # Operador unario: toma un solo operando de la pila
            if len(pila) < 1:
                raise ValueError(f"Al operador '{token}' le falta su operando")
            operando = pila.pop()
            nodo = expandir_unario(token, operando)
            pila.append(nodo)
        elif token in BINARIOS:
            # Operador binario: toma dos operandos de la pila
            if len(pila) < 2:
                raise ValueError(f"Al operador '{token}' le faltan operandos")
            derecho = pila.pop()
            izquierdo = pila.pop()
            nodo = Nodo(token, izquierdo=izquierdo, derecho=derecho)
            pila.append(nodo)
        elif es_simbolo(token):
            # Símbolo del alfabeto: crea un nodo hoja
            nodo = Nodo(token)
            pila.append(nodo)
        else:
            raise ValueError(f"Token desconocido: {token}")

    # Si sobra más de un subárbol, el postfix estaba incompleto.
    if len(pila) != 1:
        raise ValueError("Postfix mal formado: la expresión no está completa")

    return pila.pop()  # El último nodo en la pila es la raíz del árbol


def es_hoja(nodo):
    """True si el nodo no tiene hijos."""
    return nodo.izquierdo is None and nodo.derecho is None


def numerar_posiciones(raiz):
    """
    Numera de izquierda a derecha las hojas que no son ε (recorrido in-orden).

    Devuelve la lista de hojas numeradas, en orden de posición.
    """
    hojas = []

    def recorrer(nodo):
        if nodo is None:
            return
        recorrer(nodo.izquierdo)
        if es_hoja(nodo) and nodo.valor != EPSILON:
            hojas.append(nodo)
            nodo.posicion = len(hojas)   # las posiciones arrancan en 1
        recorrer(nodo.derecho)

    recorrer(raiz)
    return hojas

def etiqueta(nodo):
    """Texto visible del nodo; las hojas numeradas llevan su posición."""
    texto = simbolo_legible(nodo.valor)
    if nodo.posicion is not None:
        return f"{texto} ({nodo.posicion})"
    return texto


def dibujar(nodo, dot):
    """
    Agrega el nodo y su subárbol al Digraph.
    Devuelve el id del nodo creado, para que su padre pueda conectarlo.
    """
    # id() es único por objeto, así que dos hojas 'a' nunca colisionan.
    mi_id = str(id(nodo))

    if es_hoja(nodo):
        dot.node(mi_id, etiqueta(nodo), shape="circle")
    else:
        dot.node(mi_id, etiqueta(nodo), shape="box")

    # El izquierdo se agrega primero para que quede a la izquierda.
    if nodo.izquierdo is not None:
        dot.edge(mi_id, dibujar(nodo.izquierdo, dot))
    if nodo.derecho is not None:
        dot.edge(mi_id, dibujar(nodo.derecho, dot))

    return mi_id


def generar_imagen(raiz, nombre, expresion):
    """Genera <nombre>.png con el árbol. Devuelve la ruta o None si falla."""
    if Digraph is None:
        return None

    # ordering='out' conserva el orden izquierda-derecha de los hijos.
    dot = Digraph(graph_attr={"ordering": "out", "label": expresion,
                              "labelloc": "t"})
    dibujar(raiz, dot)

    try:
        return dot.render(nombre, directory=CARPETA_IMAGENES,
                          format="png", cleanup=True)
    except Exception as error:
        print("No se pudo generar la imagen:", error)
        return None


def leer_expresiones(ruta):
    """
    Devuelve las expresiones del archivo, una por línea.

    Se ignoran las líneas en blanco y las que empiezan con "#", para poder
    dejar comentarios dentro del archivo.

    Si el archivo no existe se usan las del diccionario 'expresiones'.
    """
    lista = []

    try:
        with open(ruta, encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea == "" or linea.startswith("#"):
                    continue
                lista.append(linea)
    except FileNotFoundError:
        print("No se encontró", ruta, "- se usan las expresiones del programa.")
        print()
        for inciso in sorted(expresiones):
            lista.append(expresiones[inciso])

    return lista


def procesar(expresion, nombre):
    """Muestra la ejecución completa: infix, postfix, árbol e imagen."""
    postfix = a_postfix(expresion)
    print("Expresion regular:", expresion)
    print("En postfix:       ", postfix_a_texto(postfix))

    arbol = construir_arbol(postfix)
    hojas = numerar_posiciones(arbol)

    print("Posiciones:", ", ".join(
        f"{h.posicion}={simbolo_legible(h.valor)}" for h in hojas))

    ruta = generar_imagen(arbol, nombre, expresion)
    if ruta is not None:
        print("Imagen:", ruta)

    return arbol


if __name__ == "__main__":

    numero = 1

    for expresion in leer_expresiones(ARCHIVO_EXPRESIONES):
        try:
            procesar(expresion, f"arbol_{numero}")
        except ValueError as error:
            print("Expresion regular:", expresion)
            print("Error:", error)
        numero = numero + 1
        print()
