import pandas as pd
import numpy as np
from Entity_EM import 


def test_noun_chunking():
    pass


def test_ner_tagging():
    pass


def test_extract_finalize():
    pass


def test_final_match():
    pass


if __name__ == '__main__':
    df_orig = pd.read_excel('Copy of Energy_newsdb_refineries_minhash_SDZ.xlsx')
    df_1 = df_orig[df_orig['Refinery'] == 'Y']

    df_ref = pd.read_excel('EPIX_Asset_Details_original.xls')
    df_ref = df_ref[['OperatorName', 'refineryName']]
    df_ref.fillna(' ', inplace=True)

    a = df_ref.refineryName.values
    b = df_ref.OperatorName.values
    canonicals = list(set(np.concatenate((a, b), axis=0)))
    kw = 'pipeline|refinery|plant|oil field|gas terminal'

    #df_1['extracted_asset_names'] = df_1.apply(lambda x: extract_finalize(x['Text'], kw, \
                    #['ORG', 'PERSON'], x['Title'] +', '+x['Owner'], 90), axis=1)
    test = df_1[:3].apply(lambda x: extract_finalize(x['Text'], kw, ['ORG','PERSON'], x['Title']+x['Owner'], 90), axis=1)
    print test
    #df_1[['Asset_name_extract_code', 'Asset_name_extracted']] \
                                        #= df_1['extracted_asset_names'].apply(pd.Series)

    #df_1['matched_asset_names'] = df_1.apply(lambda x: final_match( \
                               #x['Asset_name_extracted'], canonicals), axis=1)

    #df_1[['Asset_name_match_code', 'Asset_name_matched']] = df_1['matched_asset_names'].apply(pd.Series)

    #print sum(df_1['Asset_name_match_code']=='M')*1./167

    #df_1.drop(['extracted_asset_names', 'matched_asset_names'], axis=1, inplace = True)
    #writer = pd.ExcelWriter('Ziru_AssetName_refinery_only_test.xlsx'.replace('\\', os.sep))
    #df_1.to_excel(writer, 'Energy', index=False)
    #writer.save()
