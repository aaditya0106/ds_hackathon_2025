#pip install 'h3==3.7.6'
#pip install shapely
#pip install pyomo
from pyomo.environ import *
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np
import requests
from shapely.geometry import Polygon
import h3
import ast

def get_optimised_model(base_data, min_price,
                        max_price,
                        min_area,
                        max_area,
                        commute_budget,
                        num_beds,
                        num_baths,
                        second_loc_freq,
                        walk_dist,
                        commute_time_limit,
                        commute_type):
    print(".....", max_price)
    x = base_data[(base_data.bedrooms.isin(num_beds)) & (base_data.bathrooms.isin(num_baths))][
        (base_data.livingArea >= min_area) & (base_data.livingArea <= max_area)]

    def get_distance(r):
        home_to_source = r['distance_time_source_vehicle']['distance']
        source_to_second = r['distance_time_second_vehicle']['distance']
        second_to_home = r['distance_time_source_second_vehicle']['distance']
        if (home_to_source <= walk_dist):
            home_to_source = 0
        tot_cost = (((second_loc_freq * (home_to_source + source_to_second + second_to_home) + (5 - second_loc_freq) * (
                    2 * second_to_home)) * 4 * 4.167) / 24.4)
        if (home_to_source <= walk_dist):
            return tot_cost + second_loc_freq * 4 * 10
        return tot_cost + 10

    x['total_commute_cost_tranist'] = (((x['total_commute_cost_tranist'] / 22) * second_loc_freq * (1.5) + x[
        'total_commute_cost_tranist'] / 22) * (5 - second_loc_freq)) * 22
    x = x[x['price']>=min_price]

    if(len(x)==0):
        return 0
    scaler = MinMaxScaler()

    # Scale the numerical columns
    scaled_data = scaler.fit_transform(x[['price', 'total_commute_cost_vehicle', 'total_commute_cost_tranist']])
    # Convert back to DataFrame
    scaled_df = pd.DataFrame(scaled_data, columns=['price_scaled', 'total_commute_cost_vehicle_scaled',
                                                   'total_commute_cost_tranist_scaled'])

    x.reset_index(drop=True, inplace=True)
    scaled_df.reset_index(drop=True, inplace=True)

    # Join the DataFrames
    x = x.join(scaled_df, how='left')

    apartments = x.to_dict(orient='records')

    # Parameters (weights)
    w1 = 0.4  # Weight for rent
    w2 = 0.25  # Weight for commute cost
    w3 = 0.15  # Weight for safety score
    w4 = 0.2  # Weight for neighborhood score

    def run_model():

        # Initialize model
        model = ConcreteModel()

        # Sets
        model.Apartments = Set(initialize=[str(a["apartment_id"]) for a in apartments])

        # Parameters
        rent = {a["apartment_id"]: a["price_scaled"] for a in apartments}
        area = {a["apartment_id"]: a["livingArea"] for a in apartments}
        beds = {a["apartment_id"]: a["bedrooms"] for a in apartments}
        baths = {a["apartment_id"]: a["bathrooms"] for a in apartments}
        if (commute_type == 'vehicle'):
            commute_cost = {a["apartment_id"]: a["total_commute_cost_vehicle_scaled"] for a in apartments}
        else:
            commute_cost = {a["apartment_id"]: a["total_commute_cost_tranist_scaled"] for a in apartments}

        if (commute_type == 'vehicle'):
            commute_time = {a["apartment_id"]: ast.literal_eval(a["distance_time_source_vehicle"])['duration'] for a in
                            apartments}
        else:
            commute_time = {a["apartment_id"]: ast.literal_eval(a["distance_time_source_transit"])['duration'] for a in
                            apartments}
        safety_score = {a["apartment_id"]: a["safety_score"] for a in apartments}
        neighborhood_score = {a["apartment_id"]: a["neighbourhood_score"] for a in apartments}
        # return apartments

        # Decision Variables
        model.x = Var(model.Apartments, domain=Binary, initialize=0)  # 1 if apartment is selected, 0 otherwise

        # Objective Function
        def objective_rule(model):
            return sum(
                model.x[i] * (w1 * rent[i] + w2 * commute_cost[i] - w3 * safety_score[i] - w4 * neighborhood_score[i])
                for i in model.Apartments
            )

        model.Objective = Objective(rule=objective_rule, sense=minimize)

        # Constraints
        # Only one apartment can be selected
        def one_apartment_constraint(model):
            return sum(model.x[i] for i in model.Apartments) == 1

        model.OneApartment = Constraint(rule=one_apartment_constraint)

        # Commute time constraint
        def commute_time_constraint(model):
            return sum(model.x[i] * commute_time[i] for i in model.Apartments) <= commute_time_limit

        model.CommuteTime = Constraint(rule=commute_time_constraint)

        # Total commute cost constraint
        def commute_cost_constraint(model):
            return sum(model.x[i] * commute_cost[i] for i in model.Apartments) <= commute_budget

        model.CommuteCost = Constraint(rule=commute_cost_constraint)

        # Rent constraint
        def rent_constraint(model):
            return sum(model.x[i] * rent[i] for i in model.Apartments) <= max_price

        def rent_constraint_min(model):
            return sum(model.x[i] * rent[i] for i in model.Apartments) >= min_price

        model.Rent = Constraint(rule=rent_constraint)
        # model.Rent_min = Constraint(rule=rent_constraint_min)

        # Solve the model
        solver = SolverFactory('cbc')  # Use 'glpk', 'cbc', or another solver available
        result = solver.solve(model)

        # Display results
        if result.solver.termination_condition != TerminationCondition.optimal:
            print("Solver failed to find an optimal solution.")
        elif result.solver.termination_condition == TerminationCondition.optimal:
            # print("Optimal Solution Found!")
            for i in model.Apartments:
                if model.x[i]() == 1:
                    apt_id = i
                    # print(f"Selected Apartment ID: {i}")
                    # print(f"Rent: {rent[i]}, Commute Cost: {commute_cost[i]}, Commute Time: {commute_time[i]}")
                    # print(f"Safety Score: {safety_score[i]}, Neighborhood Score: {neighborhood_score[i]}")
            del model
            return base_data[base_data['apartment_id'] == apt_id].iloc[0].to_dict()
        else:
            # print("No Optimal Solution Found!")
            del model
            return -1

    apartment_list = list()
    for i in range(5):
        # print(i)
        try:
            a = run_model()
            if (a == -1 and len(apartment_list) == 0):
                return -1
            if (a == -1):
                return apartment_list
            apartment_list.append(a)
            apartments = [apt for apt in apartments if apt['apartment_id'] != a['apartment_id']]
        except:
            return 0
    return apartment_list
