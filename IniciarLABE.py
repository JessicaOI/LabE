from analizador import *

from YAPar import *



def convert_productions(productions):
    converted_productions = {}
    for key, value in productions.items():
        converted_productions[key] = [prod.split() for prod in value]
    return converted_productions


# Leer el archivo Yalex
with open('slr-1.yal', 'r') as f:
    yalex_document = f.read()



header_result = ''
regex = {}
simple_pattern = r"\[(\w)\s*-\s*(\w)\]"
compound_pattern = r"\[(\w)\s*-\s*(\w)\s*(\w)\s*-\s*(\w)\]"
simple_regex_pattern = r"^let\s+\w+\s+=\s+(.*?)$"
documentRead = yalex_document
header_result, trailer_result, documentRead, i = crear_encabezado_y_trailer(documentRead)
documentRead = eliminar_comentarios(documentRead)
documentRead = sustituir_comillas(documentRead)
regex, errors, fin = construir_regex(documentRead, i)
yalexTokens, errors = generar_tokens(documentRead, regex, errors, fin + 1)


# Interpretando el archivo YAPar
tokens, productions_dict, errors = parse_yalp_file('slr-1.yalp', errors)
if errors:
    print("Error stack:")
    for error in errors:
        print(error)
    exit()

gooTokens = []

print("Validación de tokens Yapar segun las reglas del Yalex:")
for token in tokens:
    for lex_token in yalexTokens:
        evald = evaluando_Token(lex_token)
        if token == evald:
            gooTokens.append(token)
            print(f"Coinciden: {token}")
    if token not in gooTokens:
        errors.append(f"Token {token} no definido en el YALEX")

if len(gooTokens) < len(yalexTokens):
    errors.append("Falta instanciar tokens en el YAPAR")

if errors:
    print("Error:")
    for error in errors:
        print(error)
    exit()

print("Vaidacion exitosa! Todos coinciden")