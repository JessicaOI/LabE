import re
from graphviz import Digraph


# Genera un gráfico del autómata LR(0) utilizando la biblioteca Graphviz.
def generate_lr0_diagram(states, transitions):
    dot = Digraph("LR0", format='png')
    dot.attr(rankdir="LR")
    dot.attr('node', shape='rectangle')

    accept_state = len(states) - 1

    for i, state in enumerate(states):
        if i == accept_state:  # Estado de aceptación
            label = 'ACEPTAR'
        else:
            non_derived = [str(item) for item in state if not item.derived]
            derived = [str(item) for item in state if item.derived]

            label = f'Estado {i}\n'
            label += 'No derivadas:\n'
            label += '\n'.join(non_derived) + '\n'
            label += 'Derivadas:\n'
            label += '\n'.join(derived)



        dot.node(str(i), label=label)

    for t in transitions:
        dot.edge(str(t[0]), str(t[2]), label=t[1])

    # Generar y guardar el gráfico como imagen PNG
    dot.render("DiagramaLR0", cleanup=True)
    print("Diagrama LR0 generado")


# Obtiene los conjuntos de terminales y no terminales a partir de las producciones.
def get_terminals_and_non_terminals(productions):
    non_terminals = set(productions.keys())
    terminals = set()

    for non_terminal in non_terminals:
        for production in productions[non_terminal]:
            for symbol in production:
                if symbol not in non_terminals:
                    terminals.add(symbol)

    return terminals, non_terminals

# Calcula los conjuntos First para cada no terminal en las producciones.
def first_sets(productions):
    terminals, non_terminals = get_terminals_and_non_terminals(productions)
    first = {non_terminal: set() for non_terminal in non_terminals}

    changed = True
    while changed:
        changed = False
        for non_terminal in non_terminals:
            for production in productions[non_terminal]:
                for symbol in production:
                    if symbol in terminals:
                        if symbol not in first[non_terminal]:
                            first[non_terminal].add(symbol)
                            changed = True
                        break
                    else:
                        added = len(first[non_terminal])
                        first[non_terminal].update(first[symbol] - {None})
                        if len(first[non_terminal]) != added:
                            changed = True
                        if None not in first[symbol]:
                            break
                else:
                    if None not in first[non_terminal]:
                        first[non_terminal].add(None)
                        changed = True

    return first


# Calcula los conjuntos Follow para cada no terminal en las producciones, utilizando los conjuntos First.
def follow_sets(productions, first_sets):
    _, non_terminals = get_terminals_and_non_terminals(productions)
    follow = {non_terminal: set() for non_terminal in non_terminals}
    follow[next(iter(non_terminals))].add('$')

    changed = True
    while changed:
        changed = False
        for non_terminal in non_terminals:
            for production in productions[non_terminal]:
                for i, symbol in enumerate(production):
                    if symbol in non_terminals:
                        if i + 1 < len(production):
                            next_symbol = production[i + 1]
                            if next_symbol in non_terminals:
                                added = len(follow[symbol])
                                follow[symbol].update(first_sets[next_symbol] - {None})
                                if len(follow[symbol]) != added:
                                    changed = True
                            else:
                                if next_symbol not in follow[symbol]:
                                    follow[symbol].add(next_symbol)
                                    changed = True
                        else:
                            added = len(follow[symbol])
                            follow[symbol].update(follow[non_terminal])
                            if len(follow[symbol]) != added:
                                changed = True

    return follow

# Divide el contenido del archivo YALP en secciones de tokens y producciones.
def split_sections(content):
    errorStack = []
    tokens_section = None
    productions_section = None
    sections = content.split('%%')
    if len(sections)!= 2:
        errorStack.append("Error: No se encuentra la división '%%' entre las secciones de tokens y producciones.")
    else:
        tokens_section = sections[0]
        productions_section = sections[1]
    return tokens_section, productions_section,errorStack


# Procesa la sección de tokens y devuelve la lista de tokens.
def process_tokens_section(content):
    tokens = []
    lines = content.split('\n')
    for line in lines:
        if line.startswith("%token"):
            line_tokens = line[len("%token"):].strip().split(' ')
            tokens.extend(line_tokens)
    return tokens

# Procesa la sección de producciones y devuelve un diccionario con las producciones.
def process_productions_section(content):
    productions = {}
    current_production = None
    production_rules = []

    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Si la línea contiene dos puntos (:), la consideramos como el nombre de una producción
        if line.endswith(':'):
            if current_production:
                productions[current_production] = production_rules
                production_rules = []

            current_production = line[:-1]

        # Si la línea contiene un punto y coma (;), finalizamos la producción actual
        elif line.endswith(';'):
            line = line[:-1]
            if line != "":
                production_rules.append(line)

            productions[current_production] = production_rules
            production_rules = []
            current_production = None

        # Si la línea contiene una flecha (->) o una barra (|), la consideramos como una regla de producción
        else:
            production_rules.extend(re.split(r'\s*\|\s*', line))

    return productions


