import math
import sys
from itertools import combinations, product
from multiprocessing import Pool
import time


def preberi_dnk(filename):
    with open(filename, "r") as f:
        return f.read().strip()


def poisci_reze(dnk_SEQ, encim_mesto):
    indeksi = []

    for zaporedje in encim_mesto:
        i = dnk_SEQ.find(zaporedje)
        while i != -1:
            indeksi.append(i)
            i = dnk_SEQ.find(zaporedje, i + 1)

    indeksi.sort()
    return indeksi


def izracunaj_razdalje(indeksi, dolzina_dnk):
    vsi_rezi = [0] + indeksi + [dolzina_dnk - 1]
    razdalje = [abs(a - b) for a, b in combinations(vsi_rezi, 2)]
    razdalje.sort()
    return razdalje


def brute_force(L):
    M = L[-1:][0]
    n = int((1 + math.sqrt(1 + 8 * len(L))) / 2)
    set_L = set(L)

    resitve = set()

    for subset in combinations(L, n - 2):
        # if len(subset) > n-2: continue
        X = {0, *subset, M}
        dX = {abs(a - b) for a, b in combinations(X, 2)}

        if dX == set_L:
            resitve.add(frozenset(X))
            # if len(resitve) > 1: return resitve

    return resitve


def process_subset(subset, M, set_L):
    X = {0, *subset, M}
    dX = {abs(a - b) for a, b in combinations(X, 2)}

    if dX == set_L:
        return frozenset(X)
    return None


def brute_force_multi(L):
    M = L[-1:][0]
    n = int((1 + math.sqrt(1 + 8 * len(L))) / 2)
    set_L = set(L)

    subsets = combinations(L, n - 2)
    with Pool(8) as pool:
        resitve = set(pool.starmap(process_subset, [(subset, M, set_L) for subset in subsets]))

    return resitve


def partial_digest(L):
    sirina = L[-1]
    L.pop()
    X = {0, sirina}
    rezultat = set()

    def place(l, x):
        if not l or len(l) == 0:
            rezultat.add(frozenset(x))
            return
        y = max(l)

        def checkSubset(delta_values, target_list):
            # Sort both lists first
            delta_values.sort()
            target_list.sort()

            i, j = 0, 0  # Indexes for delta_values and target_list

            while i < len(delta_values) and j < len(target_list):
                if delta_values[i] == target_list[j]:
                    # Found a match, move both pointers
                    i += 1
                    j += 1
                elif delta_values[i] < target_list[j]:
                    # Current delta value isn't in target list
                    return False
                else:  # delta_values[i] > target_list[j]
                    # Skip this target element and check next one
                    j += 1

            # If we've gone through all delta values, it's a subset
            return i == len(delta_values)

        dyX = [abs(y - xi) for xi in x]
        if checkSubset(dyX, l):
            x.add(y)
            for z in dyX: l.remove(z)
            place(l, x)
            x.remove(y)
            for z in dyX: l.append(z)

        dyX = [abs((sirina - y) - xi) for xi in x]
        if checkSubset(dyX, l):
            x.add(sirina - y)
            for z in dyX: l.remove(z)
            place(l, x)
            x.remove(sirina - y)
            for z in dyX: l.append(z)

    place(L, X)
    return rezultat


# Function to generate all combinations and log/save the results
def poisci_reze_and_log(dnk_seq, filename="results.txt"):
    # Define the set of letters
    letters = ['A', 'C', 'T', 'G']

    # Open the file to write results
    with open(filename, "w") as file:
        # Generate all combinations with length from 1 to 6
        for length in range(1, 7):
            for comb in product(letters, repeat=length):
                comb_str = ''.join(comb)  # Convert tuple to string
                result = len(poisci_reze(dnk_seq, [comb_str]))

                # Log the output number to the file
                file.write(f"Combination: {comb_str}, Result: {result}\n")

                # Optional: Also print to console
                print(f"Combination: {comb_str}, Result: {result}")

    print(f"Results saved to {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Podaj ime datoteke z DNK zaporedjem: ")
        ime_datoteke = input()

        print("Podaj zaporedja, ki jih iščemo: ")
        mesto = input().split(", ")
    else:
        ime_datoteke = sys.argv[1]
        mesto = sys.argv[2:]

    print("Datoteka: ", ime_datoteke)
    print("Mesta rezov: ", mesto)

    # ime_datoteke = "DNK3.txt"

    # Branje DNK datoteke
    dnk_zaporedje = preberi_dnk(ime_datoteke)

    # poisci_reze_and_log(dnk_zaporedje, "rezi_DNK1.txt")
    # exit(0)

    # Iskanje rezov in računanje razdalj
    # mesto = ["GTGTG"]
    # mesto = ["TTCC", "CTCTCT"]
    # mesto = ["AAAA", "CCCC", "TTTT", "GGGG"]
    # mesto = ["ACTACT", "GGAGGA", "GAGGCC", "CTCTCT"]
    # mesto = ["TTTTTTT", "GTGTCGT", "ACACACA"]
    # mesto = ["ACCCC"]

    rezultati = poisci_reze(dnk_zaporedje, mesto)

    if not rezultati:
        print("Encim ne reže v tej DNK sekvenci.")

    print(f"Položaji rezov: {rezultati}")

    # Izračunamo razdalje in zgradimo multimnožico
    multimnozica_razdalj = izracunaj_razdalje(rezultati, len(dnk_zaporedje))
    print(f"Multimnožica razdalj: {multimnozica_razdalj}")

    # multimnozica_razdalj = [1, 3, 7, 8, 9, 11, 14, 15, 17, 21]
    # multimnozica_razdalj = [2, 2, 3, 3, 4, 5, 6, 7, 8, 10]

    # Reševanje problema
    # resitev = brute_force(multimnozica_razdalj)
    # resitev = brute_force_multi(multimnozica_razdalj)
    resitev = partial_digest(multimnozica_razdalj)

    # Timing
    # repeat = 1000
    # sum = 0
    # for _ in range(repeat):
    #     start = time.time()
    #     resitev = partial_digest(multimnozica_razdalj.copy())
    #     # resitev = brute_force(multimnozica_razdalj.copy())
    #     end = time.time()
    #     sum += (end - start) * 1_000_000  # Convert to microseconds
    #
    # diff = sum / repeat
    # print(f"Zaporedje: {ime_datoteke}, Mesto reza: {mesto}, Čas izvajanja: {diff:.2f} µs")

    print("Rešitev: ")
    for r in resitev: print("  ", sorted(r))

    # Output to file
    # with open("output.txt", "w") as file:
    # file.write(f"Zaporedje: {ime_datoteke}, Mesto reza: {mesto}, Čas izvajanja: {diff:.2f} s\n")
    # for r in resitev: file.write(f"  {sorted(r)}\n")
