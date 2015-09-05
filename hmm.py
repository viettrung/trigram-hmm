import os
import re
import time

BROWN_CORPUS_DIR = 'brown'
DICTIONARY_DIR = 'dictionary'
TEST_DIR = 'test'

WORD = 'word'
WORD_TAG = 'word_tag'
UNIGRAM = 'unigram'
BIGRAM = 'bigram'
TRIGRAM = 'trigram'
POSSIBLE_TAGS = "possible_tags"
FILE_TEST_TAG_ORIGIN = 'test_tag_origin'
FILE_TEST = 'test'

LAMDA_1 = 0.2
LAMDA_2 = 0.4
LAMDA_3 = 0.4


class BrownCorpus:
    word_dict = {}
    word_tag_dict = {}
    unigram_tag_dict = {}
    bigram_tag_dict = {}
    trigram_tag_dict = {}
    possible_tags_dict = {}
    distinct_tags = []

    test = ''
    test_tag = ''

    def __init__(self):

        if os.path.isdir(DICTIONARY_DIR):
            self.word_dict = get_trained_data(WORD)
            self.word_tag_dict = get_trained_data(WORD_TAG)
            self.unigram_tag_dict = get_trained_data(UNIGRAM)
            self.bigram_tag_dict = get_trained_data(BIGRAM)
            self.trigram_tag_dict = get_trained_data(TRIGRAM)
            self.possible_tags_dict = get_trained_data(POSSIBLE_TAGS)
        else:
            list_of_filename = os.listdir(BROWN_CORPUS_DIR)
            count_file = 0
            for filename in list_of_filename:
                if re.match('c[a-r]\d{2}', filename) is not None:
                    count_file += 1
                    with open(BROWN_CORPUS_DIR + "/" + filename) as corpus_file:
                        lines = corpus_file.readlines()
                        for line in lines:
                            if line.strip():
                                line += " STOP/STOP"
                                penult_tag = ''
                                last_tag = ''
                                for word_tag in line.split():
                                    word, tag = word_tag.rsplit('/', 1)

                                    if count_file <= 490:

                                        if word in self.possible_tags_dict:
                                            self.possible_tags_dict[word].add(tag)
                                        else:
                                            self.possible_tags_dict[word] = {tag}

                                        if word in self.word_dict:
                                            self.word_dict[word] += 1
                                        else:
                                            self.word_dict[word] = 1

                                        if (word, tag) in self.word_tag_dict:
                                            self.word_tag_dict[word, tag] += 1
                                        else:
                                            self.word_tag_dict[word, tag] = 1

                                        if tag in self.unigram_tag_dict:
                                            self.unigram_tag_dict[tag] += 1
                                        else:
                                            self.unigram_tag_dict[tag] = 1

                                        if (last_tag, tag) in self.bigram_tag_dict:
                                            self.bigram_tag_dict[last_tag, tag] += 1
                                        else:
                                            self.bigram_tag_dict[last_tag, tag] = 1

                                        if (penult_tag, last_tag, tag) in self.trigram_tag_dict:
                                            self.trigram_tag_dict[penult_tag, last_tag, tag] += 1
                                        else:
                                            self.trigram_tag_dict[penult_tag, last_tag, tag] = 1

                                        penult_tag = last_tag
                                        last_tag = tag

                                    elif len(line.split()) > 2:
                                        self.test += word + '\n'
                                        if word != 'STOP':
                                            self.test_tag += word + '\t' + tag + '\n'

                                    else:
                                        break

                        corpus_file.close()

            os.makedirs(DICTIONARY_DIR)
            save_trained_data(self.word_dict, WORD)
            save_trained_data(self.word_tag_dict, WORD_TAG)
            save_trained_data(self.unigram_tag_dict, UNIGRAM)
            save_trained_data(self.bigram_tag_dict, BIGRAM)
            save_trained_data(self.trigram_tag_dict, TRIGRAM)
            save_trained_data(self.possible_tags_dict, POSSIBLE_TAGS)

            os.makedirs(TEST_DIR)
            save_test_data(self.test, FILE_TEST)
            save_test_data(self.test_tag, FILE_TEST_TAG_ORIGIN)

        self.process_low_frequency_word()
        self.distinct_tags = set(self.unigram_tag_dict.keys())

    def process_low_frequency_word(self):
        new = {}
        possible_tags_dict = {}
        # change words with freq <5 into unknown words "<unkown>"
        for (word, tag) in self.word_tag_dict:
            new[word, tag] = self.word_tag_dict[word, tag]
            possible_tags_dict[word] = self.possible_tags_dict[word]
            if self.word_tag_dict[word, tag] < 5:
                if ('<unkown>', tag) not in new:
                    new['<unkown>', tag] = 0
                new['<unkown>', tag] += self.word_tag_dict[word, tag]
                if '<unkown>' not in self.possible_tags_dict:
                    possible_tags_dict['<unkown>'] = {tag}
                possible_tags_dict['<unkown>'] = self.possible_tags_dict[word]
        self.word_tag_dict = new
        self.possible_tags_dict = possible_tags_dict

    def get_e(self, word, tag):
        if (word, tag) in self.word_tag_dict:
            return float(self.word_tag_dict[word, tag]) / self.unigram_tag_dict[tag]
        else:
            return 0.0

    def get_q(self, penult_tag, last_tag, current_tag):
        # if (penult_tag, last_tag, current_tag) in self.trigram_tag_dict:
        #     return float(self.trigram_tag_dict[penult_tag, last_tag, current_tag]) / self.bigram_tag_dict[last_tag, current_tag]
        if (penult_tag, last_tag, current_tag) in self.trigram_tag_dict and (
                penult_tag, last_tag) in self.bigram_tag_dict:
            value_1 = LAMDA_1 * float(self.trigram_tag_dict[penult_tag, last_tag, current_tag]) / \
                      self.bigram_tag_dict[penult_tag, last_tag]
        else:
            value_1 = 0.0

        if (last_tag, current_tag) in self.bigram_tag_dict and last_tag in self.unigram_tag_dict:
            value_2 = LAMDA_2 * float(self.bigram_tag_dict[last_tag, current_tag]) / \
                      self.unigram_tag_dict[last_tag]
        else:
            value_2 = 0.0

        if current_tag in self.unigram_tag_dict:
            value_3 = LAMDA_3 * float(self.unigram_tag_dict[current_tag]) / \
                      len(self.unigram_tag_dict)
        else:
            value_3 = 0.0

        return value_1 + value_2 + value_3
        # else:
        #     return 0.0

    def get_tag_sequence(self, sentence):
        print('tagging...')
        pi = {}
        pi[0, '', ''] = 1
        bp = {}
        n = len(sentence)
        y = {}
        for k in range(1, n + 1):
            word = self.get_word(sentence, k - 1)
            last_word = self.get_word(sentence, k - 2)
            penult_word = self.get_word(sentence, k - 3)

            for u in self.get_tags(k - 1, last_word):
                for v in self.get_tags(k, word):
                    pi[k, u, v], bp[k, u, v] = max(
                        [(pi[k - 1, w, u] * self.get_q(w, u, v) * self.get_e(word, v), w) for w in
                         self.get_tags(k - 2, penult_word)])

        v_tags = self.possible_tags_dict[self.get_word(sentence, n - 1)]
        u_tags = self.possible_tags_dict[self.get_word(sentence, n - 2)]

        prob, y[n - 1], y[n] = max([(pi[n, u, v] * self.get_q(u, v, 'STOP'), u, v) for u in u_tags for v in v_tags])

        for k in range(n - 2, 0, -1):
            y[k] = bp[k + 2, y[k + 1], y[k + 2]]

        return y

    def get_word(self, sentence, k):
        if k < 0:
            return ''
        else:
            if sentence[k] not in self.word_dict:
                print("\033[93m <Warning: '%s' is not exist in the training data> \033[0m" % sentence[k])
                return '<unkown>'
            return sentence[k]

    def get_tags(self, k, word):
        if k in [0, -1]:
            return set([''])
        else:
            return self.possible_tags_dict[word]

    def test_accuracy(self, test_result):
        correct = 0
        n = 0
        fkey = open(TEST_DIR + '/' + FILE_TEST_TAG_ORIGIN, 'r')
        for line in open(TEST_DIR + '/' + test_result, 'r'):
            n += 1
            if line == fkey.readline():
                correct += 1
        fkey.close()
        print('tag accuracy: ', float(correct) / n)

    def test_tag_sequence(self, testFileName, outFileName):
        start_time = time.time()

        sentence = []
        fout = open(TEST_DIR + '/' + outFileName, 'w')

        for line in open(TEST_DIR + '/' + testFileName, 'r'):
            line = line.strip()
            if line == 'STOP':
                if sentence:
                    # sentence.append(line)
                    print(sentence)
                    path = self.get_tag_sequence(sentence)
                    print(path)
                    for i in range(len(sentence)):
                        fout.write(sentence[i] + '\t' + path[i + 1] + '\n')
                    sentence = []
            else:
                sentence.append(line)

        finish_time = time.time()
        fout.close()
        print('time to execute test_tag_sequence method:', finish_time - start_time)


def save_trained_data(data, filename):
    file_path = DICTIONARY_DIR + '/' + filename
    file = open(file_path, 'w')
    file.write(str(data))
    file.close()


def save_test_data(data, filename):
    file_path = TEST_DIR + '/' + filename
    file = open(file_path, 'w')
    file.write(str(data))
    file.close()


def get_trained_data(filename):
    file_path = DICTIONARY_DIR + '/' + filename
    file = open(file_path, 'r')
    file_content = file.read()
    file.close()
    return eval(file_content)
