import re

def analizar(entrada):
    entero = r"0|1|2|3|4|5|6|7|8|9"
    decimal = r"(0|1|2|3|4|5|6|7|8|9).(0|1|2|3|4|5|6|7|8|9)"
    hexadecimal = r"0[xX][0-9a-fA-F]+"
    operador = r"\+|\-|\*"
    potenciacion = r"\^"
    tabulaciones = r"\t|\n "
    expresion_total = re.compile(f"({entero}|{decimal}|{hexadecimal}|{operador}|{potenciacion}|{tabulaciones})")

    tokens = []
    for token in entrada.split():
        if re.match(entero, token):
            tokens.append(("Entero", token))
        elif re.match(decimal, token):
            tokens.append(("Decimal", token))
        elif re.match(hexadecimal, token):
            tokens.append(("Hexadecimal", token))
        elif re.match(operador, token):
            tokens.append(("Operador", token))
        elif re.match(potenciacion, token):
            tokens.append(("Potenciacion", token))
        elif re.match(tabulaciones, token):
            tokens.append(("Tabulaciones", token))
        else:
            tokens.append(("Error Sintactico", token))
    
    return tokens


def parse_yapar_file(filename):
    with open(filename, 'r') as file:
        content = file.read()

    tokens = []
    productions = {}
    current_production = None
    rules = []

    lines = content.split('\n')
    is_token_section = False
    is_production_section = False

    for line in lines:
        line = line.strip()
        if not line or line.startswith('/*'):
            continue

        if line.startswith('%token'):
            is_token_section = True
            tokens.extend(line[6:].strip().split(' '))
        elif line.startswith('IGNORE'):
            tokens.remove(line[6:].strip())
        elif line.startswith('%%'):
            is_token_section = False
            is_production_section = True
        elif is_production_section:
            if line.endswith(';'):
                rules.append(line[:-1])
                productions[current_production] = rules
                current_production = None
                rules = []
            elif line.endswith(':'):
                current_production = line[:-1]
            else:
                rules.append(line)

    return tokens, productions


filename = 'example.yalp'  # Cambia esto por el nombre de tu archivo YAPar
tokens, productions = parse_yapar_file(filename)
print("Tokens:", tokens)
print("Productions:", productions)

