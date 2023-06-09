import re

# Reemplaza las comillas en el contenido del archivo.
def sustituir_comillas(file_content):
    file_content = file_content.replace("\'\"\'","(' ハ ')")
    file_content = file_content.replace("\"\'\"","(' ワ ')")
    file_content = file_content.replace("\'`\'","(' カ ')")
    file_content = file_content.replace('"', " ' ")
    file_content = file_content.replace("'", " ' ")
    return file_content

# Limpia los comentarios del contenido del archivo.
def eliminar_comentarios(file_content):
    patron = re.compile(r'\(\*.*?\*\)', re.DOTALL)
    file_content = re.sub(patron, '', file_content)
    return file_content

# Construye la expresión regular a partir del contenido del archivo.
def construir_regex(file_content,inicio):
    ErrorStack = []
    patron = re.compile(r'\{.*?\}', re.DOTALL)
    content = re.sub(patron, '', file_content)
    content = content.split('\n')
    content = file_content.split('\n')
    simple_pattern = r"\[(\w)\s*-\s*(\w)\]"
    compound_pattern = r"\[(\w)\s*-\s*(\w)\s*(\w)\s*-\s*(\w)\]"
    simple_regex_pattern = r"^let\s+\w+\s+=\s+(.*?)$"
    regex = {}

    # Verificar llaves y paréntesis desbalanceados
    open_brackets = ['{', '(']
    close_brackets = ['}', ')']
    stack = []

    for line_num, line in enumerate(content, start=1):
        for char in line:
            if char in open_brackets:
                stack.append((char, line_num))
            elif char in close_brackets:
                if not stack or stack[-1][0] != open_brackets[close_brackets.index(char)]:
                    ErrorStack.append(f"Llaves o paréntesis desbalanceados en la línea {line_num+inicio}: {line}")
                    break
                else:
                    stack.pop()

        line = line.strip()
        if line:
            if re.match(simple_regex_pattern, line):
                regex,ErrorStack = agregar_regex_comun(line, regex, simple_pattern, compound_pattern,ErrorStack)
            elif line.startswith("let"):
                ErrorStack.append(f"Expresión regular inválida en la línea {line_num+inicio}: {line}")
            elif line.startswith("rule tokens"):
                break

    if stack:
        for bracket, line_num in stack:
            ErrorStack.append(f"Llave o paréntesis '{bracket}' sin cerrar en la línea {line_num+inicio}")

    fin = line_num+inicio
    return regex, ErrorStack,fin

# Verifica si existe un trailer en el contenido del archivo.
def revisar_trailer(content):
    has_header = True
    j = len(content) - 1
    while has_header:
        line = content[j].strip()
        if line:
            if 'return' in line or '|' in line:
                return False
            if line == "}" or "}" in line:
                return True
        j -= 1

# Verifica si existe un encabezado en el contenido del archivo.
def verificar_encabezado(content):
    has_header = True
    i = 0
    while has_header:
        line = content[i].strip()
        if line:
            if line == "{" or "{" in line:
                return True
        if 'let' in line or 'rule' in line:
            return False
        i += 1

# Construye el encabezado y el trailer a partir del contenido del archivo.
def crear_encabezado_y_trailer(file_content):
    content = file_content.split('\n')
    header_result = ''
    trailer_result = ''
    i = 0

    if verificar_encabezado(content):
        finished = False
        started = False
        while not finished:
            line = content[i]
            for element in line:
                if element == '{':
                    started = True
                if element != '{' and element != '}':
                    if started:
                        header_result += element
                if element == '}':
                    finished = True
                    header_result = header_result.rstrip()
                    break
            header_result += '\n'
            i += 1

    file_content = '\n'.join(content[i:])

    # Build trailer
    j = len(content) - 1
    if revisar_trailer(content):
        finished = False
        while not finished and j >= 0:
            line = content[j]
            temp_line = ''
            for element in line:
                if element != '{' and element != '}':
                    temp_line = element + temp_line
                if element == '{':
                    finished = True
                    temp_line = temp_line.rstrip()
                    
            trailer_result = temp_line + trailer_result
            if not finished:
                trailer_result = '\n' + trailer_result
            j -= 1
        real_trailer = ''
        for lines in range(j, len(content)):
            line = content[lines]
            for element in line:
                if element != '{' and element != '}':
                    real_trailer += element
                if element == '}':
                    real_trailer = real_trailer.rstrip()
                    break
            real_trailer += '\n'
        trailer_result = real_trailer
        
    

    file_content = '\n'.join(content[:j+1])
    return header_result, trailer_result, file_content, i

# Reemplaza los delimitadores en las expresiones.
def reemplazar_delimitadores(expressions):
    new_list = []
    for element in expressions:
        element = element.replace('\n', '')
        element = element.strip()
        new_list.append(element)
    return new_list

