# Analizador Léxico y Sintáctico LR(1) en Python

Proyecto académico para la fase de **análisis léxico y análisis sintáctico** de un traductor para un lenguaje de programación simplificado. Está implementado en Python y reutiliza estructuras de programación orientada a objetos, incluyendo una pila con terminales, no terminales y estados.

El analizador léxico lee un archivo de código fuente y genera tokens. Si no encuentra errores léxicos, el parser carga la tabla LR(1) de `compilador.lr` y determina si la secuencia de tokens cumple la gramática.

> **Alcance:** este proyecto analiza la estructura léxica y sintáctica del lenguaje. No genera código objeto ni ejecuta los programas.

## Contenido del proyecto

| Archivo | Descripción |
|---|---|
| `SintactObjetos_completo.py` | Programa principal con lexer y parser LR(1). |
| `compilador.inf` | Referencia entregada por el profesor: categorías y números de token, además de las producciones de la gramática. El programa no necesita leerlo directamente. |
| `compilador.lr` | Archivo que el programa carga para obtener las reglas de reducción y la tabla LR(1). |
| `programa_valido.txt` | Entrada de prueba sintácticamente válida. |
| `error_lexico.txt` | Entrada con un carácter no reconocido para probar los errores léxicos. |
| `error_sintactico.txt` | Entrada con una estructura incorrecta para probar los errores sintácticos. |
| `salida_parser_valido.txt` | Ejemplo de salida de una ejecución válida. |
| `salida_error_lexico.txt` | Ejemplo de salida con error léxico. |
| `salida_error_sintactico.txt` | Ejemplo de salida con error sintáctico. |

## Requisitos

- Python 3.
- Los archivos de prueba y `compilador.lr` deben estar disponibles en las rutas indicadas al ejecutar el programa.
- No requiere instalar bibliotecas externas.

## Cómo ejecutar

Abre una terminal en la carpeta del proyecto.

### Analizar un programa válido

```bash
python SintactObjetos_completo.py programa_valido.txt
```

### Probar un error léxico

```bash
python SintactObjetos_completo.py error_lexico.txt
```

### Probar un error sintáctico

```bash
python SintactObjetos_completo.py error_sintactico.txt
```

El programa lee el nombre del archivo fuente desde el argumento que se escribe después del nombre del script. Por defecto, busca `compilador.lr` en la misma carpeta que el archivo Python. Si la tabla está en otra ubicación, se puede indicar explícitamente:

```bash
python SintactObjetos_completo.py programa_valido.txt --lr ruta/a/compilador.lr
```

Para guardar la salida de una prueba en un archivo de texto, puede usarse la redirección de la terminal:

```bash
python SintactObjetos_completo.py programa_valido.txt > salida_parser_valido.txt
```

En Windows, los comandos también pueden ejecutarse desde PowerShell o la terminal de Visual Studio Code.

## Flujo de análisis

```text
Archivo de código fuente (.txt)
              |
              v
      Analizador léxico
              |
              v
         Lista de Token
              |
       ¿Hay errores léxicos?
          /          \
        Sí            No
        |              |
        v              v
 Reportar errores   Cargar compilador.lr
   y detener              |
                          v
                   Parser LR(1)
                          |
                          v
                 Aceptar o rechazar
                  por sintaxis
```

## Analizador léxico

El lexer recorre el archivo fuente y agrupa caracteres en unidades llamadas **tokens**. Cada objeto `Token` guarda:

- `tipo`: número asociado a la categoría del token según `compilador.inf`.
- `lexema`: texto encontrado en el código.
- `linea`: línea donde comienza el token.
- `columna`: columna donde comienza el token.
- `nombre`: nombre legible de la categoría.

Al final de la entrada se agrega el símbolo `$`, usado por la tabla LR como marcador de fin de entrada.

### Categorías de tokens

Los números siguientes corresponden a los valores proporcionados en `compilador.inf`.

| Categoría | Número |
|---|---:|
| `identificador` | 0 |
| `entero` | 1 |
| `real` | 2 |
| `cadena` | 3 |
| `tipo` | 4 |
| `opSuma` | 5 |
| `opMul` | 6 |
| `opRelac` | 7 |
| `opOr` | 8 |
| `opAnd` | 9 |
| `opNot` | 10 |
| `opIgualdad` | 11 |
| `;` | 12 |
| `,` | 13 |
| `(` | 14 |
| `)` | 15 |
| `{` | 16 |
| `}` | 17 |
| `=` | 18 |
| `if` | 19 |
| `while` | 20 |
| `return` | 21 |
| `else` | 22 |
| `$` | 23 |

