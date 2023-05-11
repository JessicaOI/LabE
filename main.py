from funciones import reescribir_archivo, get_values_list, get_variable_names
from AFN import regex_to_enfa, enfa_to_graphviz, generate_mega_enfa_graph

def main():
    yalex_file_name = "EjemploYalex.txt"
    input_file_name = "archivo_entrada.txt"

    with open(yalex_file_name, "r") as file:
        yalex_text = file.read()

    with open(input_file_name, "r") as file:
        input_text = file.read().replace('\n', '')

    rewritten_text = reescribir_archivo(yalex_text)

    if rewritten_text is None:
        print("Se detectaron errores en el archivo de entrada. Por favor, corrige los errores e intenta nuevamente.")
        return

    variable_names = get_variable_names(rewritten_text)
    resultado = get_values_list(rewritten_text)

    enfas = [regex_to_enfa(regex) for regex in resultado]

    categorias = {}
    for i, var_name in enumerate(variable_names):
        if i < len(resultado):
            categorias[resultado[i]] = var_name

    identifiers = [categorias.get(regex, "Desconocido") for regex in resultado]

    for idx, enfa in enumerate(enfas):
        identifier = identifiers[idx]
        enfa_graph = enfa_to_graphviz(enfa, identifier)
        enfa_graph.render(f"enfa_output_{idx}", view=True)

    mega_enfa_graph = generate_mega_enfa_graph(enfas, identifiers)
    mega_enfa_graph.render("mega_enfa_output", view=True)

    with open("compilado.py", "w") as compiled_file:
        compiled_file.write("import re\n\n")

        for regex, var_name in zip(resultado, identifiers):
            compiled_file.write(f"{var_name} = r\"{regex}\"\n")

        compiled_file.write("\n# Compilación de todas las expresiones regulares en una sola expresión\n")
        compiled_file.write("expresion_total = re.compile(")
        compiled_file.write("f\"(")
        compiled_file.write("|".join([f"{{{var_name}}}" for var_name in identifiers]))
        compiled_file.write(")\")\n")
        # compiled_file.write("print(expresion_total)\n")

        compiled_file.write(f'\n# Analizar el archivo de entrada\narchivo_entrada = "{input_text}"\n')
        compiled_file.write("def analizar(entrada):\n")
        compiled_file.write("    tokens = entrada.split()\n")
        compiled_file.write("    for token in tokens:\n")

        for i, var_name in enumerate(identifiers):
            if i == 0:
                compiled_file.write(f"        if re.match({var_name}, token):\n")
            else:
                compiled_file.write(f"        elif re.match({var_name}, token):\n")
            compiled_file.write(f"            print(f\"{var_name.capitalize()}: {{token}}\")\n")
            
        compiled_file.write("        else:\n")
        compiled_file.write("            print(f\"Error Sintactico(No reconocido): {token}\")\n")
        compiled_file.write("\n\nanalizar(archivo_entrada)\n")

if __name__ == "__main__":
    main()
