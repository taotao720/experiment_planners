#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one or more
contributor license agreements. See the NOTICE file distributed with this
work for additional information regarding copyright ownership. The ASF
licenses this file to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

The code in this file was developed at Harvard University (2018) and
modified at ChemOS Inc. (2019) as stated in the NOTICE file.
'''

__author__  = 'Florian Hase'

#=========================================================================

import sys
sys.path.append('../../phoenics')
import pickle

from phoenics import Phoenics
from branin   import branin as loss

#=========================================================================

class OptimizationManager(object):

    def __init__(self, config_file, loss_function):

        # creates instance of Phoenics optimizer
        self.phoenics      = Phoenics(config_file)
        self.loss_function = loss_function


    def optimize(self, observations, removed_obs = [], max_iter = 10):

        for num_iter in range(max_iter):

            # query for new parameters based on prior observations
            params = self.phoenics.recommend(observations = observations)

            # use parameters for evaluation ...
            # ... experimentally or computationally
            for param in params:
                observation = self.loss_function(param)
                observations.append(observation)

                # log observations in a pickle file for future analysis
                observations_log = self.restore_removed_obs(observations.copy(), removed_obs)
                pickle.dump(observations_log, open('observations.pkl', 'wb'))

                # print observations to file
                logfile = open('logfile.dat', 'a')
                new_line = ''
                for param_name in sorted(self.phoenics.config.param_names):
                    for param_value in param[param_name]:
                        new_line += '%.5e\t' % (param[param_name])
                for obj_name in sorted(self.phoenics.config.obj_names):
                    new_line += '%.5e\t' % (param[obj_name])
                logfile.write(new_line + '\n')
                logfile.close()

    def remove_obs(self, observations, removed_obs_indices):

        removed_obs = []
        if len(removed_obs_indices) > 0:
            removed_obs_indices.sort(reverse=True)
            if len(observations) < removed_obs_indices[0]:
                print ('Point of of bound\n') #need to change to a correct error type
            else:
                for index in removed_obs_indices:
                    removed_obs.append([index, observations.pop(index - 1)])
        return observations, removed_obs

    def restore_removed_obs(self, observations, removed_obs):

        removed_obs.sort()
        for [index, val] in removed_obs:
            observations.insert(index - 1, val)
        return observations




#=========================================================================

if __name__ == '__main__':

    logfile = open('logfile.dat', 'a')
    logfile.close()

    manager = OptimizationManager('config.json', loss)

    try:
        obs_file = open('observations.pkl','rb')
        observations = pickle.load(obs_file)
    except:
        observations = []

    removed_obs_indices = []
    observations, removed_obs = manager.remove_obs(observations, removed_obs_indices)
    manager.optimize(observations, removed_obs, 3)
