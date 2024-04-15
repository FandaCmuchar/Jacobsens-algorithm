import numpy as np
import pandas as pd
from pathlib import Path

class NGramAnalyzer:
    def __init__(self, file_path: Path | str):
        self.file_path = file_path
        self.data = pd.read_csv(file_path, delimiter='\t', header=0, index_col=0, keep_default_na=False, na_filter=False)
        self.en_letter_freq = None
        self.en_letters_freq_sorted = None
        self.en_bigram_matrix = None

    def _get_x_gram_row_index(self, x: int) -> int:
        for row_idx, index_row in enumerate(self.data.iterrows()):
            index, row = index_row
            first_column_value = str(index)
            if f'{x}-gram' in first_column_value:
                return row_idx
        return None

    def get_en_letter_freq(self):
        if self.en_letter_freq is None:
            start_row = 0
            end_row = self._get_x_gram_row_index(2)
            number_matrix = self.data.iloc[start_row:end_row].apply(pd.to_numeric, errors='coerce')
            numpy_matrix = number_matrix.to_numpy()
            first_col = numpy_matrix[:,0]
            norm_numpy_matrix = first_col / np.sum(first_col) * 100
            self.en_letter_freq = {letter.lower(): percent for letter, percent in zip(list(number_matrix.index), norm_numpy_matrix)}
        return self.en_letter_freq

    def get_en_letters_sorted(self):
        if self.en_letters_freq_sorted is None:
            if self.en_letter_freq is None:
                self.get_en_letter_freq()
            self.en_letters_freq_sorted = list(self.en_letter_freq.keys())
        return self.en_letters_freq_sorted

    def get_en_bigram_matrix(self):
        if self.en_bigram_matrix is None:
            if self.en_letters_freq_sorted is None:
                self.get_en_letters_sorted()
            start_row = self._get_x_gram_row_index(2) + 1
            end_row = self._get_x_gram_row_index(3)
            data_part = self.data.iloc[start_row:end_row].apply(pd.to_numeric, errors='coerce')
            numpy_matrix = data_part.to_numpy()
            first_col = numpy_matrix[:,0]
            self.en_bigram_matrix = np.zeros((len(self.en_letters_freq_sorted), len(self.en_letters_freq_sorted)))
            for bigram_idx, bigram in enumerate(list(data_part.index)):
                letter1, letter2 = bigram
                idx1 = self.en_letters_freq_sorted.index(letter1.lower())
                idx2 = self.en_letters_freq_sorted.index(letter2.lower())
                self.en_bigram_matrix[idx1, idx2] = first_col[bigram_idx]
            self.en_bigram_matrix = self.en_bigram_matrix / np.sum(first_col) * 100
        return self.en_bigram_matrix
