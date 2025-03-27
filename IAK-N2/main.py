import sys
import numpy as np
import random


def readFileData(filename_string):
    with open(filename_string, 'r') as file:
        data = file.readlines()

    return [int(x.strip()) for x in data]


def simpleReversalSort(data):
    for i in range(len(data) - 1):
        j = np.argmin(data[i:]) + i
        if j != i:
            # data = data[:i] + data[i:j + 1][::-1] + data[j + 1:]
            data[i:j + 1] = reversed(data[i:j + 1])
            print(data)
        if all(data[i] == i + 1 for i in range(len(data))):
            return data


def getBreakpoints(data):
    breakpoints = []
    for i in range(len(data) - 1):
        if abs(data[i] - data[i + 1]) != 1:
            breakpoints.append(i)

    return breakpoints


def find_ordered_strips(data, breakpoints):
    ascending_strips = []
    descending_strips = []
    single_item_strips = []

    if not breakpoints.__contains__(0):
        breakpoints = [0] + breakpoints
    if not breakpoints.__contains__(len(data) - 1):
        breakpoints = breakpoints + [len(data) - 1]
    # breakpoints = [0] + breakpoints + [len(data) - 1]

    for i in range(len(breakpoints)-1):
        start, end = breakpoints[i], breakpoints[i + 1]
        if end - start > 1:  # Multiple elements in the strip
            strip = data[start + 1:end + 1]  # Elements in the strip

            # Check if strip is in ascending order
            if all(strip[j] < strip[j + 1] for j in range(len(strip) - 1)):
                ascending_strips.append([start + 1, end])

            # Check if strip is in descending order
            elif all(strip[j] > strip[j + 1] for j in range(len(strip) - 1)):
                descending_strips.append([start + 1, end])
        else:
            single_item_strips.append([start + 1, end])
            # ascending_strips.append([start + 1, end])

    return ascending_strips, descending_strips, single_item_strips


def improvedBreakpointReversalSort(data):
    # data = [6, 9, 8, 1, 4, 7, 3, 2, 5]
    # data = [0, 13, 2, 17, 1, 3, 20, 19, 11, 12, 4, 5, 16, 15, 10, 18, 14, 8, 7, 6, 9, 21]
    # print(data)

    while True:
        # get breakpoints
        breakpoints = getBreakpoints(data)
        # print("Breakpoints:", len(breakpoints), breakpoints)
        print("Breakpoints:", len(breakpoints))

        if not breakpoints:
            return data

        ascending_strips, descending_strips, single_item_strips = find_ordered_strips(data, breakpoints)
        # print("Descending Strips:", descending_strips)
        # print("Ascending Strips:", ascending_strips)

        if not descending_strips:
            if not ascending_strips:
                print("No Ascending or Descending Strips")
                return data
                # data[0:breakpoints[0]] = list(reversed(data[0: breakpoints[0]]))
                # continue
            # data[ascending_strips[0][0]:ascending_strips[0][1] + 1] = list(
            # reversed(data[ascending_strips[0][0]:ascending_strips[0][1] + 1]))
            # valid_strips = [strip for strip in ascending_strips
            #                 if strip[0] != strip[1]]
            # random_strip = random.choice(ascending_strips)
            # random_strip = random.choice(valid_strips)
            # random_strip = random.choice(ascending_strips)
            random_strip = ascending_strips[0]
            data[random_strip[0]:random_strip[1] + 1] = list(
                reversed(data[random_strip[0]:random_strip[1] + 1]))

            continue

        # Get the smallest element of all strips
        # smallest_element = min(data[strip[1]] for strip in descending_strips)
        smallest_element = data[descending_strips[0][1]]
        strip = descending_strips[0]
        for x in range(1, len(descending_strips)):
            if data[descending_strips[x][1]] < smallest_element:
                smallest_element = data[descending_strips[x][1]]
                strip = descending_strips[x]

        # print("Smallest Element:", smallest_element)
        # print("Smallest Element ix:", strip[1])
        # print("Strip:", strip)

        # find the element smallest_element-1 in the data
        # index = data.index(smallest_element - 1)
        index = -1
        for asc_strip in ascending_strips+single_item_strips:
            if data[asc_strip[1]] == smallest_element - 1:
                index = asc_strip[1]
                break
        print("Index of smallest_element-1:", index)

        # splice the data
        # data[strip[0]:strip[1] + 1] = list(reversed(data[strip[0]:strip[1] + 1]))
        # data = data[:index] + data[strip[0]:strip[1] + 1] + data[index + 1:strip[0]] + data[strip[1] + 1:]

        # Reverse the strip first
        # data[strip[0]:strip[1] + 1] = list(reversed(data[strip[0]:strip[1] + 1]))

        # Handle splicing based on index position
        if index == -1:
            # Move the reversed strip to the beginning
            # data = data[strip[0]:strip[1] + 1] + data[:strip[0]] + data[strip[1] + 1:]
            data[0:strip[1] + 1] = list(reversed(data[0:strip[1] + 1]))
        elif index < strip[0]:
            # Index is before the strip
            # data = data[:index + 1] + data[strip[0]:strip[1] + 1] + data[index + 1:strip[0]] + data[strip[1] + 1:]
            data[index+1:strip[1]+1] = list(reversed(data[index+1:strip[1]+1]))
        elif index > strip[1]:
            # Index is after the strip
            # data = data[:strip[0]] + data[strip[1] + 1:index + 1] + data[strip[0]:strip[1] + 1] + data[index + 1:]
            data[strip[1]+1:index+1] = list(reversed(data[strip[1]+1:index+1]))
        else:
            # Index is within the strip
            pass

        # print("Reordered Data:", data)


if __name__ == '__main__':
    filename = ""

    filename = "G2.txt"

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    readData = readFileData(filename)
    # print("Data:\n", readData)

    # simpleReverseData = simpleReversalSort(readData)
    # print("Simple Reversal Sort:\n", simpleReverseData)

    breakpointData = improvedBreakpointReversalSort(readData)
    print("Improved Breakpoint Reversal Sort:\n", breakpointData)
