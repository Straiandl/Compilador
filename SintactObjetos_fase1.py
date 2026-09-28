#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

import sys


class Alumno:
    def __init__(self, codigo: str):
        self.codigo = codigo

    def muestra(self):
        pass


class Bachillerato(Alumno):
    def __init__(self, codigo: str, preparatoria: str):
        super().__init__(codigo)
        self.preparatoria = preparatoria

    def muestra(self):
        print(f"[Alumno Bachillerato] Código: {self.codigo} | Preparatoria: {self.preparatoria}")


class Licenciatura(Alumno):
    def __init__(self, codigo: str, carrera: str, creditos: int):
        super().__init__(codigo)
        self.carrera = carrera
        self.creditos = creditos

    def muestra(self):
        print(f"[Alumno Licenciatura] Código: {self.codigo} | Carrera: {self.carrera} | Créditos: {self.creditos}")


class ElementoPila:
    def muestra(self):
        pass

    def __str__(self):
        return ""


class Terminal(ElementoPila):
    def __init__(self, tipo: int, simbolo: str):
        self.tipo = tipo
        self.simbolo = simbolo

    def muestra(self):
        print(f"Terminal('{self.simbolo}', tipo={self.tipo})", end=" ")

    def __str__(self):
        return self.simbolo


class NoTerminal(ElementoPila):
    def __init__(self, tipo: int, simbolo: str):
        self.tipo = tipo
        self.simbolo = simbolo

    def muestra(self):
        print(f"NoTerminal('{self.simbolo}', tipo={self.tipo})", end=" ")

    def __str__(self):
        return self.simbolo


class Estado(ElementoPila):
    def __init__(self, estado: int):
        self.estado = estado

    def muestra(self):
        print(f"Estado({self.estado})", end=" ")

    def __str__(self):
        return str(self.estado)


class Pila:
    def __init__(self):
        self.items = []

    def push(self, elem: ElementoPila):
        self.items.append(elem)

    def pop(self) -> ElementoPila:
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Intento de pop en una pila vacía.")

    def top(self) -> ElementoPila:
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Intento de top en una pila vacía.")

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def muestra(self):
        print("  Pila: [ " + " ".join(str(x) for x in self.items) + " ]")



class Token:
    """Token producido por el analizador léxico."""

    def __init__(self, tipo: int, lexema: str, linea: int, columna: int, nombre: str):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.nombre = nombre

    def __str__(self):
        return (
            f"{self.nombre:<15} "
            f"lexema={self.lexema!r:<18} "
            f"tipo={self.tipo:<2} "
            f"línea={self.linea:<3} "
            f"columna={self.columna}"
        )

    def muestra(self):
        print(self)


TIPOS_TOKEN = {
    "identificador": 0,
    "entero": 1,
    "real": 2,
    "cadena": 3,
    "tipo": 4,
    "opSuma": 5,
    "opMul": 6,
    "opRelac": 7,
    "opOr": 8,
    "opAnd": 9,
    "opNot": 10,
    "opIgualdad": 11,
    ";": 12,
    ",": 13,
    "(": 14,
    ")": 15,
    "{": 16,
    "}": 17,
    "=": 18,
    "if": 19,
    "while": 20,
    "return": 21,
    "else": 22,
    "$": 23,
}

PALABRAS_RESERVADAS = {
    "if": ("if", TIPOS_TOKEN["if"]),
    "while": ("while", TIPOS_TOKEN["while"]),
    "return": ("return", TIPOS_TOKEN["return"]),
    "else": ("else", TIPOS_TOKEN["else"]),
}

# El .inf define la categoría "tipo", pero no enumera aquí los lexemas.
# Se dejan centralizados para poder ajustarlos a la especificación del profesor.
TIPOS_DATOS = {"int", "float", "char", "void"}

OPERADORES_DOS = {
    "||": ("opOr", TIPOS_TOKEN["opOr"]),
    "&&": ("opAnd", TIPOS_TOKEN["opAnd"]),
    "==": ("opIgualdad", TIPOS_TOKEN["opIgualdad"]),
    "!=": ("opIgualdad", TIPOS_TOKEN["opIgualdad"]),
    "<=": ("opRelac", TIPOS_TOKEN["opRelac"]),
    ">=": ("opRelac", TIPOS_TOKEN["opRelac"]),
}

