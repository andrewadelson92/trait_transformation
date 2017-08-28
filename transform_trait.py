import pandas as pd
import math
import numpy as np

def informationValue(data, dictionary):
    iv = 0
    for bucket in dictionary['counts']:
        iv += ((float(dictionary['counts'][bucket][0]) / (data['Approved'] == 1).sum()) - (
            float(dictionary['counts'][bucket][1]) /(data['Approved'] == 0).sum())) * dictionary['woe'][bucket]
    return iv



def traitTransform(df, trait, categoricals):
    # This function will return the binned trait for the training set and also save dictionaries, to look up
    #woes and bins for the test set

    #call train set data
    data = df[:]

    #this will be a dictionary of all the qualities necessary qualities defining a trait
    #example qualities are "kind" (categorical or WE) and  "WE" which describes what to transform the values to
    attr_dict = {}


    vals = data[trait]
    # percentage of values that are not null and not 0
    percent = float(len(data[trait].dropna()[vals.dropna() != 0])) / data.shape[0]
    #this will be the series of values that I build, associated with each application.
    new_series = []
    # cap number of buckets at 15.
    if percent > .45:
        num_buckets = 15
    else:
        ##eg. 5% nonnull, nonzero, can only contain one valid bucket
        num_buckets = int(percent / .03)
    #if num_buckets is 0 or 1, this will necessarily be a categorical variable
    if num_buckets in [0,1]:
        categoricals.append(trait)
        if num_buckets ==0:
            attr_dict['kind'] = 'less_categorical'
            # make three buckets- zero, null, and numeric - this will be categoric
            for val in vals:

                try:
                    int(val)
                    if val == 0:
                        new_series.append(-5)
                    else:
                        new_series.append(5)
                except:
                    new_series.append(-9700)
            categoricals.append(trait)
            return new_series, attr_dict, categoricals

        else:
            median = vals.dropna()[vals.dropna() != 0].median()
            attr_dict['kind'] = 'more_categorical'
            attr_dict['median'] = median
            for i, val in enumerate(vals):
                try:
                    int(val)
                    if val == 0:
                        new_series.append(-5)

                    elif val <= median:
                        new_series.append(4)
                    else:
                        new_series.append(20)
                except:
                    new_series.append(-9700)

        return new_series, attr_dict, categoricals

    else:
        #array of the percentiles of the data. E.G. if 4 buckets qualify, buckets are [0th percentile, 25th percentile, 50th percentile, 75th percentile]
        ptiles = [vals.dropna()[vals.dropna() != 0].quantile(x) for x in np.linspace(0, 1 - ((float(1)) / num_buckets), num_buckets)]

        attr_dict['counts'] = {}
        attr_dict['ind_min'] = {}
        for i, val in enumerate(vals):
            #we need to look at result of the application
            result = data['Approved'].iloc[i]
            try:
                int(val)
                if val == 0:
                    new_series.append(-5)

                else:
                    k = num_buckets - 1
                    while val < ptiles[k]:
                        k -= 1
                    new_series.append(k)
            except:
                new_series.append(-9700)
            #check to see if appended value is already in series
            if new_series[-1] in attr_dict['counts']:
                #if it is, increment the appropriate value (good or bad)
                if result == 1:
                    attr_dict['counts'][new_series[-1]][0] += 1
                else:
                    attr_dict['counts'][new_series[-1]][1] += 1
            else:
                #if not, initiate a two piece array that saves goods and bads
                if result == 1:
                    attr_dict['counts'][new_series[-1]] = [1, 0]
                else:
                    attr_dict['counts'][new_series[-1]] = [0, 1]
        array = []

        for key, value in attr_dict['counts'].iteritems():
            temp = [key, value]
            array.append(temp)
        #this saves an array of the appropriate bin name and the value of goods and bads in it
        array.sort(reverse=True)

        for i, bin in enumerate(array):
            # if there are no goods (or no bads) in a bucket, we need to change it
            if bin[1][0] == 0 or bin[1][1] == 0:
                #If so, put things in "new bin."  try to put in left bin if we can. if not, put in right bin
                try:
                    new_bin = array[i+1]
                    new_bin[1][0] += bin[1][0]
                    new_bin[1][1] += bin[1][1]
                except:
                    new_bin = array[i - 1]
                    new_bin[1][0] += bin[1][0]
                    new_bin[1][1] += bin[1][1]
                # have to fix this
                new_series.replace(bin[0], new_bin[0], inplace=True)
                attr_dict['counts'][new_bin[0]] +=   attr_dict['counts'][bin[0]]
                attr_dict['counts'][new_bin[0]] += attr_dict['counts'][bin[0]]
                #get rid of this value from the dictionary
                attr_dict['counts'].pop(bin[0])
            else:
                pass
        attr_dict['counts'] = {}

        for index in attr_dict['counts']:
            if index in [-9700, -5]:
                # if 0, or null, don't worry about the percentiles
                pass
            else:
                attr_dict['ind_min'][index] = ptiles[index]
        if len(attr_dict['counts']) < 4:
            attr_dict['kind'] = 'ptile_categorical'
            categoricals.append(trait)
            return new_series, attr_dict, categoricals
        else:
            attr_dict['kind'] = 'ptile_woe'
            attr_dict['woe'] = {}
            for index in attr_dict['counts']:
                good = float(attr_dict['counts'][index][0]) / (data['Approved'] == 1).sum()

                bad = float(attr_dict['counts'][index][1]) / (data['Approved'] == 0).sum()
                woe = math.log(good / bad)
                attr_dict['woe'][index] = woe
            attr_dict['iv'] = informationValue(attr_dict)
            new_series = new_series.map(attr_dict['woe'])
            return new_series, attr_dict, categoricals


        return new_series, attr_dict, categoricals