# Reemplaza las expresiones regulares existentes en la lista de expresiones.
def cambiar_regex_existente(expressions, regex):
    new_list = []
    for element in expressions:
        r = element[0]
        if r in regex:
            replacement = regex[r]
            element.append(replacement)
        new_list.append(element)
    return new_list

# Convierte las expresiones regulares en la lista de expresiones en tuplas.
def cambiar_regex_a_tuplas(expressions,regex,errorStack,inicio):
    simple_pattern = r"\[(\w)\s*-\s*(\w)\]"
    compound_pattern = r"\[(\w)\s*-\s*(\w)\s*(\w)\s*-\s*(\w)\]"
    new_list = []
    for element in expressions:
        line_number = inicio + expressions.index(element)
        splitted = re.split(r'\s+', element, maxsplit=1)
        if len(splitted) >= 2:
            first_part = splitted[0]
            if first_part not in regex.keys():
                first_part,errorStack = regex_habitual(first_part.split(" "),regex, simple_pattern, compound_pattern,errorStack,line_number)
            second_part = splitted[1].replace('\t', '')
            second_part = second_part.replace('{' , '')
            second_part = second_part.replace('}', '')
            second_part = second_part.strip()
            element = [first_part, second_part]
            new_list.append(element)
        else:
            errorStack.append(f"Error en la línea {line_number}: expresión no válida faltan parámetros")
    return new_list,errorStack

# Agrega el token de carácter especial a las expresiones.
def agregar_token_de_caracteres_especiales(expressions):
    new_list = []
    for element in expressions:
        expression = element[0]
        if "'" in expression or '"' in expression:
            element[0] = agregar_caracteres_string(expression)
        if "\\" in expression:
            element[0] = element[0].replace("\\", "")
        new_list.append(element)
    return new_list

# Recorta las comillas en una línea de texto.
def quitar_comillas(line):
    matches = re.findall(r"'([^']+)'", line)
    for element in matches:
        text = element
        line = line.replace("'" + text + "'", "'" + text.strip() + "'")
    return line

# Construye los tokens a partir del contenido del archivo y la expresión regular.
def generar_tokens(file_content, regex,errorStack,inicio):
    content = file_content.split('rule tokens =')
    content = quitar_comillas(content[1])
    content = content.strip().split('|')
    content = reemplazar_delimitadores(content)
    content,errorStack = cambiar_regex_a_tuplas(content,regex,errorStack,inicio)
    content = agregar_token_de_caracteres_especiales(content)
    content = cambiar_regex_existente(content, regex)
    return content,errorStack


def operadores_logicos(line):
    operators = '*+|?()'
    for operator in operators:
        line = line.replace(operator, ' ' + operator + ' ')
    return line


def intervalo_de_multiples_espacios(regex, search_spaces):
    space_map = {
        '\\s': r'\サ',
        '\\t': r'\ラ',
        '\\n': r'\ナ',
        '"': r'\"',
    }
    space_list = re.findall(r"(\\s|\\t|\\n)", search_spaces.group(0))
    space_regex = '|'.join([space_map[space_type] for space_type in space_list])
    regex = re.sub(r"\[(\\s|\\t|\\n|,|\s)+\]", f'({space_regex})', regex)
    #regex = regex.replace(search_spaces.group(0), f'({space_regex})')
    return regex

# Reemplaza los patrones comunes en una expresión regular.
def reemplazar_patrones_comunes(regex, simple_pattern, compound_pattern):
    search_spaces = re.search(r"\[(\\s|\\t|\\n|,|\s)+\]", regex)
    search_simple_regex_result = re.search(simple_pattern, regex)
    search_compound_regex_result = re.search(compound_pattern, regex)
    
    letters = 'abcdefghijklmnopqrstuvwxyz'
    upper_letters = letters.upper()
    numbers = '0123456789'

    if search_simple_regex_result and not search_compound_regex_result:
        regex = rango_simple(regex, search_simple_regex_result, letters, numbers,upper_letters)
    elif search_compound_regex_result:
        regex = rango_compuesto(regex, search_compound_regex_result, letters, numbers,upper_letters)
    elif search_spaces:
        regex = intervalo_de_multiples_espacios(regex, search_spaces)
    return regex

# Reemplaza el rango simple en una expresión regular.
def rango_simple(regex, search_simple_regex_result, letters, numbers,upper_letters):
    initial = search_simple_regex_result.group(1)
    final = search_simple_regex_result.group(2)
    result = remplazar_rango(initial, final, letters, numbers,upper_letters)
    result = '(' + result + ')'
    regex = regex.replace('['+initial+'-'+final+']', result)
    return regex

