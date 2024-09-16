from pyomo.environ import *


Model = ConcreteModel()
Model.dual = Suffix(direction=Suffix.IMPORT) 


Model.O = Set(initialize=['Bogota', 'Medellin'])
Model.D = Set(initialize=['Cali', 'Barranquilla', 'Pasto', 'Tunja', 'Chia', 'Manizales'])


costos = {
    ('Bogota', 'Barranquilla'): 2.5, ('Bogota', 'Pasto'): 1.6, ('Bogota', 'Tunja'): 1.4, 
    ('Bogota', 'Chia'): 0.8, ('Bogota', 'Manizales'): 1.4, 
    ('Medellin', 'Cali'): 2.5, ('Medellin', 'Pasto'): 2.0, ('Medellin', 'Tunja'): 1.0, 
    ('Medellin', 'Chia'): 1.0, ('Medellin', 'Manizales'): 0.8
}
destinos = {'Cali': 125, 'Barranquilla': 175, 'Pasto': 225, 'Tunja': 250, 'Chia': 225, 'Manizales': 200}
origen = {'Bogota': 550, 'Medellin': 700}

Model.cost = Param(Model.O, Model.D, initialize=costos, default=1000)  # Large default for undefined routes
Model.demand = Param(Model.D, initialize=destinos)
Model.supply = Param(Model.O, initialize=origen)

# Decision Variables
Model.x = Var(Model.O, Model.D, domain=NonNegativeReals)


def funcionObjetivo(Model):
    return sum(Model.cost[o, d] * Model.x[o, d] for o in Model.O for d in Model.D)
Model.obj = Objective(rule=funcionObjetivo, sense=minimize)

#restricciones
def restriccionSuministro(Model, o):
    return sum(Model.x[o, d] for d in Model.D) <= Model.supply[o]
Model.supply_con = Constraint(Model.O, rule=restriccionSuministro)

def restriccionDemanda(Model, d):
    return sum(Model.x[o, d] for o in Model.O) == Model.demand[d]
Model.demand_con = Constraint(Model.D, rule=restriccionDemanda)


solver = SolverFactory('glpk')
solver.solve(Model)


Model.display()

for o in Model.O:
    for d in Model.D:
        print(f'Toneladas de {o} a {d}: {Model.x[o, d].value}')



print("\nDual Values (Shadow Prices):")
for c in Model.component_objects(Constraint, active=True):
    print(f"Duals for constraint: {c}")
    c_object = getattr(Model, c.name)
    for index in c_object:
        if c_object[index].active:
            print(f"  {c.name}[{index}]: Dual Value = {Model.dual[c_object[index]]}")