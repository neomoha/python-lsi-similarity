# Copyright (c) <2014>, <Mohamed Sordo>
# Email: mohamed ^dot^ sordo ^at^ gmail ^dot^ com
# Website: http://msordo.weebly.com
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.

import os, sys, pickle, argparse
import numpy
from gensim import corpora, models, similarities

import config, cleaner

def cosine(v1, v2):
    cos = numpy.dot(v1, v2)
    cos /= numpy.linalg.norm(v1)
    cos /= numpy.linalg.norm(v2)
    return cos

class MyCorpus(object):
    def __init__(self, corpus_filename, dictionary):
        self.dictionary = dictionary
        self.corpus_filename = corpus_filename
        self.docs = []
    def __iter__(self):
        for line in open(self.corpus_filename):
            #assume there's one document per line, items separated by tab
            doc, documents_weights = line.strip().split("\t")
            text = []
            for document, weight in eval(documents_weights):
                text.extend([document]*int(weight))
            self.docs.append(doc)
            yield self.dictionary.doc2bow(text)

class Model:
    def __init__(self, dict_filename, corpus_filename, num_topics=50):
        self.num_topics = num_topics
        self.original_dict_filename = dict_filename
        self.original_corpus_filename = corpus_filename
        dict_suffix = dict_filename[dict_filename.rfind("/")+1:dict_filename.rfind(".")]
        corpus_suffix = corpus_filename[corpus_filename.rfind("/")+1:corpus_filename.rfind(".")]
        self.dict_filename = 'tmp/%s.dict' % dict_suffix
        self.corpus_filename = 'tmp/%s.mm' % corpus_suffix
        self.lsi_filename = 'tmp/%s_%s.lsi' % (corpus_suffix, num_topics)
        self.index_filename = 'tmp/%s_%s.lsi.index' % (corpus_suffix, num_topics)
        self.doc2id_filename = "tmp/%s.doc2id.pickle" % corpus_suffix
        self.id2doc_filename = "tmp/%s.id2doc.pickle" % corpus_suffix
        self._create_directories()

    def _create_directories(self):
        if not os.path.exists("tmp"):
            os.mkdir("tmp")

    def _create_docs_dict(self, docs):
        '''
        Create the dictionaries that translate from document name to document index in the corpus, and viceversa
        '''
        self.doc2id = dict(zip(docs, range(len(docs))))
        self.id2doc = dict(zip(range(len(docs)), docs))
        pickle.dump(self.doc2id, open(self.doc2id_filename, "w"))
        pickle.dump(self.id2doc, open(self.id2doc_filename, "w"))
    
    def _load_docs_dict(self):
        '''
        Load the dictionaries that translate from document name to document index in the corpus, and viceversa
        '''
        self.doc2id = pickle.load(open(self.doc2id_filename))
        self.id2doc = pickle.load(open(self.id2doc_filename))
    
    def _generate_dictionary(self):
        print "generating dictionary..."
        documents = []
        with open(self.original_dict_filename) as f:
            documents = [[line.strip()] for line in f]
        self.dictionary = corpora.Dictionary(documents)
        self.dictionary.save(self.dict_filename)
    
    def _load_dictionary(self, regenerate=False):
        '''
        Load the dictionary gensim object. If the dictionary object does not exist, or regenerate is set to True, it will generate it.
        '''
        if not os.path.exists(self.dict_filename) or regenerate is True:
            self._generate_dictionary()
        else:
            self.dictionary = corpora.Dictionary.load(self.dict_filename)

    def _generate_corpus(self):
        print "generating corpus..."
        self.corpus = []
        corpus_memory_friendly = MyCorpus(self.original_corpus_filename, self.dictionary)
        count = 0
        for vector in corpus_memory_friendly:
            self.corpus.append(vector)
            count += 1
            if count % 10000 == 0:
                print count, "vectors processed"
        self._create_docs_dict(corpus_memory_friendly.docs)
        corpora.MmCorpus.serialize(self.corpus_filename, self.corpus)
        
    def _load_corpus(self, regenerate=False):
        '''
        Load the corpus gensim object. If the corpus object does not exist, or regenerate is set to True, it will generate it.
        '''
        if not os.path.exists(self.corpus_filename) or regenerate is True:
            self._generate_corpus()
        else:
            self.corpus = corpora.MmCorpus(self.corpus_filename)

    def _generate_lsi_model(self, regenerate=False):
        print "generating lsi models..."
        if not os.path.exists(self.lsi_filename) or regenerate is True:
            self.lsi = models.LsiModel(self.corpus, id2word=self.dictionary, num_topics=self.num_topics)
            self.lsi.save(self.lsi_filename)
            self.index = similarities.MatrixSimilarity(self.lsi[self.corpus])
            self.index.save(self.index_filename)
        elif not os.path.exists(self.index_filename):
            self.lsi = models.LsiModel.load(self.lsi_filename)
            self.index = similarities.MatrixSimilarity(self.lsi[self.corpus])
            self.index.save(self.index_filename)
    
    def _load_lsi_model(self, regenerate=False):
        '''
        Load the LSI and the index gensim object. If any of the two object does not exist, or regenerate is set to True, it will generate it.
        '''
        if os.path.exists(self.lsi_filename) and os.path.exists(self.index_filename) and regenerate is False:
            self.lsi = models.LsiModel.load(self.lsi_filename)
            self.index = similarities.MatrixSimilarity.load(self.index_filename)
        else:
            self._generate_lsi_model(regenerate)
    
    def load(self, regenerate=False):
        '''
        Load all the necessary objects for the model. If any object does not exist, it will generate it.
        '''
        self._load_dictionary(regenerate)
        self._load_corpus(regenerate)
        self._load_lsi_model(regenerate)
        self._load_docs_dict()
    
    def _get_vector(self, doc):
        vec_bow = None
        try:
            vec_bow = self.corpus[self.doc2id[doc]]
        except KeyError:
            print "Document '%s' does not exist. Have you used the proper string cleaner?" % doc
        return vec_bow
    
    def get_similars(self, doc, num_sim=20):
        '''
        Given a document (doc), this method retrieves the num_sim most similar documents in the LSI models
        '''
        vec_bow = self._get_vector(doc)
        if vec_bow is None:
            return []
        vec_lsi = self.lsi[vec_bow]
        sims = self.index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])[1:num_sim+1]
        sims = [(self.id2doc[docid], weight) for docid, weight in sims]
        return sims
    
    def get_pairwise_similarity(self, doc1, doc2):
        '''
        Given two document names (doc1 and doc2), this method computes the cosine similarity between the documents' vectors in the LSI models
        '''
        vec_bow1 = self._get_vector(doc1)
        vec_bow2 = self._get_vector(doc2)
        if vec_bow1 is None or vec_bow2 is None:
            return None
        vec_lsi1 = [val for idx,val in self.lsi[vec_bow1]]
        vec_lsi2 = [val for idx,val in self.lsi[vec_bow2]]
        return cosine(vec_lsi1, vec_lsi2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Item similarity models using Latent Semantic Indexing')
    parser.add_argument('item', help='The item name')
    parser.add_argument('-n', '--num_topics', type=int, default=100, help='Number of topics, i.e. number of factors to use from the original SVD decomposition (default=100)')
    parser.add_argument('-s', '--num_similars', type=int, default=20, help='Number of similar items to retrieve (deafult=20)')
    parser.add_argument('-c', '--cleaner', default="DefaultCleaner", help='An object that cleans the item from special chars (deafult=DefaultCleaner)')
    parser.add_argument('-r', '--regenerate_models', type=bool, default=False, help='regenerate models even if they already exist (default=False)')
    parser.add_argument('-p', '--pairwise_similarity', default=None, help='Computer pairwise similarity given a second item as argument (default=None)')
    
    args = parser.parse_args()
    
    model = Model(config.DICTIONARY_FILENAME, config.CORPUS_FILENAME, num_topics=args.num_topics)
    model.load(args.regenerate_models)
    try:
        item_cleaner = getattr(cleaner, args.cleaner)()
    except AttributeError:
        print "Cleaner '%s' does not exist. Using 'DefaultCleaner' instead" % args.cleaner
        item_cleaner = cleaner.DefaultCleaner()
    if args.pairwise_similarity is not None:
        print model.get_pairwise_similarity(item_cleaner.clean(args.item), item_cleaner.clean(args.pairwise_similarity))
    else:
        sims = model.get_similars(item_cleaner.clean(args.item), args.num_similars)
        for sim in sims:
            print sim
    