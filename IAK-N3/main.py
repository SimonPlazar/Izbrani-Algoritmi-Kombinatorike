import time
from typing import List, Tuple, Any
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


def recursive_greedy_motif_search(dna: str, n: int, l: int, t: int) -> Tuple[List[int], str, int]:
    nmers = get_nmers(dna, n, t)
    best_score = 0
    best_motifs = []
    best_positions = []

    expected_combinations = (n - l + 1) ** t
    combinations_explored = 0

    def explore_combinations(index, current_motifs, current_positions):
        nonlocal best_score, best_motifs, best_positions, combinations_explored

        if index == t:
            combinations_explored += 1
            current_score = score_motifs(current_motifs)

            # if combinations_explored % 1000 == 0:
            #     print(f"Explored {combinations_explored}/{expected_combinations} combinations")

            if current_score > best_score:
                best_score = current_score
                best_motifs = current_motifs.copy()
                best_positions = current_positions.copy()
            return

        for start in range(n - l + 1):
            motif = nmers[index][start:start + l]
            explore_combinations(
                index + 1,
                current_motifs + [motif],
                current_positions + [start + 1] # 1-indexed
            )

    # Start recursive exploration
    explore_combinations(0, [], [])

    # print(f"Explored {combinations_explored}/{expected_combinations} combinations")
    if combinations_explored != expected_combinations:
        print("Warning: Not all combinations were explored!")

    consensus = get_consensus(best_motifs)
    return best_positions, consensus, best_score

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

    return min_dist, min_pos + 1  # 1-indexed


def branch_and_bound_motif_search(dna: str, n: int, l: int, t: int) -> tuple[list[Any], str, float]:
    nmers = get_nmers(dna, n, t)
    nucleotides = ['A', 'C', 'G', 'T']

    best_consensus = ""
    best_distance = float('inf')
    best_positions = []

    def calculate_partial_distance(partial_pattern):
        total_distance = 0
        positions = []

        for nmer in nmers:
            min_dist, pos = min_hamming_distance(partial_pattern, nmer, len(partial_pattern))
            total_distance += min_dist
            positions.append(pos)

            if total_distance >= best_distance:
                break

        return total_distance, positions

    def dfs(partial_consensus):
        nonlocal best_consensus, best_distance, best_positions

        current_distance, current_positions = calculate_partial_distance(partial_consensus)

        if current_distance >= best_distance:
            return

        if len(partial_consensus) == l:
            best_distance = current_distance
            best_consensus = partial_consensus
            best_positions = current_positions
            return

        for nucleotide in nucleotides:
            dfs(partial_consensus + nucleotide)

    dfs("")

    return best_positions, best_consensus, best_distance


import concurrent.futures

def measure_performance(dna: str):
    filename = "performance_results.txt"

    for t in range(2, 6):
        for l in range(2, 11):
            for n in range(10, 101, 10):
                print(f"\nTesting with l={l}, n={n}, t={t}")

                # Measure greedy algorithm with timeout
                greedy_time = None
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(recursive_greedy_motif_search, dna, n, l, t)
                    try:
                        start_time = time.time()
                        future.result(timeout=10)  # 10 second timeout
                        greedy_time = time.time() - start_time
                        print(f"Greedy Motif Search Time: {greedy_time:.4f} seconds")
                    except concurrent.futures.TimeoutError:
                        print(f"Greedy algorithm aborted - exceeded 10 seconds")

                # Measure branch and bound algorithm with timeout
                bnb_time = None
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(branch_and_bound_motif_search, dna, n, l, t)
                    try:
                        start_time = time.time()
                        future.result(timeout=10)  # 10 second timeout
                        bnb_time = time.time() - start_time
                        print(f"B&B Motif Search Time: {bnb_time:.4f} seconds")
                    except concurrent.futures.TimeoutError:
                        print(f"B&B algorithm aborted - exceeded 10 seconds")

                # Write to text file
                with open(filename, 'a') as file:
                    # file.write(f"l={l}, n={n}, t={t}, Greedy Time: {greedy_time} seconds, "
                    #            f"B&B Time: {bnb_time} seconds\n")
                    file.write(f"l={l}, n={n}, t={t}, ")
                    if greedy_time is not None:
                        file.write(f"Greedy Time: {greedy_time:.4f} seconds, ")
                    else:
                        file.write("Greedy Time: DNF, ")
                    if bnb_time is not None:
                        file.write(f"B&B Time: {bnb_time:.4f} seconds\n")
                    else:
                        file.write("B&B Time: DNF\n")

