import time
from typing import List, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return damerau_levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    d = {}
    len1, len2 = len(s1), len(s2)
    
    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1
    
    for i in range(len1):
        for j in range(len2):
            if s1[i] == s2[j]:
                d[(i, j)] = d[(i-1, j-1)]
            else:
                d[(i, j)] = min(
                    d[(i-1, j)] + 1,    # deletion
                    d[(i, j-1)] + 1,    # insertion
                    d[(i-1, j-1)] + 1   # substitution
                )
            if (i > 0 and j > 0 and s1[i] == s2[j-1] and s1[i-1] == s2[j]):
                d[(i, j)] = min(d[(i, j)], d[(i-2, j-2)] + 1)  # transposition
    
    return d[(len1-1, len2-1)]


def fuzzy_search(word: str, corpus_text: str, algorithm: str) -> List[Tuple[str, int]]:
    words = corpus_text.split()
    results = []
    
    if algorithm == "levenshtein":
        distance_func = levenshtein_distance
    elif algorithm == "damerau-levenshtein":
        distance_func = damerau_levenshtein_distance
    else:
        raise ValueError("Unsupported algorithm")
    
    for corpus_word in words:
        distance = distance_func(word, corpus_word)
        results.append((corpus_word, distance))
    
    return sorted(results, key=lambda x: x[1])
