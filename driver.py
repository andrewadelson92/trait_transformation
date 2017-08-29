import pandas as pd
import math
import numpy as np
import transform_trait as tt
import map_trait as mt

df = pd.read_csv("C:\Users\\aadelson\Desktop\loan_docs\\" + 'apr_2017.csv')
def matrixTransformation(df, traits):
    data = df[:]
    #This function transforms a train set and maps a test set to the fitted transformation
    categoricals = []
    train_size = .8
    train =  data[:int(train_size* data.shape[0])]
    test = data[int(train_size* data.shape[0]):]


    dict_traits = {}

    #transforming train applications
    for trait in traits:
        train[trait], dict_traits[trait], categoricals = tt.traitTransform(train, trait, categoricals)

    train = pd.get_dummies(train, columns= categoricals)

    #mapping test applications
    for trait in traits:
        trait_dict = dict_traits[trait]
        test[trait] = mt.traitMap(test, trait, trait_dict)

    test = pd.get_dummies(test, columns = categoricals)
    return train, test


if __name__ == '__ main__':
    cols = [x for x in df.columns if 'SUCI0' in x]
    train,test = matrixTransformation(df, cols)
    print train.head()


