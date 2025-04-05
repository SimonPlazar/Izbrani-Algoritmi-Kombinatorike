from typing import List, Tuple, Any
from itertools import product
import numpy as np
import time
import sys


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


def get_consensus(motifs: List[str]) -> List[str]:
    l = len(motifs[0])
    profile = get_profile(motifs, l)
    nucleotides = ['A', 'T', 'G', 'C']

    # Store all possible nucleotides at each position
    position_options = []
    for j in range(l):
        col = profile[:, j]
        max_count = np.max(col)
        # Find all nucleotides with the max count
        max_indices = np.where(col == max_count)[0]
        position_options.append([nucleotides[idx] for idx in max_indices])

    # Generate all possible consensus sequences
    def generate_all_consensus(pos, current):
        if pos == l:
            return [current]

        results = []
        for nucleotide in position_options[pos]:
            results.extend(generate_all_consensus(pos + 1, current + nucleotide))
        return results

    return generate_all_consensus(0, "")


def greedy_motif_search(dna: str, n: int, l: int, t: int) -> tuple[list[tuple[list[int], str, int]], int]:
    nmers = get_nmers(dna, n, t)
    best_score = 0
    optimal_solutions = []

    # For each starting position in first n-mer
    for start1 in range(n - l + 1):
        motifs = [nmers[0][start1:start1 + l]]
        starts = [start1 + 1]  # 1-indexed

        # For each remaining n-mer
        for i in range(1, t):
            best_motif_score = -1
            best_motifs = []
            best_starts = []

            for start in range(n - l + 1):
                current_motif = nmers[i][start:start + l]
                current_motifs = motifs + [current_motif]
                current_score = score_motifs(current_motifs)

                if current_score > best_motif_score:
                    best_motif_score = current_score
                    best_motifs = [current_motif]
                    best_starts = [start]
                elif current_score == best_motif_score:
                    best_motifs.append(current_motif)
                    best_starts.append(start)

            # Add all tied best motifs to the queue
            motifs.append(best_motifs[0])  # Use first for simplicity
            starts.append(best_starts[0] + 1)  # 1-indexed

        current_score = score_motifs(motifs)
        consensus_list = get_consensus(motifs)

        if current_score > best_score:
            best_score = current_score
            optimal_solutions = [(starts, consensus, current_score) for consensus in consensus_list]
        elif current_score == best_score:
            for consensus in consensus_list:
                optimal_solutions.append((starts, consensus, current_score))

    return optimal_solutions, best_score


def hamming_distance(s1: str, s2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def min_hamming_distance(pattern: str, text: str, l: int) -> Tuple[int, List[int]]:
    min_dist = float('inf')
    min_positions = []

    for i in range(len(text) - l + 1):
        dist = hamming_distance(pattern, text[i:i + l])

        if dist < min_dist:
            min_dist = dist
            min_positions = [i + 1]  # 1-indexed position
        elif dist == min_dist:
            min_positions.append(i + 1)  # 1-indexed position

    return min_dist, min_positions


def branch_and_bound_motif_search(dna: str, n: int, l: int, t: int) -> tuple[
    list[tuple[list[Any], str, int]], float | int]:
    nmers = get_nmers(dna, n, t)
    best_distance = float('inf')
    optimal_solutions = []

    # Generate all possible l-mers
    all_lmers = set()
    # for nmer in nmers:
    #     for i in range(n - l + 1):
    #         all_lmers.add(nmer[i:i + l])

    # for i in range(n*t - l + 1):
    # for i in range(len(dna) - l + 1):
    #     all_lmers.add(dna[i:i + l])

    # Generate all possible l-mers
    nucleotides = ['A', 'T', 'G', 'C']
    all_lmers = set(''.join(p) for p in product(nucleotides, repeat=l))

    for consensus_pattern in all_lmers:
        # For each potential position combination
        position_options = []
        total_distances = []

        # Get all minimum distance positions for each nmer
        for nmer in nmers:
            dist, positions = min_hamming_distance(consensus_pattern, nmer, l)
            position_options.append(positions)
            total_distances.append(dist)

            # if sum already exceeds best, no need to continue
            if sum(total_distances) > best_distance:
                break

        if len(position_options) == t:
            total_distance = sum(total_distances)

            # Generate all possible position combinations
            for pos_combination in product(*position_options):
                if total_distance < best_distance:
                    best_distance = total_distance
                    optimal_solutions = [(list(pos_combination), consensus_pattern, total_distance)]
                elif total_distance == best_distance:
                    optimal_solutions.append((list(pos_combination), consensus_pattern, total_distance))

    return optimal_solutions, best_distance


def measure_performance(dna: str):
    filename = "performance_results.txt"

    for l in range(2, 11):
        for n in range(l, 101):
            for t in range(2, 6):
                print(f"\nTesting with l={l}, n={n}, t={t}")
                # Measure greedy algorithm
                start_time = time.time()
                greedy_motif_search(dna, n, l, t)
                greedy_time = time.time() - start_time
                print(f"Greedy Motif Search Time: {greedy_time:.4f} seconds")

                # Measure branch and bound algorithm
                start_time = time.time()
                branch_and_bound_motif_search(dna, n, l, t)
                bnb_time = time.time() - start_time
                print(f"B&B Motif Search Time: {bnb_time:.4f} seconds")

                # write to text file
                with open(filename, 'a') as file:
                    file.write(f"l={l}, n={n}, t={t}, Greedy Time: {greedy_time:.4f} seconds, "
                               f"B&B Time: {bnb_time:.4f} seconds\n")


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
        greedy_solutions, actual_greedy_score = greedy_motif_search(dna, n, l, t)
        bnb_solutions, actual_bnb_distance = branch_and_bound_motif_search(dna, n, l, t)

        # Check if expected solutions are found
        greedy_found = any(consensus == greedy_expected and score == greedy_score
                           for _, consensus, score in greedy_solutions)
        bnb_found = any(consensus == bnb_expected and distance == bnb_distance
                        for _, consensus, distance in bnb_solutions)

        greedy_status = "✓" if greedy_found else "✗"
        bnb_status = "✓" if bnb_found else "✗"

        print(f"{l:^3} {n:^3} {t:^3} {greedy_expected + '(' + str(greedy_score) + ')':^15} {greedy_status:^7} "
              f"{bnb_expected + '(' + str(bnb_distance) + ')':^15} {bnb_status:^7}")

        if not greedy_found:
            print(f"  Greedy found instead: {[f'{c}({s})' for _, c, s in greedy_solutions]}")
        if not bnb_found:
            print(f"  B&B found instead: {[f'{c}({d})' for _, c, d in bnb_solutions]}")

    print("=" * 70)


if __name__ == '__main__':

    filename = "DNK1.txt"

    # verify_solutions(read_dna_file(filename))
    # exit(1)

    measure_performance(read_dna_file(filename))
    exit(1)

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
        ValueError("Invalid parameters! Please ensure: 2 <= l <= 10, l <= n <= 100, 2 <= t <= 5")

    # Run search and performance measurement
    print("\nGreedy Motif Search:")
    greedy_results, greedy_score = greedy_motif_search(dna, n, l, t)
    for starts, consensus, score in greedy_results:
        print(f"Starts: {starts}, Consensus: {consensus}, Score: {score}")
    print("\nBranch and Bound Motif Search:")
    bnb_results, bnb_distance = branch_and_bound_motif_search(dna, n, l, t)
    for starts, consensus, distance in bnb_results:
        print(f"Starts: {starts}, Consensus: {consensus}, Distance: {distance}")
