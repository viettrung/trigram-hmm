# trigram-hmm
This is an implementation of a second-order HMM

How to use:

1. Download and extract Brown Corpus (More information: https://en.wikipedia.org/wiki/Brown_Corpus)
2. Checkout code from github (https://github.com/viettrung/trigram-hmm/)
3. Go to directory of folder checkout from github
4. Run file with python3: 
 - python3 ./main.py
5. Wait for result.

Note: Sentence with new word (not include in Brown Corpus) the result will be wrong 
--> need care about new word case.

Sample data: 

['I', "wouldn't", 'have', 'missed', 'it', 'for', 'anything', '.']
k:  1
k:  2
k:  3
k:  4
k:  5
k:  6
k:  7
k:  8
{1: 'ppss', 2: 'md*', 3: 'hv', 4: 'vbn', 5: 'ppo', 6: 'in', 7: 'pn', 8: '.'}
['``', 'O', '!', '!']
k:  1
k:  2
k:  3
k:  4
{1: '``', 2: 'uh', 3: '.', 4: '.'}
