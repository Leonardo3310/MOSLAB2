from pyomo.environ import *

# Modelo
Model = ConcreteModel()

# Conjuntos
locations = ['L1', 'L2', 'L3', 'L4','L5', 'L6','L7','L8', 'L9', 'L10', 'L11', 'L12']  # Reemplaza con tus datos
sensores = ['S1', #Enviromental sensor
           'S2', #Traffic sensor
           'S3'  #Public safety sensor
           ]  

Model.L = Set(initialize=locations)
Model.S = Set(initialize=sensores)

# Parámetros
instalation_cost = {'L1': 250, 'L2': 100, 'L3': 200, 'L4': 250, 'L5': 300, 'L6': 120, 'L7': 170, 'L8': 150, 'L9': 270, 'L10': 130, 'L11': 100, 'L12': 230} 
energy_consumption = {'S1': 7, 'S2': 4, 'S3': 8}      
communication_cost = {('L1','S1'): 48, ('L2','S1'): 38, ('L3','S1'): 24, ('L4','S1'): 17, ('L5','S1'): 30, ('L6','S1'): 48, ('L7','S1'): 28, ('L8','S1'): 32, ('L9','S1'): 20, ('L10','S1'): 20, ('L11','S1'): 33, ('L12','S1'): 45, 
                      ('L1','S2'): 49, ('L2','S2'): 33, ('L3','S2'): 47, ('L4','S2'): 31, ('L5','S2'): 11, ('L6','S2'):33, ('L7','S2'): 39,('L8','S2'): 47, ('L9','S2'): 11, ('L10','S2'): 30, ('L11','S2'): 42, ('L12','S2'): 21,
                      ('L1','S3'): 31, ('L2','S3'): 34, ('L3','S3'): 36, ('L4','S3'):37, ('L5','S3'): 25, ('L6','S3'): 24, ('L7','S3'): 12, ('L8','S3'): 46, ('L9','S3'): 16, ('L10','S3'):30,('L11','S3'): 18, ('L12','S3'): 48}  

# Cobertura del sensor en las ubicaciones
sensor_coverage = {
    ('S1', 'L1'): 1, ('S1', 'L2'): 1, 
    ('S1', 'L3'): 1, ('S1', 'L4'): 1,
    ('S1', 'L5'): 1, ('S1', 'L6'): 1,
    ('S1', 'L7'): 1, ('S1', 'L8'): 1,
    ('S1', 'L9'): 1, ('S1', 'L10'): 1,
    ('S1', 'L11'): 1, ('S1', 'L12'): 1,
    ('S2', 'L1'): 0, ('S2', 'L2'): 0, ('S2', 'L3'): 0,
    ('S2', 'L4'): 1, ('S2', 'L5'): 1,
    ('S2', 'L6'): 1, ('S2', 'L8'): 1, ('S2', 'L7'): 0,
    ('S2', 'L9'): 1, ('S2', 'L10'): 1,
    ('S2', 'L11'): 1, ('S2', 'L12'): 0,
    ('S3', 'L1'): 1, ('S3', 'L2'): 1, 
    ('S3', 'L3'): 1, ('S3', 'L4'): 0,
    ('S3', 'L5'): 1, ('S3', 'L6'): 1,
    ('S3', 'L7'): 1, ('S3', 'L8'): 1,
    ('S3', 'L9'): 1, ('S3', 'L10'): 0,
    ('S3', 'L11'): 1,('S3', 'L12'): 1
    
}

# Adyacencias: Define si una ubicación es adyacente a otra (1 si lo es, 0 si no)
adyacencias = {
    ('L1', 'L2'): 1, ('L1', 'L3'): 1, ('L1', 'L5'): 1, ('L2', 'L1'): 1, ('L2', 'L5'): 1,
    ('L3', 'L1'): 1, ('L3', 'L4'): 1, ('L3', 'L5'): 1, ('L3', 'L6'): 1, ('L3', 'L7'): 1, ('L3', 'L8'): 1,
    ('L4', 'L3'): 1, ('L4', 'L6'): 1, ('L4', 'L11'): 1, ('L4', 'L5'): 1,
    ('L5', 'L1'): 1, ('L5', 'L2'): 1, ('L5', 'L3'): 1, ('L5', 'L4'): 1, ('L5', 'L11'): 1, ('L5', 'L10'): 1,
    ('L6', 'L3'): 1, ('L6', 'L4'): 1, ('L6', 'L8'): 1, ('L6', 'L11'): 1,
    ('L7', 'L3'): 1, ('L7', 'L8'): 1, ('L7', 'L12'): 1,
    ('L8', 'L3'): 1, ('L8', 'L6'): 1, ('L8', 'L7'): 1, ('L8', 'L12'): 1,('L8', 'L9'): 1,('L8', 'L11'): 1,
    ('L9', 'L8'): 1, ('L9', 'L11'): 1, ('L9', 'L12'): 1,('L9', 'L10'): 1,
    ('L10', 'L5'): 1, ('L10', 'L9'): 1, ('L10', 'L11'): 1,
    ('L11', 'L4'): 1, ('L11', 'L5'): 1, ('L11', 'L6'): 1, ('L11', 'L8'): 1, ('L11', 'L9'): 1, ('L11', 'L10'): 1,
    ('L12', 'L7'): 1, ('L12', 'L8'): 1, ('L12', 'L9'): 1
}

# Variables de decisión
Model.x = Var(Model.S, Model.L, domain=Binary)

# Función objetivo: Minimizar el costo total (instalación, energía, comunicación)
def funcion_obj(Model):
    return sum(instalation_cost[l] * Model.x[s, l] for s in Model.S for l in Model.L) + sum((energy_consumption[s] + communication_cost.get((s,l),0)) * Model.x[s, l] for s in Model.S for l in Model.L)

Model.obj = Objective(rule=funcion_obj, sense=minimize)

# Restricción: Cada ubicación debe estar cubierta por al menos un sensor o un sensor en una ubicación adyacente
def regla_covertura(Model, l):
    # Si un sensor cubre la ubicación o una adyacente
    return sum(Model.x[s, l] * sensor_coverage.get((s, l), 0) for s in Model.S) + sum(Model.x[s, l_adj] * adyacencias.get((l_adj, l), 0) for s in Model.S for l_adj in Model.L) >= 1

Model.coverage_constraint = Constraint(Model.L, rule=regla_covertura)

# Resolver el Modelo
solver = SolverFactory('glpk')
solver.solve(Model)
Model.display()

# Resultados
print("Resultados:")
for s in Model.S:
    for l in Model.L:
        if value(Model.x[s, l]) > 0.5:  # Si el sensor está instalado
            print(f'Sensor {s} se instala en ubicación {l}')
