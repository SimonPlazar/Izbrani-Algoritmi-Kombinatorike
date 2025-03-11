import math
from itertools import combinations
from multiprocessing import Pool


def preberi_dnk(ime_datoteke):
    with open(ime_datoteke, "r") as f:
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

    return resitve


# brute force but multi-threaded
def brute_force_multi(L):
    M = L[-1:][0]
    n = int((1 + math.sqrt(1 + 8 * len(L))) / 2)
    set_L = set(L)

    def process_subset(subset):
        X = {0, *subset, M}
        dX = {abs(a - b) for a, b in combinations(X, 2)}

        if dX == set_L:
            return frozenset(X)
        return None

    subsets = combinations(L, n - 2)
    with Pool(8) as pool:
        resitve = set(pool.map(process_subset, subsets))

    return resitve


def partial_digest(L):
    sirina = max(L)
    L.pop()
    X = {0, sirina}
    rezultat = set()

    def place(l, x):
        if not l or len(l) == 0:
            rezultat.add(frozenset(x))
            return
        y = max(l)

        dyX = {abs(y - x) for x in x}
        if dyX.issubset(set(l)):
            x.add(y)
            for z in dyX: l.remove(z)
            place(l, x)
            x.remove(y)
            for z in dyX: l.append(z)

        dyX = {abs((sirina - y) - x) for x in x}
        if dyX.issubset(set(l)):
            x.add(sirina - y)
            for z in dyX: l.remove(z)
            place(l, x)
            x.remove(sirina - y)
            for z in dyX: l.append(z)

    place(L, X)
    return rezultat


if __name__ == "__main__":
    # print("Podaj ime datoteke z DNK zaporedjem: ")
    # ime_datoteke = input()
    # dnk_zaporedje = preberi_dnk(ime_datoteke)
    #
    # print("Podaj zaporedja, ki jih iščemo: ")
    # mesto = input().split(", ")

    # Branje DNK datoteke
    dnk_zaporedje = preberi_dnk("DNK1.txt")

    # Iskanje rezov in računanje razdalj
    mesto = ["AAAA", "CCCC", "TTTT", "GGGG"]
    # mesto = ["GTGTG"]
    # mesto = ["TTCC", "CTCTCT"]

    rezultati = poisci_reze(dnk_zaporedje, mesto)

    if not rezultati:
        print("Encim ne reže v tej DNK sekvenci.")

    print(f"Položaji rezov: {rezultati}")
    # Izračunamo razdalje in zgradimo multimnožico
    multimnozica_razdalj = izracunaj_razdalje(rezultati, len(dnk_zaporedje))
    print(f"Multimnožica razdalj: {multimnozica_razdalj}")

    # multimnozica_razdalj = [1, 3, 7, 8, 9, 11, 14, 15, 17, 21]
    # multimnozica_razdalj = [2, 2, 3, 3, 4, 5, 6, 7, 8, 10]

    # resitev = brute_force(multimnozica_razdalj)
    # resitev = partial_digest(multimnozica_razdalj)
    resitev = brute_force_multi(multimnozica_razdalj)

    print("Rešitev: ")
    for r in resitev: print("  ", sorted(r))
