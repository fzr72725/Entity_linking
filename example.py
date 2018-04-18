import pandas as pd
import numpy as np
import time
import os
import datetime

import Entity_linking as em


if __name__ == '__main__':
    df_orig = pd.read_excel('Entity_linking/data/Energy_newsdb_refineries_minhash_SDZ.xlsx')
    df_1 = df_orig[df_orig['Refinery'] == 'Y'][:3]#[['Article_Number','Text','Title','Owner']]

    df_ref = pd.read_excel('Entity_linking/data/EPIX_Asset_Details_original.xls')
    df_ref = df_ref[['OperatorName', 'refineryName']]
    df_ref.fillna(' ', inplace=True)


    # generate Asset_Name
    a = df_ref.refineryName.values
    b = df_ref.OperatorName.values
    canonicals = list(set(np.concatenate((a, b), axis=0)))
    kw = 'pipeline|refinery|plant|oil field|gas terminal'
    print 'Extracting refinery names...'
    start = time.time()
    df_1.loc[:, 'extracted_asset_names'] = df_1.apply(lambda x: em.extract_finalize_asset(x['Text'], kw, \
                    ['ORG', 'PERSON'], x['Title'] +', '+x['Owner'], 90), axis=1)
    end = time.time()
    time_intervale = end - start
    print("---extract took {} seconds ---".format(time_intervale))

    df_1[['Asset_name_extract_code', 'Asset_name_extracted']] \
                                        = df_1['extracted_asset_names'].apply(pd.Series)
    print 'Matching refinery names against EPIX lists...'
    df_1.loc[:, 'matched_asset_names'] = df_1.apply(lambda x: em.final_match( \
                               x['Asset_name_extracted'], canonicals), axis=1)

    df_1[['Asset_name_match_code', 'Asset_name_matched']] = df_1['matched_asset_names'].apply(pd.Series)

    print sum(df_1['Asset_name_match_code']=='M')*1./167

    df_1.drop(['extracted_asset_names', 'matched_asset_names'], axis=1, inplace = True)
    now = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    writer = pd.ExcelWriter('result/example_asset_result_{}.xlsx'.replace('\\', os.sep).format(now))
    df_1.to_excel(writer, 'Energy', index=False)
    writer.save()

    '''
    # Generate Owner
    df_1 = df_orig[df_orig['Refinery'] == 'Y'][:3]
    company_list = df_ref.OperatorName.values
    print 'Extracting company names...'
    start = time.time()
    df_1.loc[:, 'extracted_Owner_names'] = df_1.apply(lambda x: em.extract_finalize_comp(x['Text'], \
                    ['ORG', 'PERSON'], 'This is placeholder, '+x['Title'], 90), axis=1)
    end = time.time()
    time_intervale = end - start
    print("---extract took {} seconds ---".format(time_intervale))

    df_1[['Owner_name_extract_code', 'Owner_name_extracted']] \
                                        = df_1['extracted_Owner_names'].apply(pd.Series)
    print 'Matching company names against EPIX lists...'
    df_1.loc[:, 'matched_Owner_names'] = df_1.apply(lambda x: em.final_match( \
                               x['Owner_name_extracted'], company_list), axis=1)

    df_1[['Owner_name_match_code', 'Owner_name_matched']] = df_1['matched_Owner_names'].apply(pd.Series)

    #print sum(df_1['Owner_name_match_code']=='M')*1./167

    df_1.drop(['extracted_Owner_names', 'matched_Owner_names'], axis=1, inplace = True)
    now = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    writer = pd.ExcelWriter('result/example_owner_result_{}.xlsx'.replace('\\', os.sep).format(now))
    df_1.to_excel(writer, 'Energy', index=False)
    writer.save()
    '''
