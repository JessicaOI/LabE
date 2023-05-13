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
    print("Errores encontrados:")
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


converted_productions = convert_productions(productions_dict)

states, transitions = canonical_collection(converted_productions)

converted_prod = convert_productions(productions_dict)
first = first_sets(converted_prod)
follow = follow_sets(converted_prod, first)
print("\n", "First sets:")
for non_terminal, first_set in first.items():
    print(f"{non_terminal}: {first_set}")

print("\n", "Follow sets:")
for non_terminal, follow_set in follow.items():
    print(f"{non_terminal}: {follow_set}")

print('\n', 'Estados:')
for i, state in enumerate(states):
    print(f'{i}: {state}')

print('\n', 'Transiciones:')
for transition in transitions:
    print(transition)

generate_lr0_diagram(states, transitions)
