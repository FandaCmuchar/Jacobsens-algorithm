import random
import numpy as np
import numpy.typing as npt
from typing import Generator
from utils import perform_frequency_analysis, decipher_text
from string import ascii_lowercase
from ngram_analyzer import NGramAnalyzer

# https://www.researchgate.net/profile/Thomas-Jakobsen-6/publication/266714630_A_fast_method_for_cryptanalysis_of_substitution_ciphers/links/56ebe4fe08aefd0fc1c718ef/A-fast-method-for-cryptanalysis-of-substitution-ciphers.pdf

class JacobsenAlgorithm:
    def __init__(self, ngram_analyzer: NGramAnalyzer) -> None:
        
        self.ngram_analyzer = ngram_analyzer
        self.EN_LETTER_FREQ = self.ngram_analyzer.get_en_letter_freq()
        self.EN_LETTERS_SORTED = self.ngram_analyzer.get_en_letters_sorted()
        self.EN_BIGRAM_MATRIX = self.ngram_analyzer.get_en_bigram_matrix()
    
    def _deterministic_swap_generator(self) -> Generator[tuple[int, int], None, None]:
        # Generate deterministic swap pairs.
        for i in range(1, len(self.EN_LETTER_FREQ)):
            for j in range(len(self.EN_LETTER_FREQ) - i):
                yield (j, j + i)
        
        return None


    def _random_swap_generator(self) -> Generator[tuple[int, int], None, None]:
        # Generate random swap pairs based on letter frequency.
        random_index_distribution = []
        alphabet_sorted = list(self.EN_LETTER_FREQ.keys())

        # Generate index distribution with respect to letter frequency
        for letter, frequency in self.EN_LETTER_FREQ.items():
            index = alphabet_sorted.index(letter)
            random_index_distribution.extend([index] * int(1000 * frequency))

        while True:
            yield random.sample(random_index_distribution, 2)

    def generate_bigram_matrix(self, text: str) -> npt.NDArray:
        # Generate bigram matrix from given text.
        bigram_matrix = np.zeros(shape=(len(ascii_lowercase), len(ascii_lowercase)))

        for i in range(len(text) - 1):
            char_1_idx = self.EN_LETTERS_SORTED.index(text[i])
            char_2_idx = self.EN_LETTERS_SORTED.index(text[i+1])
            bigram_matrix[char_1_idx, char_2_idx] += 1
        
        bigram_matrix = bigram_matrix / np.sum(bigram_matrix) * 100
        return bigram_matrix

    def optimize_bigram_matrix(self, ciphered_text: str, random_swap_gen = True, max_iters: int = 10000, print_score=False) -> list[str]:
        
        self.swap_generator = self._random_swap_generator() if random_swap_gen else self._deterministic_swap_generator()

        cipher_freq_ordered = perform_frequency_analysis(ciphered_text)
        cipher_key = list(cipher_freq_ordered.keys())
        cipher_key.extend([l for l in ascii_lowercase if l not in cipher_key])

        putative_plain_text = decipher_text(ciphered_text, cipher_key, self.EN_LETTER_FREQ)
        bigram_matrix = self.generate_bigram_matrix(putative_plain_text)
        best_score = np.abs(bigram_matrix - self.EN_BIGRAM_MATRIX).sum()

        iters_since_last_improvement = 0

        while (a_b := next(self.swap_generator, None)) is not None and iters_since_last_improvement < max_iters:
            a, b = a_b
            potential_bi_mat = np.copy(bigram_matrix)
            potential_bi_mat[[b, a]], potential_bi_mat[:, [b, a]] = potential_bi_mat[[a, b]], potential_bi_mat[:, [a, b]]
            score = np.abs(potential_bi_mat - self.EN_BIGRAM_MATRIX).sum()

            if score < best_score:
                bigram_matrix, cipher_key[b], cipher_key[a] = potential_bi_mat, cipher_key[a], cipher_key[b]
                best_score = score
                if print_score:
                    print(f'Improved score: {score}')
                iters_since_last_improvement = 0
            else:
                iters_since_last_improvement += 1           

        return cipher_key