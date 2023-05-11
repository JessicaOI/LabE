import re

# Definición de las expresiones regulares para cada token
entero = r"[0-9]+"
decimal = r"[0-9]*\.[0-9]+"
hexadecimal = r"0[xX][0-9a-fA-F]+"
operador = r"[\+\-\*/]"
potenciacion = r"\^"
tabulaciones = r"[ \t\n]"

# Compilación de todas las expresiones regulares en una sola expresión
expresion_total = re.compile(f"({entero}|{decimal}|{hexadecimal}|{operador}|{potenciacion}|{tabulaciones})")
print(expresion_total)
# Analizar el archivo de entrada
archivo_entrada = "10 20.5 0xA1B2 + - * / ^\n42 3.14 0x12345 * / ^ + -"

def analizar(entrada):
    tokens = expresion_total.findall(entrada)
    for token in tokens:
        if re.match(entero, token):
            print(f"Entero: {token}")
        elif re.match(decimal, token):
            print(f"Decimal: {token}")
        elif re.match(hexadecimal, token):
            print(f"Hexadecimal: {token}")
        elif re.match(operador, token):
            print(f"Operador aritmético: {token}")
        elif re.match(potenciacion, token):
            print(f"Operador de potenciación: {token}")
        elif re.match(tabulaciones, token):
            pass  # Ignorar espacios, tabulaciones y saltos de línea

analizar(archivo_entrada)
