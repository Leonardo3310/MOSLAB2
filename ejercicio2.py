from pyomo.environ import *
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Cargar la matriz de distancias desde el archivo .csv
def cargar_matriz(file_path):
    matriz = pd.read_csv(file_path, header=0)
    return matriz.values

file_path = 'data/proof_case.csv'
matriz_distancias = cargar_matriz(file_path)
#print(matriz_distancias)

# Modelo
Model = ConcreteModel()

# Número de localidades y equipos
num_localidades = len(matriz_distancias)
num_equipos = 4
lo = 0  # Localidad de origen

# Conjuntos
Model.equipos = RangeSet(1, num_equipos)
Model.localidades = RangeSet(0, num_localidades - 1)

# Parámetro de distancias entre localidades
Model.distancias = Param(Model.localidades, Model.localidades, initialize=lambda Model, i, j: matriz_distancias[i][j])

# Variables de decisión: x[e, i, j] = 1 si el equipo e va de i a j
Model.x = Var(Model.equipos, Model.localidades, Model.localidades, domain=Binary, initialize=0)

# Función Objetivo: Minimizar la distancia total recorrida
def funcion_objetivo(Model):
    return sum(Model.distancias[i, j] * Model.x[e, i, j] for e in Model.equipos for i in Model.localidades for j in Model.localidades)
Model.obj = Objective(rule=funcion_objetivo, sense=minimize)

# Restriccion 1: cada equipo debe salir de la localidad de origen
def restriccion_salida_origen(Model, e):
    return sum(Model.x[e, lo, j] for j in Model.localidades if j != lo) == 1
Model.salida_origen = Constraint(Model.equipos, rule=restriccion_salida_origen)

# Restriccion 2: cada equipo debe regresar a la localidad de origen
def restriccion_regreso_origen(Model, e):
    return sum(Model.x[e, i, lo] for i in Model.localidades if i != lo) == 1
Model.regreso_origen = Constraint(Model.equipos, rule=restriccion_regreso_origen)

#Restricción 3: cada equipo debe visitar al menos dos localidades
def restriccion_visitar_al_menos_dos(Model, e):
    return sum(Model.x[e, i, j] for i in Model.localidades for j in Model.localidades if i != j) >= 2
#Model.visitar_al_menos_dos = Constraint(Model.equipos, rule=restriccion_visitar_al_menos_dos)

# Restricción 4: cada localidad debe ser visitada por un solo equipo
def restriccion_visitar_localidad_una_vez(Model, i):
    if i != lo:
        return sum(Model.x[e, i, j] for e in Model.equipos for j in Model.localidades if j != i) == 1
    else:
        return Constraint.Skip
Model.visitar_localidad_una_vez = Constraint(Model.localidades, rule=restriccion_visitar_localidad_una_vez)

# Restricción 5: todo lo que entra a una localidad debe salir
def restriccion_continuidad(Model, e, i):
    if i != lo:
        return sum(Model.x[e, i, j] for j in Model.localidades if j != i) == sum(Model.x[e, j, i] for j in Model.localidades if j != i)
    else:
        return Constraint.Skip
Model.continuidad = Constraint(Model.equipos, Model.localidades, rule=restriccion_continuidad)

# Resolver el modelo
solver = SolverFactory('glpk')
results = solver.solve(Model)

Model.display()

# Imprimir los resultados
def imprimir_resultados(Model):
    total_modelo=0
    for e in Model.equipos:
        print(f"\nEquipo {e}:")
        total_equipo = 0
        for i in Model.localidades:
            for j in Model.localidades:
                if Model.x[e, i, j].value == 1:  # Si el equipo viaja de i a j
                    print(f"De {i} a {j}: dis {Model.distancias[i, j]}")
                    total_equipo += Model.distancias[i, j]
        total_modelo += total_equipo
        print(f"Distancia total recorrida Equipo {e}: {total_equipo}")
    print(f"\nDISTANCIA TOTAL RECORRIDA: {total_modelo}")


    
# Visualización de rutas
def visualizar_rutas(Model):
    G = nx.DiGraph()
    localidades = [i for i in Model.localidades]
    G.add_nodes_from(localidades)

    for e in Model.equipos:
        for i in Model.localidades:
            for j in Model.localidades:
                if Model.x[e, i, j].value == 1:
                    G.add_edge(i, j, label=f'Equipo {e}')

    pos = nx.shell_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue", font_size=10, font_weight="bold")
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color="black", width=2)
    plt.title("Rutas óptimas de los equipos de trabajo")
    plt.show()
    
# Imprimir resultados y visualizar rutas
imprimir_resultados(Model)
visualizar_rutas(Model)


