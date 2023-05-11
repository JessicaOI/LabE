from pyformlang.regular_expression import Regex
from graphviz import Digraph

def regex_to_enfa(regex_str):
    regex = Regex(regex_str)
    return regex.to_epsilon_nfa()

def enfa_to_graphviz(enfa, identifier=None):
    graph = Digraph("ENFA", format="png")

    # Creación de los estados del AFN
    graph.attr("node", shape="circle")
    for state in enfa.states:
        graph.node(str(state))

    # Creación del estado inicial
    graph.attr("node", shape="circle", style="filled", fillcolor="lightblue")
    graph.node(str(enfa._start_state))

    # Creación de los estados finales
    graph.attr("node", shape="doublecircle")
    for final_state in enfa.final_states:
        if identifier is not None:
            label = f"{final_state} ({identifier})"
        else:
            label = str(final_state)
        graph.node(str(final_state), label=label)

    # Creación de las transiciones
    for from_state, to_dict in enfa._transition_function._transitions.items():
        for symbol, to_states in to_dict.items():
            for to_state in to_states:
                graph.edge(str(from_state), str(to_state), label=str(symbol))

    return graph


def generate_mega_enfa_graph(enfas, identifiers=None):
    mega_graph = Digraph("Combined_ENFA", format="png")
    mega_start_state = "MegaStart"

    # Creación del mega estado inicial
    mega_graph.attr("node", shape="circle", style="filled", fillcolor="lightblue")
    mega_graph.node(str(mega_start_state))

    current_max_state = 0

    for idx, enfa in enumerate(enfas):
        current_max_state += 1
        offset = current_max_state

        # Mapeo de estados antiguos a nuevos
        state_mapping = {}

        # Creación de los estados del AFN
        for state in enfa.states:
            new_state = current_max_state
            state_mapping[state] = new_state
            mega_graph.node(str(new_state))
            current_max_state += 1

        # Creación de las transiciones
        for from_state, to_dict in enfa._transition_function._transitions.items():
            for symbol, to_states in to_dict.items():
                for to_state in to_states:
                    mega_graph.edge(str(state_mapping[from_state]), str(state_mapping[to_state]), label=str(symbol))

        # Creación de los estados finales
        mega_graph.attr("node", shape="doublecircle")
        for final_state in enfa.final_states:
            if identifiers is not None:
                label = f"{state_mapping[final_state]} ({identifiers[idx]})"
            else:
                label = str(state_mapping[final_state])
            mega_graph.node(str(state_mapping[final_state]), label=label)

        # Conectar el mega estado inicial a los estados iniciales de los ENFA individuales
        for start_state in enfa._start_state:
            mega_graph.edge(str(mega_start_state), str(state_mapping[start_state]), label="ε")

    return mega_graph


# def main():
#     regex_list = [
#         # "0|1|2",
#         # "(0|1|2)((0|1|2))*",
#         # "a|b|c|A|B|C",
#         # "(a|b|c|A|B|C)((a|b|c|A|B|C)|(0|1|2))*"
#         "[0-9]+",
#         "[0-9]*\.[0-9]+"
#     ]

#     enfas = [regex_to_enfa(regex) for regex in regex_list]

#     # Graficar y guardar ENFA individuales
#     for idx, enfa in enumerate(enfas):
#         enfa_graph = enfa_to_graphviz(enfa)
#         enfa_graph.render(f"enfa_output_{idx}", view=True)

#     # Generar y guardar el mega autómata
#     mega_enfa_graph = generate_mega_enfa_graph(enfas)
#     mega_enfa_graph.render("mega_enfa_output", view=True)

# if __name__ == "__main__":
#     main()
