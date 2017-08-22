from joblib import Parallel, delayed
import multiprocessing
import math
try:
    import arpa
except:
    pass
import os
import pandas
def process_by_sq(models, X, length, probabilities, guesses):
    probability_by_word = {}
        
    for word, model in models.items():
        try:
            w_score = model.score(X, length)
            probability_by_word[word] = w_score
        except Exception:
            probability_by_word[word] = -float(math.inf) 
        
    best_guess = max(probability_by_word.keys(), key=(lambda w: probability_by_word[w])) 
    guesses.append(best_guess)
    probabilities.append(probability_by_word)
    
if __name__ == '__main__':
    
    #df_probs = pandas.DataFrame(data={'col1': 4, 'col2': 4}, index=3)
    p = os.path.join('data', 'ukn.3.lm')
    models = arpa.loadf(p)  
    
    print('d')  