def create_expected_solutions_table():
    # Format: (l, n, t, greedy_solution, greedy_score, bnb_solution, bnb_distance)
    return [
        (3, 10, 2, "CAA", 5, "AGC", 1),
        (5, 15, 2, "CAAAT", 10, "CAAAT", 0),
        (7, 20, 2, "CAAATGA", 12, "CAAATGA", 2),
        (3, 10, 3, "CAA", 8, "CAA", 1),
        (5, 15, 3, "CAAAT", 13, "AAATG", 2),
        (7, 15, 3, "CAAATGA", 16, "AGATGTC", 5),
        (7, 20, 3, "CAAATGC", 18, "CAAATGC", 3),
        (3, 10, 4, "CAA", 10, "CAA", 2),
        (5, 15, 4, "CAAAT", 17, "AAATG", 3),
        (7, 15, 4, "CAAATGC", 22, "CAAATGC", 6),
        (7, 20, 4, "TTCCAAG", 23, "TTCCAAG", 5),
        (3, 10, 5, "CAA", 12, "CAA", 3),
        (5, 15, 5, "CAAAT", 20, "AAATG", 5),
    ]


def verify_solutions(dna):
    table = create_expected_solutions_table()
    print("\nVerifying solutions against reference table:")
    print("=" * 70)
    print(f"{'l':^3} {'n':^3} {'t':^3} {'Expected Greedy':^15} {'Found?':^7} {'Expected B&B':^15} {'Found?':^7}")
    print("-" * 70)

    for l, n, t, greedy_expected, greedy_score, bnb_expected, bnb_distance in table:
        # Run algorithms
        greedy_solutions, greedy_consensus, greedy_score = recursive_greedy_motif_search(dna, n, l, t)
        bnb_solutions, bnb_consensus, bnb_scores = branch_and_bound_motif_search(dna, n, l, t)

        # Check if expected solutions are found
        greedy_found = greedy_expected == greedy_consensus and greedy_score == greedy_score
        bnb_found = bnb_expected == bnb_consensus and bnb_scores == bnb_scores

        greedy_status = "✓" if greedy_found else "✗"
        bnb_status = "✓" if bnb_found else "✗"

        print(f"{l:^3} {n:^3} {t:^3} {greedy_expected + '(' + str(greedy_score) + ')':^15} {greedy_status:^7} "
              f"{bnb_expected + '(' + str(bnb_distance) + ')':^15} {bnb_status:^7}")

        if not greedy_found:
            print(f"  Greedy found instead: {greedy_consensus}, score: {greedy_score}")
        if not bnb_found:
            print(f"  B&B found instead: {bnb_consensus}, distance: {bnb_scores}")

    print("=" * 70)

if __name__ == '__main__':
    filename = "DNK1.txt"

    measure_performance(read_dna_file(filename))
    exit(0)

    # verify_solutions(read_dna_file(filename))
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
    # greedy_starts, greedy_consensus, greedy_score = greedy_motif_search(dna, n, l, t)
    greedy_starts, greedy_consensus, greedy_score = recursive_greedy_motif_search(dna, n, l, t)
    bnb_starts, bnb_consensus, bnb_distance = branch_and_bound_motif_search(dna, n, l, t)

    print("\nResults:")
    # print(f"Greedy method consensus: {greedy_consensus} (score: {greedy_score})")
    # print(f"Greedy method positions: {greedy_starts}")
    print(f"Branch & Bound consensus: {bnb_consensus} (distance: {bnb_distance})")
    print(f"Branch & Bound positions: {bnb_starts}")
