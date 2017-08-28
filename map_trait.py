import pandas as pd
import math
import numpy as np


def traitMap(test, trait, trait_dict):
    # this function should take an attribute in a test set, and map each value in the test set to the correct woe or category

    #create copy of test as to not edit it directly
    data = test[:]
    series = data[trait]
    new_series = []

    #if we only have room for 3 categories, then the work is easy
    if trait_dict['kind'] == 'less_categorical':
        for val in series:
            try:
                int(val)
                if val == 0:
                    new_series.append(-5)
                else:
                    new_series.append(5)
            except:
                new_series.append(-9700)
        return new_series
    #if we have room for four categories, then the work is slightly harder
    elif trait_dict['kind'] == 'more_categorical':
        #if it has 1 bucket, we can add another indicator, greater than and less than median
        for val in series:
            try:
                int(val)
                if val == 0:
                    new_series.append(-5)
                elif val <= trait_dict['median']:
                    new_series.append(4)
                else:
                    new_series.append(20)
            except:
                new_series.append(-9700)
        return new_series
    #if the column is categorical, determined from ptiles, then do this function
    elif trait_dict['kind'] == 'ptile_categorical':
        dictlist = []
        for key, value in trait_dict['ind_min'].iteritems():
            temp = [key, value]
            dictlist.append(temp)
        dictlist.sort(lambda x: x[1], reverse=True)
        for val in series:
            try:
                int(val)
                if val == 0:
                    new_series.append(-5)
                else:
                    i = len(dictlist)
                    while val < dictlist[i][1]:
                        i -= 1
                    new_series.append(dictlist[i][0])

            except:
                new_series.append(-9700)
        return new_series
    else:
        #otherwise, it is a weight of evidence transformation
        woe = trait_dict['woe']
        #create a list [[bucket, percentile value], ...]
        dictlist = []
        for key, value in trait_dict['ind_min'].iteritems():
            temp = [key, value]
            dictlist.append(temp)
        dictlist.sort(lambda x: x[1], reverse=True)
        for val in series:
            try:
                int(val)
                if val == 0:
                    new_series.append(woe[-5])
                else:
                    i = len(dictlist) - 1
                    while val < dictlist[i][1]:
                        i -= 1
                    new_series.append(woe[dictlist[i][0]])
            except:
                new_series.append(woe[-9700])
        return new_series




