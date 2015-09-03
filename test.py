from hmm import BrownCorpus
import time

s = time.time()

hmm = BrownCorpus()

hmm.test_tag_sequence('test', 'test_result')
hmm.test_accuracy('test_result')

e = time.time()

print('elapsed time:', e-s)
