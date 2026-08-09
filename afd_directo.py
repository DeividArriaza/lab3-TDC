"""
Laboratorio #3 - Teoría de la Computación, CC2019, UVG

Parte 2: construcción directa del AFD a partir del árbol sintáctico.

Reutiliza el árbol del Punto 1 (posfix_arbol_sintactico.py). Sobre ese árbol
calcula anulable, primerapos y ultimapos en post-orden, y de ahí siguientepos.
Con siguientepos arma el AFD por subconjuntos de posiciones.

Como el Punto 1 ya expande "+" y "?", en el árbol solo quedan hojas y los
operadores "*", "." y "|", así que cada función tiene apenas cuatro casos.

Por cada expresión imprime:
  - posiciones y su siguientepos
  - tabla de transiciones del AFD        (inciso 2.a)
  - estados y las posiciones que lo forman  (inciso 2.b)
"""

from posfix_arbol_sintactico import (
    EPSILON,
    Nodo,
    a_postfix,
    construir_arbol,
    es_hoja,
    leer_expresiones,
    numerar_posiciones,
    postfix_a_texto,
    simbolo_legible,
)

MARCA_FIN = "#"                        # símbolo de fin de la expresión aumentada
ARCHIVO_EXPRESIONES = "expresiones.txt"


def aumentar(raiz, posicion_fin):
    """Devuelve la raíz de (r)·# , con # en la última posición."""
    fin = Nodo(MARCA_FIN)
    fin.posicion = posicion_fin
    return Nodo(".", raiz, fin)


def calcular_funciones(nodo, siguiente):
    """
    Recorrido post-orden: calcula anulable, primerapos y ultimapos de cada
    nodo, y va llenando el diccionario siguiente (siguientepos).

    Es post-orden porque cada nodo necesita que sus hijos ya estén resueltos.
    """
    if nodo is None:
        return

    calcular_funciones(nodo.izquierdo, siguiente)
    calcular_funciones(nodo.derecho, siguiente)

    izq = nodo.izquierdo
    der = nodo.derecho

    if es_hoja(nodo):
        if nodo.valor == EPSILON:
            nodo.anulable = True
            nodo.primerapos = set()
            nodo.ultimapos = set()
        else:
            nodo.anulable = False
            nodo.primerapos = {nodo.posicion}
            nodo.ultimapos = {nodo.posicion}

    elif nodo.valor == "|":
        nodo.anulable = izq.anulable or der.anulable
        nodo.primerapos = izq.primerapos | der.primerapos
        nodo.ultimapos = izq.ultimapos | der.ultimapos

    elif nodo.valor == ".":
        nodo.anulable = izq.anulable and der.anulable
        # Si el izquierdo puede desaparecer, el derecho también puede ir primero.
        if izq.anulable:
            nodo.primerapos = izq.primerapos | der.primerapos
        else:
            nodo.primerapos = set(izq.primerapos)
        if der.anulable:
            nodo.ultimapos = izq.ultimapos | der.ultimapos
        else:
            nodo.ultimapos = set(der.ultimapos)
        # Regla 1: lo que cierra la izquierda es seguido por lo que abre la derecha.
        for posicion in izq.ultimapos:
            siguiente[posicion] |= der.primerapos

    elif nodo.valor == "*":
        nodo.anulable = True
        nodo.primerapos = set(izq.primerapos)
        nodo.ultimapos = set(izq.ultimapos)
        # Regla 2: lo que cierra el bucle es seguido por lo que lo reabre.
        for posicion in nodo.ultimapos:
            siguiente[posicion] |= nodo.primerapos

    else:
        raise ValueError(f"Operador inesperado en el árbol: {nodo.valor}")