**Nota sobre la especificación:** `compilador.inf` indica las categorías y sus números, pero no enumera todos los lexemas concretos para categorías como `tipo` u operadores. En esta implementación se han usado provisionalmente `int`, `float`, `char`, `void`, `+`, `-`, `*`, `/`, comparadores y operadores lógicos comunes. Estas asociaciones deben ajustarse si el profesor proporcionó otra especificación de lexemas.

## Manejo de errores léxicos

El analizador puede reportar, entre otros casos:

- Caracteres no reconocidos, por ejemplo `@`.
- Números mal formados, por ejemplo `12abc` o un número con punto sin dígitos decimales.
- Cadenas que no tienen comilla de cierre.

Los errores incluyen la línea y la columna en la que se detectaron. Cuando hay errores léxicos, el programa imprime los tokens que pudo reconocer y los mensajes de error, y no continúa con el análisis sintáctico.

## Analizador sintáctico LR(1)

La clase `ParserLR` carga el archivo `compilador.lr`. En el archivo se encuentran las reglas de reducción, las dimensiones de la tabla y la matriz de acciones/transiciones.

Para la gramática entregada, la tabla contiene **52 reglas, 95 estados y 46 columnas**. El parser consulta la tabla con el estado actual de la pila y el número del token de entrada.

Las acciones de la tabla se interpretan así:

- **Desplazamiento (`shift`)**: se introduce el token actual y el nuevo estado en la pila.
- **Reducción (`reduce`)**: se retiran de la pila los elementos correspondientes al lado derecho de una producción y se introduce el no terminal resultante junto con el estado de transición.
- **Aceptación**: la entrada cumple la gramática.
- **Error sintáctico**: la tabla no define una acción válida para el estado y el token actual.

El parser utiliza las clases `Pila`, `Terminal`, `NoTerminal` y `Estado` para representar el proceso mediante objetos.

## Pruebas incluidas

### 1. Programa válido: `programa_valido.txt`

```c
int main() {
    return 0;
}
```

Resultado esperado: el analizador léxico produce los tokens y el parser acepta la cadena.

### 2. Error léxico: `error_lexico.txt`

```c
int main() {
    return 0 @;
}
```

Resultado esperado: se informa que `@` no es un carácter reconocido y no se ejecuta el parser.

### 3. Error sintáctico: `error_sintactico.txt`

```c
int main( {
    return 0;
}
```

Resultado esperado: los símbolos se tokenizan, pero el parser rechaza la estructura sintáctica.

## Clases principales

| Clase | Responsabilidad |
|---|---|
| `Alumno` | Clase base del ejemplo de herencia. |
| `Bachillerato` y `Licenciatura` | Subclases que redefinen `muestra()` y demuestran polimorfismo. |
| `ElementoPila` | Clase base de los elementos utilizados por la pila LR. |
| `Terminal` | Representa un token terminal dentro de la pila sintáctica. |
| `NoTerminal` | Representa un no terminal después de una reducción. |
| `Estado` | Guarda un estado del autómata LR. |
| `Pila` | Administra los objetos utilizados por el parser. |
| `Token` | Almacena tipo, lexema, línea, columna y nombre de categoría. |
| `Lexico` | Lee el texto fuente y genera una lista de tokens. |
| `ErrorLexico` | Representa y presenta errores del análisis léxico. |
| `ParserLR` | Carga `compilador.lr` y ejecuta el análisis sintáctico. |

## Decisiones de diseño

1. **Objetos para los tokens:** cada token contiene el lexema y su ubicación, lo cual facilita la impresión de resultados y la localización de errores.
2. **Tabla externa:** la matriz LR se carga de `compilador.lr` en vez de escribirla manualmente dentro del código.
3. **Separación de fases:** el análisis sintáctico solo comienza cuando el lexer no reporta errores.
4. **Pila polimórfica:** los estados, terminales y no terminales se representan con distintas clases derivadas de `ElementoPila`.
5. **Entradas separadas:** los programas de prueba se guardan en archivos `.txt`, por lo que se pueden cambiar sin modificar el código fuente del analizador.

## Limitaciones actuales

- La implementación solo realiza análisis léxico y sintáctico; no genera código intermedio ni ejecutable.
- Las palabras concretas aceptadas como tipos de datos y algunos operadores se basan en supuestos provisionales hasta confirmar todos los lexemas del lenguaje con la documentación completa del curso.
- El análisis sintáctico determina si la secuencia de tokens pertenece a la gramática; no valida aspectos semánticos como variables declaradas, tipos compatibles o funciones existentes.
