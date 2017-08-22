import warnings
from asl_data import SinglesData

from joblib import Parallel, delayed
import multiprocessing
import math
import time
import os
import arpa

def calculate_with_LM(so_far, current_idx: int, lm, sq, word):
    try:
        if current_idx == sq[0]:
            return lm.log_p('<s> '+ word)
        if current_idx == sq[0]:        
            return lm.log_p(word + '</s>')
        sentence = ''
        log_l = 0
        for i in [m for m in sq if m < current_idx]:
            sentence += so_far[i][0] + ' '  
            log_l += so_far[i][1]
        return lm.log_s(sentence + word) 
    except :
        return 0

def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    
    #num_cores = multiprocessing.cpu_count()

    startTime = int(round(time.time() * 1000))
    
    p = os.path.join('data', 'ukn.3.lm')
    language_model = arpa.loadf(p)[0]  
    
    idx = 0
    #Parallel(n_jobs=num_cores)(process_by_sq(models, X, length, probabilities, guesses) for _, (X, length) in test_set.get_all_Xlengths().items())        
    for _, (X, length) in test_set.get_all_Xlengths().items():
        probability_by_word = {}
        bare_prob = {}
        sq = [si for k, si in test_set.sentences_index.items() if idx in si]
        for word, model in models.items():
            w_score = -float(math.inf) 
            try:    
                w_score = model.score(X, length)
            except:
                pass
            bare_prob[word] = w_score
            probability_by_word[word] = w_score + calculate_with_LM(guesses, idx, language_model, sq[0], word)
        
        idx += 1
        best_guess = max(probability_by_word.keys(), key=(lambda w: probability_by_word[w])) 
        best_bare = max(bare_prob.values())
        guesses.append(best_guess, best_bare)
        probabilities.append(probability_by_word)
    
    endTime = int(round(time.time() * 1000))
    print(endTime - startTime,'ms')    
    
    return probabilities, [g[0] for g in guesses]