def construir_afd(raiz, siguiente, simbolo_de, posicion_fin):
    """
    Construcción por subconjuntos: cada estado es un conjunto de posiciones.

    Devuelve (estados, transiciones, alfabeto), donde estados es la lista de
    conjuntos en orden de descubrimiento y transiciones es un diccionario
    {(indice_estado, simbolo): indice_destino}.
    """
    alfabeto = sorted({simbolo_de[p] for p in simbolo_de if p != posicion_fin})

    inicial = frozenset(raiz.primerapos)
    estados = [inicial]
    indice = {inicial: 0}
    transiciones = {}
    pendientes = [inicial]

    while len(pendientes) > 0:
        actual = pendientes.pop(0)

        for simbolo in alfabeto:
            # Unión de siguientepos de las posiciones etiquetadas con ese símbolo.
            destino = set()
            for posicion in actual:
                if simbolo_de[posicion] == simbolo:
                    destino |= siguiente[posicion]

            if len(destino) == 0:
                continue     # sin transición: el AFD queda parcial

            destino = frozenset(destino)
            if destino not in indice:
                indice[destino] = len(estados)
                estados.append(destino)
                pendientes.append(destino)

            transiciones[(indice[actual], simbolo)] = indice[destino]

    return estados, transiciones, alfabeto


def conjunto_a_texto(conjunto):
    """{3, 1, 2} -> '{1, 2, 3}'"""
    return "{" + ", ".join(str(p) for p in sorted(conjunto)) + "}"


def imprimir_tabla(encabezados, filas):
    """Imprime una tabla de texto con las columnas alineadas."""
    anchos = [len(h) for h in encabezados]
    for fila in filas:
        for i in range(len(fila)):
            anchos[i] = max(anchos[i], len(fila[i]))

    print("  " + " | ".join(encabezados[i].ljust(anchos[i])
                            for i in range(len(encabezados))))
    print("  " + "-+-".join("-" * a for a in anchos))
    for fila in filas:
        print("  " + " | ".join(fila[i].ljust(anchos[i])
                                for i in range(len(fila))))


def procesar(expresion):
    """Corre la construcción directa completa e imprime las dos tablas."""
    postfix = a_postfix(expresion)
    arbol = construir_arbol(postfix)          # ya expande "+" y "?"
    hojas = numerar_posiciones(arbol)

    posicion_fin = len(hojas) + 1
    raiz = aumentar(arbol, posicion_fin)

    simbolo_de = {hoja.posicion: hoja.valor for hoja in hojas}
    simbolo_de[posicion_fin] = MARCA_FIN

    siguiente = {posicion: set() for posicion in simbolo_de}
    calcular_funciones(raiz, siguiente)

    print("Expresion regular:", expresion)
    print("En postfix:       ", postfix_a_texto(postfix))
    print()

    print("Posiciones y siguientepos:")
    imprimir_tabla(
        ["Posicion", "Simbolo", "siguientepos"],
        [[str(p), simbolo_legible(simbolo_de[p]), conjunto_a_texto(siguiente[p])]
         for p in sorted(simbolo_de)],
    )
    print()

    estados, transiciones, alfabeto = construir_afd(
        raiz, siguiente, simbolo_de, posicion_fin)

    print("2.a  Tabla de transiciones:")
    filas = []
    for i in range(len(estados)):
        marca = "->" if i == 0 else "  "
        if posicion_fin in estados[i]:
            marca = marca + "*"
        else:
            marca = marca + " "
        fila = [marca + "S" + str(i)]
        for simbolo in alfabeto:
            destino = transiciones.get((i, simbolo))
            fila.append("-" if destino is None else "S" + str(destino))
        filas.append(fila)
    imprimir_tabla(["Estado"] + [simbolo_legible(s) for s in alfabeto], filas)
    print("  (-> estado inicial, * estado de aceptacion, - sin transicion)")
    print()

    print("2.b  Estados y posiciones que los conforman:")
    imprimir_tabla(
        ["Estado", "Posiciones", "Aceptacion"],
        [["S" + str(i),
          conjunto_a_texto(estados[i]),
          "si" if posicion_fin in estados[i] else "no"]
         for i in range(len(estados))],
    )


if __name__ == "__main__":

    for expresion in leer_expresiones(ARCHIVO_EXPRESIONES):
        try:
            procesar(expresion)
        except ValueError as error:
            print("Expresion regular:", expresion)
            print("Error:", error)
        print()
        print("=" * 60)
        print()
