import csv
import re
import traceback
from fuzzywuzzy import fuzz, process
# from ner import SocketNER
import spacy


def noun_chunking(article, keywords, libs=['spacy']):
    '''
    INPUT:
    article: one document/text, type: string
    keywords: keywords to filter for only related noun chunks, have to follow
    the following format: pipeline|refinery|plant|oil field|gas terminal, type:
    string
    libs: the libraries to use for chunking, e.g. spacy/stanford, type: list
    OUTPUT:
    extracted noun chunks, type: list

    e.g. noun_chunking(some_doc, 'pipeline|refinery|plant', libs=['spacy',
                       'stanford'])
    '''
    try:
        # get all noun chunks:
        nouns = []
        for lib in libs:
            if lib == 'spacy':
                nlp = spacy.load('en')
                doc = nlp(article.decode('utf-8'))
                # nouns = []
                for np in doc.noun_chunks:
                    # get each noun chunk, store in nouns
                    nouns.append(np.text)
            elif lib == 'stanford':
                pass

        # filter with keywords and NNP:
        # 1) keywords regex filtering
        r = re.compile('^.+('+keywords+')', re.IGNORECASE)
        keyword_nouns = list(filter(r.match, nouns))

        # 2) NNP filtering
        relevant_nouns = []
        for noun in keyword_nouns:
            flag = False
            words = re.split('('+keywords+')', noun,  flags=re.IGNORECASE)
            # the first two words are which the most likely to be proper nouns
            # if exist
            phrase1 = words[0] + words[1]
            # here we only use spaCy to generate the syntactic tags
            doc = nlp(phrase1)
            for word in doc:
                if word.tag_ == "NNP":
                    flag = True
            # store noun chunk with proper noun in a new list relevant_nouns
            if flag:
                relevant_nouns.append(noun)
        return relevant_nouns

    except Exception as error:
        print ('-'*60)
        print (traceback.format_exc())
        print ("Text :" + str(article))
        print ('-'*60)
        return "Error Occured"


def ner_tagging(article, entity_types, libs=['spacy']):
    '''
    This function use existing NER libraries to extract certain type of
    entities from an article
    INPUT:
    article: one document/text, type: string
    entity_type: e.g. ['ORG', 'PERSON'], type: list
    libs: the libraries to use for chunking, e.g. spacy/stanford, type: list
    OUTPUT:
    NER extracted entities, type: list
    '''
    try:
        # extract all name entities
        ner = []
        for lib in libs:
            if lib == 'spacy':
                nlp = spacy.load('en')
                parsedEx = nlp(article.decode('utf-8'))
                ents = list(parsedEx.ents)
                # ner = []
                for entity in ents:
                    if entity.label_ in entity_types:
                        # pick the desired entity type into list ner
                        ner.append(' '.join(t.orth_ for t in entity))
                    elif entity_types == 'no-specific':
                        ner.append(' '.join(t.orth_ for t in entity))
            elif lib == 'stanford':
                    pass
        return ner

    except Exception as error:
        print ('-'*60)
        print (traceback.format_exc())
        print ("Text :" + str(article))
        print ('-'*60)
        return "Error Occured"


