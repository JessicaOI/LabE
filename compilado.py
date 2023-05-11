import re

entero = r"0|1|2|3|4|5|6|7|8|9"
decimal = r"(0|1|2|3|4|5|6|7|8|9).(0|1|2|3|4|5|6|7|8|9)"
hexadecimal = r"0[xX][0-9a-fA-F]+"
operador = r"\+|\-|\*"
potenciacion = r"\^"
tabulaciones = r"\t|\n "

# Compilación de todas las expresiones regulares en una sola expresión
expresion_total = re.compile(f"({entero}|{decimal}|{hexadecimal}|{operador}|{potenciacion}|{tabulaciones})")

# Analizar el archivo de entrada
archivo_entrada = "9 8.5 0xA1B2 + - * / ^ 2 14 3.1 0x12345 * / ^ + - 5 ?"
def analizar(entrada):
    tokens = entrada.split()
    for token in tokens:
        if re.match(entero, token):
            print(f"Entero: {token}")
        elif re.match(decimal, token):
            print(f"Decimal: {token}")
        elif re.match(hexadecimal, token):
            print(f"Hexadecimal: {token}")
        elif re.match(operador, token):
            print(f"Operador: {token}")
        elif re.match(potenciacion, token):
            print(f"Potenciacion: {token}")
        elif re.match(tabulaciones, token):
            print(f"Tabulaciones: {token}")
        else:
            print(f"Error Sintactico(No reconocido): {token}")


analizar(archivo_entrada)
