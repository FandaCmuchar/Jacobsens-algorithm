import random
import string
from collections import Counter
from rich.progress import track

def random_substitution_cipher(text: str) -> tuple[str, dict]:
    # filter text
    filtered_text = text.lower()
    filtered_text = ''.join(char for char in filtered_text if char in string.ascii_lowercase)

    # Creating a list of all lowercase and uppercase letters
    letters = string.ascii_lowercase
    # Shuffling the letters to create a random substitution
    shuffled_letters = list(letters)
    random.shuffle(shuffled_letters)

    # Creating the substitution dictionary
    substitution_key = {shuffled_letters[i]: l for i, l in enumerate(letters)}
    # Encrypting the text using the substitution dictionary
    ciphered_text = ''.join(substitution_key[char] for char in filtered_text)

    return ciphered_text, {val: key for key, val in substitution_key.items()}


def perform_frequency_analysis(cipher_text: str) -> tuple[dict]:
    # Remove non-alphabetic characters
    filtered_text = ''.join(filter(str.isalpha, cipher_text))

    # Count the frequency of each letter
    letter_frequency = Counter(filtered_text)
    total_letters = sum(letter_frequency.values())

    # Normalize to get percentages and sort by frequency in descending order
    sorted_letter_frequency = {letter: (count / total_letters) * 100 for letter, count in letter_frequency.items()}
    sorted_letter_frequency = dict(sorted(sorted_letter_frequency.items(), key=lambda item: item[1], reverse=True))

    return sorted_letter_frequency


def decipher_text(cipher_text: str, decrypt_key: list[str] | dict = None, letter_freq: dict[str] | str = None) -> str:
    # Deciphers a given text using a specified decryption key or a dictionary-based key.
    if isinstance(decrypt_key, list) and letter_freq is not None:
        # Create indices based on the frequency of letters as specified in letter_freq
        indices = [string.ascii_lowercase.index(letter) for letter in letter_freq]
        # Create a translation dictionary using the indices and decryption key
        translation_dict = {key_letter: string.ascii_lowercase[idx] for key_letter, idx in zip(decrypt_key, indices)}
    elif isinstance(decrypt_key, dict):
        # Use the provided dictionary as the translation dictionary
        translation_dict = decrypt_key
    else:
        # Return the original text if no valid key or dictionary is provided
        return cipher_text
    
    # Translate the text using the translation dictionary
    return "".join([translation_dict[char] if char in translation_dict else char for char in cipher_text])


def count_key_acc(key: list[str], actual_key: list[str], actual_letters_freq: list[str]):
    # Calculates the accuracy of a deciphered key against the actual key and generates a correction mapping.
    positive = 0 # Counter for correctly mapped letters
    correction = {} # Dictionary to store incorrect mappings

    for idx, letter in enumerate(key):
        # Check if the deciphered letter matches the actual key letter at the same position
        if actual_key[letter] == actual_letters_freq[idx]:
            positive += 1
        else:
            correction[letter] = actual_key[letter] # Record the correct mapping for incorrect letters

    acc = positive / len(string.ascii_lowercase)
    return acc, correction

def count_text_decryption_acc(key: list[str], letter_freq: dict[str] | str, ciphered_text: str, plain_text: str):
    # Calculates the accuracy of a deciphered text.
    deciphered_text = decipher_text(ciphered_text, key, letter_freq)
    white_spaces_clean_plain_text = "".join([char.lower() for char in plain_text if char in string.ascii_letters])
    
    positive = 0 # Counter for correctly mapped letters
    for idx in range(len(deciphered_text)):
        if deciphered_text[idx] == white_spaces_clean_plain_text[idx]:
            positive += 1
    
    return positive / len(white_spaces_clean_plain_text)