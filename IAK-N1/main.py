import math
import sys
from itertools import combinations


def preberi_dnk(ime_datoteke):
    with open(ime_datoteke, "r") as f:
        return f.read().strip()


def poisci_reze(dnk_zaporedje, encim_mesto):
    indeksi = []

    for zaporedje in encim_mesto:
        i = dnk_zaporedje.find(zaporedje)
        while i != -1:
            indeksi.append(i)
            i = dnk_zaporedje.find(zaporedje, i + 1)

    indeksi.sort()
    return indeksi


def izracunaj_razdalje(indeksi, dolzina_dnk):
    vsi_rezi = [0] + indeksi + [dolzina_dnk - 1]
    razdalje = [abs(a - b) for a, b in combinations(vsi_rezi, 2)]
    razdalje.sort()
    return razdalje


def brute_force(L):
    M = L[-1:][0]
    n = int((1 + math.sqrt(1 + 4 * M)) / 2)
    set_L = set(L)
    for subset in combinations(L, n - 2):
        X = {0, *subset, M}
        dX = {abs(a - b) for a, b in combinations(X, 2)}

        if dX == set_L:
            return X

    print("  Rešitev ne obstaja.")


if __name__ == "__main__":
    # print("Podaj ime datoteke z DNK zaporedjem: ")
    # ime_datoteke = input()
    #
    # print("Podaj zaporedja, ki jih iščemo: ")
    # mesto = input().split(", ")

    # Branje DNK datoteke
    dnk_zaporedje = preberi_dnk("DNK1.txt")

    # Iskanje rezov in računanje razdalj
    mesto = ["AAAA", "CCCC", "TTTT", "GGGG"]

    rezultati = poisci_reze(dnk_zaporedje, mesto)

    if rezultati:
        print(f"  Položaji rezov: {rezultati}")
        # Izračunamo razdalje in zgradimo multimnožico
        multimnozica_razdalj = izracunaj_razdalje(rezultati, len(dnk_zaporedje))
        print(f"  Multimnožica razdalj: {multimnozica_razdalj}")
    else:
        print("  Encim ne reže v tej DNK sekvenci.")

    #  multimnozica_razdalj {1,3,7,8,9,11,14,15,17,21}
    # multimnozica_razdalj = [1, 3, 7, 8, 9, 11, 14, 15, 17, 21]

    resitev = brute_force(multimnozica_razdalj)
    print("  Rešitev: ", resitev)