# Valida el contenido del archivo YALP y devuelve una lista de errores si hay alguno.
def validate_yalp(tokens_section, productions_section, tokens, productions):
    error_stack = []

    # Verificar si existe la división '%%'
    if not tokens_section or not productions_section:
        error_stack.append("Error: Los siguientes simbolos: '%%' no se encuentran en el archivo")

    # Verificar si tiene el símbolo '%' antes de la declaración de tokens
    lines = tokens_section.split('\n')
    for line in lines:
        if not line.startswith("%token") and not line.startswith("IGNORE") and line.strip():
            error_stack.append(f"Error: El siguiente simbolo: '%' no esta antes de la declaracion del token en la siguiente linea: '{line.strip()}'.")
            break

    # Verificar si hay reglas de producción vacías:
    empty_productions = [non_terminal for non_terminal, rules in productions.items() if not rules or all(not rule.strip() for rule in rules)]
    if empty_productions:
        error_stack.append(f"Error: Las siguientes producciones tienen reglas vacías: {', '.join(empty_productions)}")


    return error_stack

# Lee el contenido del archivo YALP dado y devuelve su contenido como una cadena.
def read_yalp_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content


# Analiza el archivo YALP dado, devuelve los tokens y producciones, y reporta errores si los hay.
def parse_yalp_file(filename,error_stack):
    content = read_yalp_file(filename)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # Eliminar comentarios
    tokens_section, productions_section,divisionError = split_sections(content)
    tokens = None
    productions = None
    if(divisionError):
        error_stack.extend(divisionError)
    else:
        tokens = process_tokens_section(tokens_section)
        productions = process_productions_section(productions_section)

        error_stack.extend(validate_yalp(tokens_section, productions_section, tokens, productions))

    return tokens, productions,error_stack

# Definimos una clase para el LR0
# Clase para representar un ítem LR(0), que contiene una producción, una posición y un booleano que indica si fue derivado o no.
class LR0:
    def __init__(self, production, position,derived=False):
        self.production = (production[0], tuple(production[1]))
        self.position = position
        self.derived = derived
        

    def __repr__(self):
        return f'{self.production[0]} -> {" ".join(self.production[1][:self.position]) + "•" + " ".join(self.production[1][self.position:])}'

    def __eq__(self, other):
        return self.production == other.production and self.position == other.position

    def __hash__(self):
        return hash((self.production, self.position))


# Calcula el cierre de un conjunto de ítems dado, teniendo en cuenta las producciones.
def closure(items, productions):
    new_items = set(items)

    while True:
        #Utilizo una compresion de conjuntos {} porque son similares a las listas y tuplas pero no permiten elementos duplicados y no garantizaun orden especifico de los elementos
        symbols_to_expand = {item.production[1][item.position] for item in new_items if item.position < len(item.production[1]) and item.production[1][item.position] in productions}

        derived_items = {LR0((non_terminal, production), 0, True) for non_terminal in symbols_to_expand for production in productions[non_terminal]}

        if not (derived_items - new_items):
            break

        new_items |= derived_items

    return new_items


# Calcula el estado siguiente dado un conjunto de ítems, un símbolo y las producciones.
def go_to(items, symbol, productions):
    next_items = set()
    for item in items:
        if item.position < len(item.production[1]) and item.production[1][item.position] == symbol:
            next_items.add(LR0(item.production, item.position + 1))
    return closure(next_items, productions)

# Genera la colección canónica de conjuntos de ítems para un conjunto de producciones.
def canonical_collection(productions):
    # Inicializa el estado inicial con el símbolo de inicio y el cierre de los elementos iniciales
    items = LR0((next(iter(productions)) + '\'', [next(iter(productions))]), 0)
    states = [closure({items}, productions)]
    stack = [states[0]]
    transitions = []

    while stack:
        state = stack.pop()
        # Obtiene todos los símbolos que aparecen después de las posiciones en los ítems del estado
        symbols = set(sym for item in state for sym in item.production[1][item.position:item.position + 1])

        for symbol in symbols:
            next_state = go_to(state, symbol, productions)
            if not next_state:
                continue
            if next_state not in states:
                states.append(next_state)
                stack.append(next_state)
            transitions.append((states.index(state), symbol, states.index(next_state)))

    # Agrega transiciones de aceptación
    accept_state = len(states)
    for i, state in enumerate(states):
        for item in state:
            if item.production[0] == next(iter(productions)) + '\'' and item.position == len(item.production[1]) and item.derived == False:
                transitions.append((i, '$', accept_state))
                break
    states.append(set())

    return states, transitions