# Reemplaza el rango compuesto en una expresión regular.
def rango_compuesto(regex, search_compound_regex_result, letters, numbers,upper_letters):
    first_initial = search_compound_regex_result.group(1)
    first_final = search_compound_regex_result.group(2)

    last_initial = search_compound_regex_result.group(3)
    last_final = search_compound_regex_result.group(4)

    first_range = remplazar_rango(first_initial, first_final, letters, numbers,upper_letters)
    second_range = remplazar_rango(last_initial, last_final, letters, numbers,upper_letters)

    result = '(' + first_range + '|' + second_range + ')'
    replaced = ''
    i = 0
    closed = False
    while not closed:
        if regex[i] == ']':
            closed = True
        replaced += regex[i]
        i += 1
    regex = regex.replace(replaced, result)
    return regex

# Reemplaza el rango de caracteres en una expresión regular.
def remplazar_rango(initial, final, letters, numbers,upper_letters):
    result = str(initial) + '|'
    if initial.lower() in numbers and final.lower() in letters:
        result += quitar_numeros(initial, '9') + '|'
        initial_letter = 'A' if final in upper_letters else 'a'
        result += initial_letter + '|'
        result += quitar_strings(initial_letter, final, letters)
    elif initial.lower() in letters:
        final_letter = 'Z' if initial in upper_letters else 'z'
        if final in numbers:
            result += quitar_strings(initial, final_letter, letters) + '|'
            result += '0' + '|' + quitar_numeros('0', final)
        else:
            result += quitar_strings(initial, final, letters)
    elif initial in numbers:
            result += quitar_numeros(initial, final)
    return result

# Reemplaza el rango de letras en una expresión regular.
def quitar_strings(initial, final, letters):
    result = ''
    if ord(initial) > ord(final) and final.lower() in letters:
        result += quitar_strings(initial, 'z', letters) + '|'
        result += quitar_strings(chr(ord(initial.upper()) -1), final, letters)
    else:
        for i in range(ord(initial) + 1, ord(final)):
            between_letter = chr(i)
            result += between_letter + '|'
        result += final
    return result

# Reemplaza el rango de números en una expresión regular.
def quitar_numeros(initial, final):
    result = ''
    for i in range(int(initial) + 1, int(final)):
        result += str(i) + '|'
    result += final
    return result

# Genera una expresión regular común a partir de una línea de código.
def regex_habitual(line, regex, simple_pattern, compound_pattern, errorStack,line_number=0):
    body,erroStack = construir_regex_habitual(line, regex,errorStack,line_number)
    body = body.replace('ε', ' ')
    body = reemplazar_patrones_comunes(body, simple_pattern, compound_pattern)
    body = body.strip()
    return body,erroStack

# Agrega la expresión regular comun
def agregar_regex_comun(line, regex, simple_pattern, compound_pattern,errorStack):
    line = operadores_logicos(line)
    line = quitar_comillas(line)
    line = line.replace('" "', '"ε"')
    line = line.replace("' '", "'ε'")
    line = line.split(" ")
    body,errorStack = regex_habitual(line[3:], regex, simple_pattern, compound_pattern,errorStack)
    regex[line[1]] = body
    return regex,errorStack

# Construye la expresión regular común a partir de una línea de código.
def construir_regex_habitual(line, regex, errorStack, line_number=0):
    body = ''
    i = 0
    while i < len(line):
        element = line[i]
        if "'" in element or '"' in element or '`' in element:
            if "''" == element:
                body += "\\s"
            else:
                element = element.replace('"', '')
                element = element.replace("'", "")
                element = element.replace('+', '\+')
                element = element.replace('.', '\.')
                element = element.replace('*', '\*')
                element = element.replace('(', '\(')
                element = element.replace(')', '\)')
                body += element
        elif not verificar_operadores(element) and len(element) > 1:
            if element in regex:
                replacement = regex[element]
                body += replacement
            else:
                errorStack.append(f"Error: {element} no se encuentra definido en la línea {line_number}: {line}")
        else:
            body += element
        i += 1
    return body, errorStack

# Verifica si un elemento contiene operadores.
def verificar_operadores(element):
    operators = '*+|?'
    for operator in operators:
        if operator in element:
            return True
    return False

# Agrega caracteres de escape a una expresión regular que representa una cadena de texto.
def agregar_caracteres_string(expression):
    expression = expression.replace('.', '\.')
    expression = expression.replace('+', '\+')
    expression = expression.replace('*', '\*')
    expression = expression.replace('"', '')
    expression = expression.replace("'", "")
    return expression

# Evalúa un token y devuelve el resultado.
def evaluando_Token(token):
    return eval(token[1])

#Formatea el contenido de Yalex.
def ajustar_contenido_yalex(yalex_content):
    file_content = yalex_content
    header_result, file_content = crear_encabezado_y_trailer(file_content)
    file_content = eliminar_comentarios(file_content)
    file_content = sustituir_comillas(file_content)
    regex = construir_regex(file_content)
    tokens = generar_tokens(file_content, regex)
    return header_result, regex, tokens