OPERADORES_UNO = {
    "+": ("opSuma", TIPOS_TOKEN["opSuma"]),
    "-": ("opSuma", TIPOS_TOKEN["opSuma"]),
    "*": ("opMul", TIPOS_TOKEN["opMul"]),
    "/": ("opMul", TIPOS_TOKEN["opMul"]),
    "<": ("opRelac", TIPOS_TOKEN["opRelac"]),
    ">": ("opRelac", TIPOS_TOKEN["opRelac"]),
    "!": ("opNot", TIPOS_TOKEN["opNot"]),
    "=": ("=", TIPOS_TOKEN["="]),
}

DELIMITADORES = {
    ";": (";", TIPOS_TOKEN[";"]),
    ",": (",", TIPOS_TOKEN[","]),
    "(": ("(", TIPOS_TOKEN["("]),
    ")": (")", TIPOS_TOKEN[")"]),
    "{": ("{", TIPOS_TOKEN["{"]),
    "}": ("}", TIPOS_TOKEN["}"]),
}


class ErrorLexico(Exception):
    def __init__(self, mensaje: str, linea: int, columna: int):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(mensaje)

    def __str__(self):
        return f"Error léxico en línea {self.linea}, columna {self.columna}: {self.mensaje}"


# ANALIZADOR LÉXICO


class Lexico:
    def __init__(self, cadena: str = ""):
        self.cadena = cadena
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.errores = []

    @classmethod
    def desde_archivo(cls, nombre_archivo: str):
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            return cls(archivo.read())

    def _actual(self):
        if self.pos >= len(self.cadena):
            return None
        return self.cadena[self.pos]

    def _mirar(self, n=1):
        return self.cadena[self.pos:self.pos + n]

    def _avanzar(self):
        if self.pos >= len(self.cadena):
            return
        c = self.cadena[self.pos]
        self.pos += 1
        if c == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1

    def _error(self, mensaje, linea=None, columna=None):
        self.errores.append(
            ErrorLexico(
                mensaje,
                self.linea if linea is None else linea,
                self.columna if columna is None else columna,
            )
        )

    def _identificador(self):
        linea, columna, inicio = self.linea, self.columna, self.pos
        while True:
            c = self._actual()
            if c is not None and (c.isalnum() or c == "_"):
                self._avanzar()
            else:
                break

        lexema = self.cadena[inicio:self.pos]
        if lexema in PALABRAS_RESERVADAS:
            nombre, tipo = PALABRAS_RESERVADAS[lexema]
        elif lexema in TIPOS_DATOS:
            nombre, tipo = "tipo", TIPOS_TOKEN["tipo"]
        else:
            nombre, tipo = "identificador", TIPOS_TOKEN["identificador"]
        return Token(tipo, lexema, linea, columna, nombre)

    def _numero(self):
        linea, columna, inicio = self.linea, self.columna, self.pos
        while self._actual() is not None and self._actual().isdigit():
            self._avanzar()

        es_real = False
        if self._actual() == ".":
            if len(self._mirar(2)) == 2 and self._mirar(2)[1].isdigit():
                es_real = True
                self._avanzar()
                while self._actual() is not None and self._actual().isdigit():
                    self._avanzar()
            else:
                self._error("Número mal formado: se esperaba un dígito después del punto.")
                self._avanzar()

        # Casos como 12abc no se consideran un número válido.
        c = self._actual()
        if c is not None and (c.isalpha() or c == "_"):
            while self._actual() is not None and (self._actual().isalnum() or self._actual() == "_"):
                self._avanzar()
            lexema = self.cadena[inicio:self.pos]
            self._error(f"Token numérico mal formado: {lexema!r}", linea, columna)
            return None

        lexema = self.cadena[inicio:self.pos]
        if es_real:
            return Token(TIPOS_TOKEN["real"], lexema, linea, columna, "real")
        return Token(TIPOS_TOKEN["entero"], lexema, linea, columna, "entero")

    def _cadena(self):
        linea, columna = self.linea, self.columna
        self._avanzar()  # comilla inicial
        caracteres = []
        while True:
            c = self._actual()
            if c is None:
                self._error("Cadena sin cerrar.", linea, columna)
                return None
            if c == '"':
                self._avanzar()
                return Token(TIPOS_TOKEN["cadena"], "".join(caracteres), linea, columna, "cadena")
            if c == "\n":
                self._error("Cadena sin cerrar antes del final de línea.", linea, columna)
                return None
            caracteres.append(c)
            self._avanzar()

    def _operador(self):
        linea, columna = self.linea, self.columna
        dos = self._mirar(2)
        if dos in OPERADORES_DOS:
            nombre, tipo = OPERADORES_DOS[dos]
            self._avanzar(); self._avanzar()
            return Token(tipo, dos, linea, columna, nombre)

        uno = self._actual()
        if uno in OPERADORES_UNO:
            nombre, tipo = OPERADORES_UNO[uno]
            self._avanzar()
            return Token(tipo, uno, linea, columna, nombre)
        return None

    def _delimitador(self):
        linea, columna = self.linea, self.columna
        c = self._actual()
        if c not in DELIMITADORES:
            return None
        nombre, tipo = DELIMITADORES[c]
        self._avanzar()
        return Token(tipo, c, linea, columna, nombre)

    def tokenizar(self):
        tokens = []
        while self.pos < len(self.cadena):
            c = self._actual()
            if c.isspace():
                self._avanzar()
                continue

            token = None
            if c.isalpha() or c == "_":
                token = self._identificador()
            elif c.isdigit():
                token = self._numero()
            elif c == '"':
                token = self._cadena()
            elif c in "+-*/<>=!&|":
                token = self._operador()
                if token is None:
                    self._error(f"Operador no reconocido: {c!r}")
                    self._avanzar()
            elif c in DELIMITADORES:
                token = self._delimitador()
            elif c == "$":
                linea, columna = self.linea, self.columna
                self._avanzar()
                token = Token(TIPOS_TOKEN["$"], "$", linea, columna, "$")
            else:
                self._error(f"Carácter no reconocido: {c!r}")
                self._avanzar()

            if token is not None:
                tokens.append(token)

        # Símbolo de fin de entrada esperado por la tabla LR.
        if not tokens or tokens[-1].tipo != TIPOS_TOKEN["$"]:
            tokens.append(Token(TIPOS_TOKEN["$"], "$", self.linea, self.columna, "$"))
        return tokens

