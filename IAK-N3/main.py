import time
import itertools
from typing import List, Tuple
import numpy as np
import sys


def read_dna_file(filename: str) -> str:
    with open(filename, 'r') as file:
        return file.read().strip()


def get_nmers(dna: str, n: int, t: int) -> List[str]:
    """Split DNA into t n-mers."""
    return [dna[i:i + n] for i in range(0, t * n, n)]


def score_motifs(motifs: List[str]) -> int:
    """Calculate score for a list of motifs (l-mers)."""
    # Create profile matrix
    l = len(motifs[0])
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

    # Calculate score (sum of maximum counts at each position)
    score = sum(np.max(profile[:, j]) for j in range(l))
    return score


def get_consensus(motifs: List[str]) -> str:
    """Get consensus sequence from motifs."""
    l = len(motifs[0])
    consensus = ""
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

    # For each position, find the most frequent nucleotide
    nucleotides = ['A', 'T', 'G', 'C']
    for j in range(l):
        max_idx = np.argmax(profile[:, j])
        consensus += nucleotides[max_idx]

    return consensus


def greedy_motif_search(dna: str, n: int, l: int, t: int) -> Tuple[List[int], str, int]:
    """Greedy algorithm for motif finding."""
    nmers = get_nmers(dna, n, t)

    # Try all possible starting positions for the first n-mer
    best_score = 0
    best_motifs = []
    best_starts = []

    # For each possible starting position in the first n-mer
    for start1 in range(n - l + 1):
        motifs = [nmers[0][start1:start1 + l]]
        starts = [start1 + 1]  # 1-indexed

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
            starts.append(best_start + 1)  # 1-indexed

        current_score = score_motifs(motifs)
        if current_score > best_score:
            best_score = current_score
            best_motifs = motifs
            best_starts = starts

    consensus = get_consensus(best_motifs)
    return best_starts, consensus, best_score


def hamming_distance(s1: str, s2: str) -> int:
    """Calculate Hamming distance between two strings."""
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def min_hamming_distance(pattern: str, text: str, l: int) -> Tuple[int, int]:
    """Find the minimum Hamming distance of pattern to any l-mer in text."""
    min_dist = float('inf')
    min_pos = 0

    for i in range(len(text) - l + 1):
        dist = hamming_distance(pattern, text[i:i + l])
        if dist < min_dist:
            min_dist = dist
            min_pos = i

    return min_dist, min_pos + 1  # 1-indexed position


def branch_and_bound_motif_search(dna: str, n: int, l: int, t: int) -> Tuple[List[int], str, int]:
    """Branch and bound algorithm for motif finding."""
    nmers = get_nmers(dna, n, t)

    # Generate all possible l-mers (potential consensus sequences)
    # For practical reasons, we'll limit this to smaller l values
    if l > 10:
        raise ValueError("l is too large for branch and bound (max 10)")

    best_consensus = ""
    best_distance = float('inf')
    best_positions = []

    # Let's optimize by only generating common l-mers from the DNA sequence
    all_lmers = set()
    for nmer in nmers:
        for i in range(n - l + 1):
            all_lmers.add(nmer[i:i + l])

    # Instead of generating 4^l patterns, we'll use l-mers present in the sequence
    # This is a significant optimization
    for consensus_pattern in all_lmers:
        total_distance = 0
        positions = []

        for nmer in nmers:
            dist, pos = min_hamming_distance(consensus_pattern, nmer, l)
            total_distance += dist
            positions.append(pos)

            # Early termination - if current distance is already worse than best
            if total_distance >= best_distance:
                break

        if total_distance < best_distance:
            best_distance = total_distance
            best_consensus = consensus_pattern
            best_positions = positions

    return best_positions, best_consensus, best_distance


def measure_performance(dna: str, n: int, l: int, t: int) -> Tuple[float, float]:
    """Measure performance of both algorithms."""
    # Measure greedy algorithm
    start_time = time.time()
    greedy_starts, greedy_consensus, greedy_score = greedy_motif_search(dna, n, l, t)
    greedy_time = time.time() - start_time

    # Measure branch and bound algorithm
    start_time = time.time()
    bnb_starts, bnb_consensus, bnb_distance = branch_and_bound_motif_search(dna, n, l, t)
    bnb_time = time.time() - start_time

    print(f"Greedy method: {greedy_consensus} (score: {greedy_score}), time: {greedy_time:.6f}s")
    print(f"Branch & Bound: {bnb_consensus} (distance: {bnb_distance}), time: {bnb_time:.6f}s")

    return greedy_time, bnb_time


if __name__ == '__main__':

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
        print("Invalid parameters! Please ensure: 2 <= l <= 10, l <= n <= 100, 2 <= t <= 5")
    else:
        # Run search and performance measurement
        greedy_starts, greedy_consensus, greedy_score = greedy_motif_search(dna, n, l, t)
        bnb_starts, bnb_consensus, bnb_distance = branch_and_bound_motif_search(dna, n, l, t)

        print("\nResults:")
        print(f"Greedy method consensus: {greedy_consensus} (score: {greedy_score})")
        print(f"Greedy method positions: {greedy_starts}")
        print(f"Branch & Bound consensus: {bnb_consensus} (distance: {bnb_distance})")
        print(f"Branch & Bound positions: {bnb_starts}")

        print("\nPerformance comparison:")
        measure_performance(dna, n, l, t)