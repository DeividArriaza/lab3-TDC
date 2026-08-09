# lab3-TDC

Laboratorio #3 — Teoría de la Computación, CC2019 · UVG · Semestre 2, 2026

| Archivo | Punto | Qué hace |
|---|---|---|
| `posfix_arbol_sintactico.py` | 1 | infix → postfix → árbol sintáctico → imagen |
| `afd_directo.py` | 2 | construcción directa del AFD desde el árbol |
| `expresiones.txt` | — | las expresiones a procesar, una por línea |

---

## Requisitos

### Python 3

Sin librerías adicionales para el Punto 2. `afd_directo.py` corre tal cual.

### Graphviz — necesario solo para generar las imágenes

Para dibujar los árboles hacen falta **dos cosas distintas**, y es el error más
común al montar el proyecto desde cero:

**1. El binario del sistema** (el programa `dot`, que es quien realmente
dibuja):

```bash
# Debian / Ubuntu
sudo apt install graphviz

# Fedora
sudo dnf install graphviz

# macOS
brew install graphviz

# Windows
winget install graphviz
```

**2. El paquete de Python** (una envoltura que genera el texto en formato DOT y
se lo pasa al binario anterior):

```bash
pip install graphviz
```

Instalar solo el paquete de `pip` **no alcanza**: al correr el programa aparece
`ExecutableNotFound`, porque falta el `dot`.

Para verificar que ambos quedaron bien:

```bash
dot -V                              # debe imprimir la version de graphviz
python3 -c "import graphviz"        # no debe imprimir nada
```

### Si no se instala Graphviz

El programa **igual corre**: detecta que falta la librería y simplemente no
genera las imágenes. La salida de texto (expresión, postfix y posiciones) se
imprime normal, y el Punto 2 no se ve afectado en nada. Solo se pierden los
`.png`.

Para ver el árbol en la terminal sin graphviz está `imprimir_arbol(raiz)`, que
lo dibuja en texto rotado 90°: la raíz contra el margen izquierdo, el hijo
derecho arriba y el izquierdo abajo.

---

## Uso

```bash
python3 posfix_arbol_sintactico.py    # Punto 1
python3 afd_directo.py                # Punto 2
```

Ambos leen `expresiones.txt`. Para probar otras expresiones basta con agregarlas
ahí, una por línea; las líneas vacías y las que empiezan con `#` se ignoran.

Las imágenes se generan en `arboles/`, una por expresión (`arbol_1.png`,
`arbol_2.png`, …), y se regeneran cada vez que se corre el Punto 1.

---

## Convenciones de la entrada

| Símbolo | Significado |
|---|---|
| `\|` | unión |
| `.` | concatenación (puede omitirse: `ab` equivale a `a.b`) |
| `*` | cerradura de Kleene |
| `+` | una o más repeticiones |
| `?` | opcional |
| `( )` | agrupación |
| `ε` o `~` | cadena vacía (`~` es un alias en ASCII, por comodidad al escribir) |
| `\x` | el símbolo `x` deja de ser operador y pasa a ser parte del alfabeto |

En el árbol final **no quedan nodos `+` ni `?`**: se expanden con
`r+ → r·r*` y `r? → ε|r`. La copia de `r` en la expansión de `+` es profunda,
para que cada ocurrencia reciba su propia posición.

---

## Salida del Punto 2

Por cada expresión se imprimen tres tablas:

1. Posiciones, su símbolo y su `siguientepos`
2. **2.a** — tabla de transiciones del AFD
3. **2.b** — estados y las posiciones que conforma cada uno

En la tabla de transiciones, `->` marca el estado inicial, `*` los de
aceptación y `-` que no hay transición con ese símbolo (el AFD queda parcial,
sin estado de error explícito).
