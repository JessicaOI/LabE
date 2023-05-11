import re


def validate_parentheses(value):
    count = 0
    for char in value:
        if char == '(':
            count += 1
        elif char == ')':
            count -= 1
        if count < 0:
            return False
    return count == 0

def validate_single_quotes(value):
    return value.count("'") % 2 == 0

def get_used_variables(input_text):
    rule_tokens_section = input_text.split("rule tokens =")[1]
    used_variables = re.findall(r'\b\w+\b', rule_tokens_section)
    return set(used_variables)

def reescribir_archivo(input_text):
    lines = input_text.split("\n")
    variables = {}
    errors = []
    used_variables = get_used_variables(input_text)

    for line in lines:
        if not line.startswith("let"):
            continue
        
        var_name, value = line[4:].split(" = ")
        
        if not validate_single_quotes(value):
            errors.append(f"Error en la línea: {line}. Los valores deben estar entre comillas simples.")
            continue
        
        value = value.strip("'")
        
        if not validate_parentheses(value):
            errors.append(f"Error en la línea: {line}. Los paréntesis no están balanceados.")
            continue
        
        variables[var_name] = value

    if errors:
        for error in errors:
            print(error)
        return None

    for var_name, value in variables.items():
        for dependent_var in variables:
            variables[dependent_var] = variables[dependent_var].replace(var_name, f"({value})")

    output_lines = []
    for var_name, value in variables.items():
        if var_name in used_variables:
            output_lines.append(f"let {var_name} = '{value}'")

    return "\n".join(output_lines)

def get_values_list(rewritten_text):
    lines = rewritten_text.split("\n")
    values_list = []

    for line in lines:
        if line.startswith("let"):
            _, value = line.split(" = ")
            value = value.strip("'")
            values_list.append(value)

    return values_list

def find_identifier_from_transitions(enfa, categories):
    for from_state, to_dict in enfa._transition_function._transitions.items():
        for symbol, to_states in to_dict.items():
            for to_state in to_states:
                if to_state in enfa.final_states:
                    for key, value in categories.items():
                        if symbol in key:
                            return value
    return "Desconocido"

def get_variable_names(rewritten_text):
    lines = rewritten_text.split("\n")
    variable_names = []

    for line in lines:
        if line.startswith("let"):
            var_name, _ = line[4:].split(" = ")
            variable_names.append(var_name.strip())

    return variable_names

