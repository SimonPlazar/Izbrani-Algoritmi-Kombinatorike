import time
from typing import List, Tuple
import numpy as np
import sys
from itertools import product


def read_dna_file(filename: str) -> str:
    with open(filename, 'r') as file:
        return file.read().strip()


def get_nmers(dna: str, n: int, t: int) -> List[str]:
    return [dna[i:i + n] for i in range(0, t * n, n)]


def get_profile(motifs: List[str], l: int) -> np.ndarray:
    profile = np.zeros((4, l))

    # Count nucleotides at each position
    for motif in motifs:
        for i, nucleotide in enumerate(motif):
            if nucleotide == 'A':
                profile[0, i] += 1
            elif nucleotide == 'T':
                profile[1, i] += 1
            elif nucleotide == 'G':
                profile[2, i] += 1
            elif nucleotide == 'C':
                profile[3, i] += 1

    return profile


def score_motifs(motifs: List[str]) -> int:
    # Create profile matrix
    l = len(motifs[0])
    profile = get_profile(motifs, l)

    # Calculate score (sum of maximum counts at each position)
    score = sum(np.max(profile[:, j]) for j in range(l))
    return score


def get_consensus(motifs: List[str]) -> str:
    consensus = ""
    l = len(motifs[0])
    profile = get_profile(motifs, l)

    # For each position, find the most frequent nucleotide
    nucleotides = ['A', 'T', 'G', 'C']
    for j in range(l):
        max_idx = np.argmax(profile[:, j])
        consensus += nucleotides[max_idx]

    return consensus


def greedy_motif_search(dna: str, n: int, l: int, t: int) -> Tuple[List[int], str, int]:
    nmers = get_nmers(dna, n, t)

    # Try all possible starting positions for the first n-mer
    best_score = 0
    best_motifs = []
    best_starts = []

    # For each possible starting position in the first n-mer
    for start1 in range(n - l + 1):
        motifs = [nmers[0][start1:start1 + l]]
        starts = [start1 + 1]

        # For each remaining n-mer
        for i in range(1, t):
            # Try all starting positions and find best match for current profile
            best_motif_score = -1
            best_motif = ""
            best_start = 0

            for start in range(n - l + 1):
                current_motif = nmers[i][start:start + l]
                current_motifs = motifs + [current_motif]
                current_score = score_motifs(current_motifs)

                if current_score > best_motif_score:
                    best_motif_score = current_score
                    best_motif = current_motif
                    best_start = start

            motifs.append(best_motif)
            starts.append(best_start + 1)

        current_score = score_motifs(motifs)
        if current_score > best_score:
            best_score = current_score
            best_motifs = motifs
            best_starts = starts

    consensus = get_consensus(best_motifs)
    return best_starts, consensus, best_score


def hamming_distance(s1: str, s2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def min_hamming_distance(pattern: str, text: str, l: int) -> Tuple[int, int]:
    min_dist = float('inf')
    min_pos = 0

    for i in range(len(text) - l + 1):
        dist = hamming_distance(pattern, text[i:i + l])
        if dist < min_dist:
            min_dist = dist
            min_pos = i

    return min_dist, min_pos + 1  # 1-indexed position


def branch_and_bound_motif_search(dna: str, n: int, l: int, t: int) -> Tuple[List[int], str, int]:
    nmers = get_nmers(dna, n, t)

    # Generate all possible l-mers (potential consensus sequences)
    best_consensus = ""
    best_distance = float('inf')
    best_positions = []

    # Let's optimize by only generating common l-mers from the DNA sequence
    all_lmers = set()
    nucleotides = ['A', 'T', 'G', 'C']
    all_lmers = [''.join(p) for p in product(nucleotides, repeat=l)]

    # use l-mers present in the sequence
    for consensus_pattern in all_lmers:
        total_distance = 0
        positions = []

        for nmer in nmers:
            dist, pos = min_hamming_distance(consensus_pattern, nmer, l)
            total_distance += dist
            positions.append(pos)

            # If current distance is already worse than best
            if total_distance >= best_distance:
                break

        if total_distance < best_distance:
            best_distance = total_distance
            best_consensus = consensus_pattern
            best_positions = positions

    return best_positions, best_consensus, best_distance


def measure_performance(dna: str):
    filename = "performance_results_single.txt"
    with open(filename, "w") as file:
        for l in range(2, 11):
            for n in range(l, 101):
                for t in range(2, 6):
                    start_time = time.time()
                    greedy_motif_search(dna, n, l, t)
                    greedy_time = time.time() - start_time

                    start_time = time.time()
                    branch_and_bound_motif_search(dna, n, l, t)
                    bnb_time = time.time() - start_time

                    print(f"l={l}, n={n}, t={t} | Greedy: {greedy_time:.4f}s | BnB: {bnb_time:.4f}s")
                    file.write(f"l={l}, n={n}, t={t} | Greedy: {greedy_time:.4f}s | BnB: {bnb_time:.4f}s\n")


if __name__ == '__main__':
    filename = "DNK1.txt"

    # measure_performance(read_dna_file(filename))
    # exit(0)

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        l = int(sys.argv[2])
        n = int(sys.argv[3])
        t = int(sys.argv[4])
    else:
        filename = input("Enter DNA file path: ")
        l = int(input("Enter l (size of l-mers, 2 <= l <= 10): "))
        n = int(input("Enter n (size of n-mers, l <= n <= 100): "))
        t = int(input("Enter t (number of n-mers, 2 <= t <= 5): "))

    dna = read_dna_file(filename)

    # Validate parameters
    if not (2 <= l <= 10 and l <= n <= 100 and 2 <= t <= 5):
        ValueError("Invalid parameters: 2 <= l <= 10, l <= n <= 100, 2 <= t <= 5")

    # Run search and performance measurement
    greedy_starts, greedy_consensus, greedy_score = greedy_motif_search(dna, n, l, t)
    bnb_starts, bnb_consensus, bnb_distance = branch_and_bound_motif_search(dna, n, l, t)

    print("\nResults:")
    print(f"Greedy method consensus: {greedy_consensus} (score: {greedy_score})")
    print(f"Greedy method positions: {greedy_starts}")
    print(f"Branch & Bound consensus: {bnb_consensus} (distance: {bnb_distance})")
    print(f"Branch & Bound positions: {bnb_starts}")
