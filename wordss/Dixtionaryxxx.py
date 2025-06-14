import nltk
nltk.download('words')
from nltk.corpus import words

english_words = set(words.words())
print("apple" in english_words)  # True
