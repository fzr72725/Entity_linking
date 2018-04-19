import unittest
import Entity_linking as em

test_doc = 'Gary Winston Lineker was an excellent football player. GARY WINSTON LINEKER was a striker. gary winston lineker was born in England. gARY WiNsTon lInEker is married to Danielle Bux. \
Gary W. Lineker, Kanny Sansom and Peter Shilton played together.'


class TestEM(unittest.TestCase):
    # the function name has to start with "test_"
    def test_noun_chunking(self):
        result = em.noun_chunking(test_doc, ' ', ['spacy'])
        self.assertTrue(type(result), 'list')
        self.assertIsNotNone(result)

    def test_ner_tagging(self):
        result = em.ner_tagging(test_doc, ['PERSON'], ['spacy'])
        self.assertTrue(type(result), 'list')
        self.assertIsNotNone(result)

    def test_extract_finalize_comp(self):
        result = em.extract_finalize_comp(test_doc, ['PERSON'], 'place_holder', 90)
        self.assertTrue(type(result), 'tuple')
        self.assertTrue(type(result[1]), 'string')
        self.assertIsNotNone(result)

    def test_extract_finalize_asset(self):
        result = em.extract_finalize_comp(test_doc, ['PERSON'], 'place_holder', 90)
        self.assertTrue(type(result), 'tuple')
        self.assertTrue(type(result[1]), 'string')
        self.assertIsNotNone(result)
