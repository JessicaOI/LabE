from probando import analizar, parse_yapar_file


def main():
    # Lee el contenido del archivo YAPar
    with open("example.yalp", "r") as file:
        yapar_content = file.read()

    # Llama al analizador léxico con el contenido de YAPar
    lex_tokens = analizar(yapar_content)

    # Llama a la función parse_yapar_file
    tokens, productions = parse_yapar_file(yapar_content)

    # Imprime la información extraída
    print("Tokens analizados:")
    for token in lex_tokens:
        print(token)

    print("\nTokens:")
    for token in tokens:
        print(token)

    print("\nProducciones:")
    for production, rules in productions.items():
        print(f"{production}:")
        for rule in rules:
            print(f"  {rule}")

if __name__ == "__main__":
    main()
