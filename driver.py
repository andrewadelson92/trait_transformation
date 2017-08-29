import pandas as pd
import math
import numpy as np
import transform_trait as tt
import map_trait as mt

df = pd.read_csv("C:\Users\\aadelson\Desktop\loan_docs\\" + 'apr_2017.csv')

def matrixTransformation(df, traits):
    # create copy of df as to not change the data directly
    data = df[:]
    # randomize the order of the rows of data to perform the train test split
    data = data.sample(frac=1).reset_index(drop=True)
    # This function transforms a train set and maps a test set to the fitted transformation
    categoricals = []
    train_size = .8
    train = data[:int(train_size * data.shape[0])]
    test = data[int(train_size * data.shape[0]):]

    dict_traits = {}

    # transforming train applications
    print 'transform'
    for trait in traits:
        train[trait], dict_traits[trait], categoricals = tt.traitTransform(train, trait, categoricals)

    train = pd.get_dummies(train, columns=categoricals)
    print 'map'
    # mapping test applications
    for trait in traits:
        trait_dict = dict_traits[trait]
        test[trait] = mt.traitMap(test, trait, trait_dict)

    test = pd.get_dummies(test, columns=categoricals)
    ivs = []
    for trait in dict_traits:
        if 'iv' in trait:
            ivs.append([trait, trait['iv']])

    badcols = [x for x in train.columns if x not in test.columns]
    train.drop(badcols, axis=1, inplace=True)
    return train, test, ivs


if __name__ == '__ main__':
    cols = [x for x in df.columns if 'SUCI0' in x]
    train,test = matrixTransformation(df, cols)
    print train.head()


