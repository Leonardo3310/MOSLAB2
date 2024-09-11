from pyomo.environ import *
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Crear el Modelo
Model = ConcreteModel()

# Cargar la matriz de distancias desde el archivo .csv
file_path = 'data/proof_case.csv'

# Cargar la matriz de distancias
def cargar_matriz(file_path):
    matriz = pd.read_csv(file_path, header=0)
    return matriz.values

matriz_distancias = cargar_matriz(file_path)

# Número de localidades (dimensión de la matriz)
num_localidades = len(matriz_distancias)

# Número de equipos de trabajo
num_equipos = 1

lo=5 #localidad de origen

# Conjunto de equipos y localidades
Model.equipos = RangeSet(1, num_equipos)
Model.localidades = RangeSet(1, num_localidades)

# Parámetros: matriz de costos o distancias
Model.distancias = Param(Model.localidades, Model.localidades,
                         initialize=lambda Model, i, j: matriz_distancias[i-1][j-1])

# Variables de decisión
Model.x = Var(Model.equipos, Model.localidades, Model.localidades, domain=Binary)

# Función objetivo: Minimizar la distancia total recorrida por todos los equipos
def funcion_objetivo(Model):
    return sum(Model.distancias[i, j] * Model.x[e, i, j] for e in Model.equipos for i in Model.localidades for j in Model.localidades)

Model.obj = Objective(rule=funcion_objetivo, sense=minimize)

# Restricción: Flujo de entrada y salida debe ser igual
# def restriccion_flujo(Model, i, e):
#     return sum(Model.x[e, j, i] for j in Model.localidades if j != i) == sum(Model.x[e, i, j] for j in Model.localidades if j != i)

# Model.flujo = Constraint(Model.localidades, Model.equipos, rule=restriccion_flujo)



# Restricción: Cada localidad debe ser abandonada una sola vez
# def restriccion_salida(Model, i):
#     return sum(Model.x[e, j, i] for e in Model.equipos for j in Model.localidades if j != i) == 1

# Model.salida = Constraint(Model.localidades, rule=restriccion_salida)


# Lo que entra a una localidad debe salir
def intermediate_rule(Model, i):
    if i !=lo:
        return sum(Model.x[e, i, j] for e in Model.equipos for j in Model.localidades if j != i) - sum(Model.x[e, j, i] for e in Model.equipos for j in Model.localidades if j != i)==0
    else:
        return Constraint.Skip
    
Model.intermediate = Constraint(Model.localidades, rule=intermediate_rule)

# Restricción: Cada localidad debe ser abandonada una sola vez
def source_rule(Model, i):
    if i == lo:
        return sum(Model.x[e, i, j] for e in Model.equipos for j in Model.localidades if j != i) == 1
    else:
        return Constraint.Skip
Model.source = Constraint(Model.localidades, rule=source_rule)





# Restricción: Cada equipo debe comenzar en la localidad de origen 


def restriccion_inicio(Model, e):
    return sum(Model.x[e, lo, j] for j in Model.localidades if j != 1) == 1

Model.inicio = Constraint(Model.equipos, rule=restriccion_inicio)

# Restricción: Cada equipo debe regresar a la localidad de origen (localidad 1)
def restriccion_final(Model, e):
    return sum(Model.x[e, i, lo] for i in Model.localidades if i != 1) == 1

Model.final = Constraint(Model.equipos, rule=restriccion_final)

# Restricción de subtours usando el método MTZ
Model.u = Var(Model.equipos, Model.localidades, bounds=(1, num_localidades-1), domain=NonNegativeIntegers)

def restriccion_subtour(Model, e, i, j):
    if i != j:
        return Model.u[e, i] - Model.u[e, j] + (num_localidades - 1) * Model.x[e, i, j] <= num_localidades - 2
    else:
        return Constraint.Skip

Model.subtour = Constraint(Model.equipos, Model.localidades, Model.localidades, rule=restriccion_subtour)

# Función para visualizar las rutas
def visualizar_rutas(Model):
    # Crear un grafo dirigido
    G = nx.DiGraph()

    # Agregar nodos (localidades)
    localidades = [i for i in Model.localidades]
    G.add_nodes_from(localidades)

    # Agregar arcos (movimientos entre localidades)
    for e in Model.equipos:
        for i in Model.localidades:
            for j in Model.localidades:
                # Verificar si la variable ha sido inicializada y tiene un valor
                if Model.x[e, i, j].value is not None and Model.x[e, i, j].value == 1:
                    # Si la variable de decisión x[e, i, j] es 1, añadir la ruta
                    G.add_edge(i, j, label=f'E {e}')

    # Posiciones de los nodos (opcional, puedes mejorarlo para una representación clara)
    pos = nx.spring_layout(G)  # Disposición automática

    # Dibujar los nodos
    nx.draw(G, pos, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_weight="bold")

    # Dibujar los arcos con etiquetas de equipo
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20)

    # Mostrar el gráfico
    plt.title("Rutas óptimas de los equipos de inspección")
    plt.show()

# Resolver el Modelo
solver = SolverFactory('glpk')
results = solver.solve(Model, tee=True)

# Verificar si la solución es óptima
if (results.solver.status != SolverStatus.ok) or (results.solver.termination_condition != TerminationCondition.optimal):
    raise ValueError("El solucionador no encontró una solución óptima")

# Mostrar los resultados
Model.display()

# Visualizar las rutas óptimas
visualizar_rutas(Model)
