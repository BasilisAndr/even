import numpy as np
import pandas as pd

def loglike(df, a, b, columns):
    '''
    takes pd.DataFrame
    calculates log-likelihood for given columns based on corpora sizes given in a and b
    returns pd.DataFrame with one new column LL
    '''
    print(columns[0])
    print(columns[1])
    df['s_expected'] = a*(df[columns[0]]+df[columns[1]])/(a+b)
    df['k_expected'] = b*(df[columns[0]]+df[columns[1]])/(a+b)

    df['k_semi_l'] = df[columns[1]]*np.log(df[columns[1]]/df['k_expected'])
    df['s_semi_l'] = df[columns[0]]*np.log(df[columns[0]]/df['s_expected'])
    df['k_semi_l'] = df['k_semi_l'].fillna(0)
    df['s_semi_l'] = df['s_semi_l'].fillna(0)
    df['LL'] = 2*(df['s_semi_l'] + df['k_semi_l'])
    
    del df['s_expected']
    del df['k_expected']
    del df['k_semi_l']
    del df['s_semi_l']
    
    df = df.sort_values(['LL'], ascending=False)
    return df