#DEMOSTRACIONES

def ejemplo_polimorfismo():
    print("=" * 70)
    print("DEMO: POLIMORFISMO")
    print("=" * 70)
    alumnos = [
        Licenciatura("345678", "Computacion", 200),
        Bachillerato("456789", "Preparatoria 12"),
        Licenciatura("987654", "Informatica", 50),
    ]
    for alumno in reversed(alumnos):
        alumno.muestra()


def ejemplo_pila():
    print("\n" + "=" * 70)
    print("DEMO: PILA DE OBJETOS")
    print("=" * 70)
    pila = Pila()
    pila.push(Terminal(TIPOS_TOKEN["$"], "$"))
    pila.push(Estado(0))
    pila.push(Terminal(TIPOS_TOKEN["identificador"], "x"))
    pila.push(Estado(2))
    pila.muestra()
    print("Top:", pila.top())


def analizar_archivo(nombre_archivo: str):
    print("=" * 70)
    print(f"ANÁLISIS LÉXICO: {nombre_archivo}")
    print("=" * 70)
    try:
        lexico = Lexico.desde_archivo(nombre_archivo)
        tokens = lexico.tokenizar()
    except OSError as exc:
        print(f"No se pudo leer el archivo: {exc}")
        return 1

    print("\nTOKENS")
    print("-" * 70)
    for token in tokens:
        print(token)

    print("\nERRORES LÉXICOS")
    print("-" * 70)
    if lexico.errores:
        for error in lexico.errores:
            print(error)
    else:
        print("No se encontraron errores léxicos.")
    return 0


def main():
    if len(sys.argv) == 2:
        return analizar_archivo(sys.argv[1])

    ejemplo_polimorfismo()
    ejemplo_pila()
    print("\nPara analizar un archivo:")
    print("python SintactObjetos_fase1.py programa.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