def extract_finalize_asset(article, keywords, entity_types, ref_build_txt, overlap_score_cutoff):
    '''
    This function finalizes the entity names using the results from noun
    chunking and ner extracting
    INPUT:
    article: one document/text, type: string
    keywords: keywords to filter for only related noun chunks, have to follow
    the following format: pipeline|refinery|plant|oil field|gas terminal, type: string
    entity_types: e.g. ['ORG', 'PERSON'], type: list
    ref_build_txt: list of entity references to select the best final entity, type: string
    overlap_score_cutoff: minimum fuzzy matching score between noun chunks and
    ner list, e.g. 80

    OUTPUT:
    final name entity and matching code, type: tuple
    matching code dictionary:
    1: from noun chunks and ner list overlap
    2. from combination of noun chunks and ner list matching with specific
    reference (extracted from other df columns)
    3: 1st element of noun chunks
    4: no entity identified
    '''
    try:
        noun_chunks = noun_chunking(article, keywords)
        ner_list = ner_tagging(article, entity_types)
        name_ref = ner_tagging(ref_build_txt, 'no-specific')

        # use existing matched references to match with noun chunks and ner list, this gives
        # the 1st highest confidence
        best = []
        full_list = list(set(noun_chunks + ner_list))
        for name in full_list:
            ent = process.extractOne(name, name_ref,
                                    scorer=fuzz.partial_ratio, score_cutoff=overlap_score_cutoff)
            if ent is not None:
                best.append(ent)
        best.sort(key=lambda tup: (tup[1]), reverse=True)

        # find overlap between noun chunks and ner list, the overlap entity gives the
        # 2nd highest confidence
        chunk_ner_overlap = []
        if noun_chunks:
            for org in ner_list:
                # fuzzy match ner extracted org with relevent noun chunks
                extracted_org = process.extractOne(org, noun_chunks, score_cutoff=overlap_score_cutoff, scorer=fuzz.partial_ratio)
                if extracted_org:
                    # if the fuzzy score is high enough, store corresponding
                    # noun chunk in overlap list
                    chunk_ner_overlap.append(extracted_org)

        # if best:
            # return 2, best[0][0]
        if chunk_ner_overlap:
            # desc order the overlap entities by the fuzzy score
            chunk_ner_overlap.sort(key=lambda tup: (tup[1]), reverse=True)  # optimize the key
            # the highest ranked entity will be the final result for asset name
            return 1, chunk_ner_overlap[0][0]
        elif best:
            return 2, best[0][0]
        elif noun_chunks:
            # if no overlap found and no ner entities, return the first element in noun chunk list
            return 3, noun_chunks[0]
        else:
            return 4, "None"

    except Exception as error:
        print ('-'*60)
        print (traceback.format_exc())
        print ("Text :" + str(article))
        print ('-'*60)
        return "Error Occured"


def extract_finalize_comp(article, entity_types, ref_build_txt, overlap_score_cutoff):
    '''
    This function finalizes the company names using the results from noun
    chunking and ner extracting
    INPUT:
    article: one document/text, type: string
    entity_types: e.g. ['ORG', 'PERSON'], type: list
    ref_build_txt: list of entity references to select the best final entity, type: string
    overlap_score_cutoff: minimum fuzzy matching score between noun chunks and
    ner list, e.g. 80

    OUTPUT:
    final name entity and matching code, type: tuple
    matching code dictionary:
    1: from noun chunks and ner list overlap
    2. from combination of noun chunks and ner list matching with specific
    reference (extracted from other df columns)
    3: 1st element of noun chunks
    4: no entity identified
    '''
    try:
        ner_list = ner_tagging(article, entity_types)
        name_ref = ner_tagging(ref_build_txt, 'no-specific')

        # use existing matched references to match with noun chunks and ner list, this gives
        # the 1st highest confidence
        best = []
        full_list = list(set(ner_list))
        for name in full_list:
            ent = process.extractOne(name, name_ref,
                                    scorer=fuzz.partial_ratio, score_cutoff=overlap_score_cutoff)
            if ent is not None:
                best.append(ent)
        best.sort(key=lambda tup: (tup[1]), reverse=True)

        if best:
            return 2, best[0][0]
        elif ner_list:
            # if no overlap found and no ner entities, return the first element in noun chunk list
            return 3, ner_list[0]
        else:
            return 4, "None"

    except Exception as error:
        print ('-'*60)
        print (traceback.format_exc())
        print ("Text :" + str(article))
        print ('-'*60)
        return "Error Occured"


def final_match(name, canonicals):
    '''
    This function uses fuzzy match to determine if an article has matching entity in
    the target company list
    INPUT:
    name: entity extracted from an article, type: string
    canonicals: the dictionary of company list to be matched with, type: list

    OUTPUT:
    final matching result and match code, tuple:
    matching code dictionary:
    M: match found in target company list, ideal result
    E: no match in target list, use extracted entity
    '''
    ent = process.extractOne(name, canonicals,
                                scorer=fuzz.partial_ratio, score_cutoff=80)
    #if ent is not None:
        #return 'M-80', ent[0]
    # If high score cut off gives no match, lower score, and do other checks
    #else:
    if ent is None:
        ent = process.extractOne(name, canonicals,
                                scorer=fuzz.token_sort_ratio, score_cutoff=10)
        # validate the match result using substring
        if ent:
            matched_clean_ent = ent[0].lower().replace(' ', '')
            clean_ent = name.lower().replace(' ', '')
            if (clean_ent not in matched_clean_ent) and (matched_clean_ent not in clean_ent):
                ent = None
    if ent is not None:
        return 'M-10', ent[0]
    else:
        return 'no match', None
