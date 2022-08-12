"""
Created on Mon Apr 11 12:51:13 2022

@author: Fatehie
"""

import copy
import json

# from plotly.offline import download_plotlyjs, init_notebook_mode, plot
import math

import GPyOpt
import numpy as np
import pandas as pd

# %%
run_name = "GpyOpt"  # Names the .json file for the data dump at the end
number_campaigns = 15
campaign_train_ind = {}  # blank dictionary to be updated with results of each train inds

raw_dataset = pd.read_csv(r"MgAl.csv")

feature_name = ["Mg", "Al"]
objective_name = "energy"

X_feature = raw_dataset[feature_name].values
y = raw_dataset[objective_name].values

for campaign_number in range(1, number_campaigns + 1):
    campaign_train_ind[
        f"campaign {campaign_number}"
    ] = {}  # Create the initial dictionary to track train_inds per campaign

    # print(X_feature.shape)

    total_indexes = np.array([i for i in range(len(X_feature))])
    # # total number of data in set
    N = 29
    true_max_y = np.max(y)
    true_max_x = X_feature[np.argmax(y)]
    true_min_y = np.min(y)
    true_min_x = X_feature[np.argmin(y)]
    nb_test = 20

    best_ = np.argsort(y, axis=None)
    print(best_)
    best_15 = np.argsort(y, axis=None)[:5]
    best_5 = np.argsort(y, axis=None)[:10]

    best_15_lim = y[best_15[-1]]
    best_5_lim = y[best_5[-1]]
    best_lim = y[best_[-1]]
    xxx = np.zeros(X_feature.shape)
    xxx = X_feature
    number_of_rows = X_feature.shape[0]
    # number of ensembles
    n_ensemble = 20
    best_15_count = np.zeros(n_ensemble)
    best_5_count = np.zeros(n_ensemble)
    best_count = np.zeros(n_ensemble)
    # %% initialization

    # number of initial experiments
    n_initial = 1
    # number of top candidates, currently using top 5% of total dataset size
    n_top = int(math.ceil(len(y) * 0.05))
    # the top candidates and their indicies
    top_indices = list(raw_dataset.sort_values(objective_name).head(n_top).index)

    #
    indices = list(np.arange(N))
    random_indices = np.random.choice(number_of_rows, size=n_initial, replace=False)
    train_inds = random_indices  # initial train set indexes
    test_inds = [i for i in total_indexes if i not in train_inds]
    #
    # # index_learn = indices.copy() # test_inidices
    # # index_observed = random.sample(index_learn, n_initial) # train_indices
    X_observed = []
    y_observed = []
    can_top = 0
    #     list of cumulative number of top candidates found at each learning cycle
    TopCount_list = []
    #     add the first n_initial experiments to collection
    for i in train_inds:
        X_observed.append(X_feature[i])
        y_observed.append(y[i])
        X_init = np.array(X_observed)
        Y_init = np.array(y_observed)
        if i in top_indices:
            can_top += 1
        if y[i] > best_lim:
            best_count[0] += 1

        TopCount_list.append(can_top)

    test_inds = [i for i in total_indexes if i not in train_inds]

    next_index = 0

    # %%
    n_points = 1
    lengthscale = 0.5  # GPy option: lengthscale for kernel
    noise_var = 1  # GPy option
    parameter_space = [{"name": "var_1", "type": "bandit", "domain": xxx}]
    constraints = []
    # parameter_space = [ {'name': 'Mn', 'type': 'discrete', 'domain': (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0)},
    #                    {'name': 'Fe', 'type': 'discrete', 'domain': (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0)},
    #                    {'name': 'Co', 'type': 'discrete', 'domain': (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0)},
    #                    {'name': 'Ni', 'type': 'discrete', 'domain': (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0)},
    #                    {'name': 'La', 'type': 'discrete', 'domain': (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0)},
    #                    {'name': 'Ce', 'type': 'discrete', 'domain': (0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0)}]

    # constraints = [{'name': 'constr_1', 'constraint': 'x[:,0]+x[:,1]+x[:,2]+x[:,3]+x[:,4]+x[:,5]-1'},
    #               {'name': 'constr_2', 'constraint': '-x[:,0]-x[:,1]-x[:,2]-x[:,3]-x[:,4]-x[:,5]+1'}]
    Y_init = Y_init[:, None]
    for i in range(n_ensemble):
        print(f"Number of optimization run: {i}")
        parameter_space = [{"name": "var_1", "type": "bandit", "domain": xxx}]
        BO = GPyOpt.methods.BayesianOptimization(
            f=None,
            domain=parameter_space,
            constraints=constraints,
            model_type="GP",
            X=X_init,
            Y=Y_init,
            acquisition_type="EI",
            normalize_Y=False,
            batch_size=1,
            maximize=True,
        )
        x_next = BO.suggest_next_locations()
        next_index = np.where(np.all(X_feature == x_next, axis=1))
        print(f"New candidate: {np.array(x_next)}")
        print(f"New candidate: {np.array(next_index)}")
        # Modular bayesian optimization
        # inpar = [ X_init, ]
        # loss = [ Y_init, ]
        # noise =[ [0.1, ] ]
        # feasible_region = GPyOpt.Design_space(space = parameter_space, constraints = constraints)
        # objective = GPyOpt.core.task.objective.Objective()
        # acq_opt = AcquisitionOptimizer(feasible_region)
        # kernel = kern.RBF(input_dim = 6, lengthscale=lengthscale)
        # model = GPRegression(inpar, loss, kernel, noise_var=noise_var)
        # model.optimize('bfgs', max_iters=100)
        # opt_model = GPModel(optimize_restarts=1, verbose=False)
        # opt_model.model = model
        # acquisition = AcquisitionLCB(opt_model, feasible_region, acq_opt, exploration_weight=0)
        # evaluator = evaluators.Sequential(acquisition)
        # bo = ModularBayesianOptimization(opt_model, feasible_region, objective, acquisition, evaluator,
        #                                 X_in = model.X,
        #                                 Y_in = model.Y,
        #                                 normalize_Y = False,
        #                                 de_duplication = True
        #                                 )
        # x_next=bo.suggest_next_locations()
        # next_index=np.where(np.all(X_feature==x_next,axis=1))

        if next_index in train_inds:
            w = 1
        else:
            w = 0
        if w == 1:
            print("Show Must Go On)")
            index = np.random.choice(test_inds)
            train_inds = np.append(train_inds, index)
            test_inds = [k for k in total_indexes if k not in train_inds]
            # test_inds = np.delete(test_inds, index)
            # xxx = X_feature[test_inds,:]
            X_init = X_feature[train_inds, :]
            Y_init = y[train_inds]
            Y_init = Y_init[:, None]
            X_observed.append(X_feature[index])
            y_observed.append(y[index])

        else:
            print(f"New candidates composition to be added to trainset: {X_feature[next_index]}")
            print(f"new data from whole dataset added to trainset: {y[next_index]}")
            # adding the new data point to tran set for the next round
            train_inds = np.append(train_inds, next_index)
            test_inds = [k for k in total_indexes if k not in train_inds]
            # xxx = X_feature[test_inds,:]
            X_init = X_feature[train_inds, :]
            Y_init = y[train_inds]
            Y_init = Y_init[:, None]
            X_observed.append(X_feature[next_index])
            y_observed.append(y[next_index])
            # xxx = np.delete(xxx, index, 0)
        print(f"Best point is this: {np.max(Y_init)}")

        if y[next_index] > best_lim:
            best_count[i] = best_count[i - 1] + 1
        else:
            best_count[i] = best_count[i - 1]

        if y[next_index] > best_15_lim:
            best_15_count[i] = best_15_count[i - 1] + 1
        else:
            best_15_count[i] = best_15_count[i - 1]

        if y[next_index] > best_5_lim:
            best_5_count[i] = best_5_count[i - 1] + 1
        else:
            best_5_count[i] = best_5_count[i - 1]

        if next_index in top_indices:
            can_top += 1

        # train_inds = np.append(train_inds, next_index)
        # test_inds = [k for k in total_indexes if not k in train_inds]
        # X_init =X_feature[ train_inds, :]
        # Y_init =y[ train_inds]
        # Y_init = Y_init[:, None]

        # X_observed.append(X_feature[next_index])
        # y_observed.append(y[next_index])

    campaign_train_ind[f"campaign {campaign_number}"]["index_observed"] = (train_inds).tolist()
    campaign_train_ind[f"campaign {campaign_number}"]["best_5_count"] = (best_15_count).tolist()
    campaign_train_ind[f"campaign {campaign_number}"]["best_10_count"] = (best_5_count).tolist()
    campaign_train_ind[f"campaign {campaign_number}"][f"best_{nb_test}_count"] = (best_count).tolist()

with open(f"{run_name}.json", "w") as fp:
    json.dump(campaign_train_ind, fp, indent=4)
