import sys
import numpy as np
import random
import time


def readFileData(filename_string):
    with open(filename_string, 'r') as file:
        data = file.readlines()

    return [int(x.strip()) for x in data]


def simpleReversalSort(data):
    rotations = 0
    for i in range(len(data) - 1):
        rotations += 1
        j = np.argmin(data[i:]) + i
        if j != i:
            # data = data[:i] + data[i:j + 1][::-1] + data[j + 1:]
            data[i:j + 1] = reversed(data[i:j + 1])
            # print(data)
        if all(data[i] == i + 1 for i in range(len(data))):
            print("Rotations made:", rotations)
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

    index_to_strip = {}

    # Ensure we include the beginning and end of the array
    complete_breakpoints = [-1] + breakpoints + [len(data) - 1]

    for i in range(len(complete_breakpoints) - 1):
        start, end = complete_breakpoints[i], complete_breakpoints[i + 1]
        if end - start > 1:  # Multiple elements in the strip
            strip_start = start + 1
            strip_end = end
            strip = data[strip_start:strip_end + 1]  # Elements in the strip

            # Check if strip is in ascending order
            if all(strip[j] < strip[j + 1] for j in range(len(strip) - 1)):
                ascending_strips.append([strip_start, strip_end])
                index_to_strip[strip_start] = [strip_start, strip_end]
                index_to_strip[strip_end] = [strip_start, strip_end]

            # Check if strip is in descending order
            elif all(strip[j] > strip[j + 1] for j in range(len(strip) - 1)):
                descending_strips.append([strip_start, strip_end])
                index_to_strip[strip_start] = [strip_start, strip_end]
                index_to_strip[strip_end] = [strip_start, strip_end]
        else:
            # Single element
            single_item_strips.append([start + 1, end])
            index_to_strip[start + 1] = [start + 1, end]

    return ascending_strips, descending_strips, single_item_strips, index_to_strip


def update_breakpoints(data, breakpoints, start_index, end_index):
    # Remove existing breakpoints in the modified range (keep those outside the range)
    breakpoints = [bp for bp in breakpoints if bp < start_index - 1 or bp > end_index]

    # Check the leftmost boundary (position before the start of reversal)
    if start_index > 0 and abs(data[start_index - 1] - data[start_index]) != 1:
        breakpoints.append(start_index - 1)

    # Check inside the reversed segment
    for i in range(start_index, end_index):
        if abs(data[i] - data[i + 1]) != 1:
            breakpoints.append(i)

    # Check the rightmost boundary
    if end_index < len(data) - 1 and abs(data[end_index] - data[end_index + 1]) != 1:
        breakpoints.append(end_index)

    # Sort breakpoints to maintain order
    return sorted(breakpoints)


def update_ordered_strips(data, ascending_strips, descending_strips, single_item_strips, breakpoints, start_index,
                          end_index):
    # Step 1: Remove strips that overlap with the reversed range
    ascending_strips = [strip for strip in ascending_strips
                        if strip[1] < start_index or strip[0] > end_index]
    descending_strips = [strip for strip in descending_strips
                         if strip[1] < start_index or strip[0] > end_index]
    single_item_strips = [strip for strip in single_item_strips
                          if strip[0] < start_index or strip[0] > end_index]

    # Step 2: Find new strips in the affected area
    # Find breakpoints that define the affected area
    relevant_breakpoints = [bp for bp in breakpoints
                            if bp >= start_index - 1 and bp <= end_index]

    # Add boundary points to ensure we cover the entire affected area
    complete_breakpoints = []

    # Find the breakpoint before start_index
    before_start = max([bp for bp in breakpoints if bp < start_index - 1], default=-1)
    complete_breakpoints.append(before_start)

    # Add all relevant breakpoints in the affected area
    complete_breakpoints.extend(relevant_breakpoints)

    # Find the breakpoint after end_index
    after_end = min([bp for bp in breakpoints if bp > end_index], default=len(data) - 1)
    complete_breakpoints.append(after_end)

    # Step 3: Create new strips from the affected area
    index_to_strip = {}

    for i in range(len(complete_breakpoints) - 1):
        start, end = complete_breakpoints[i], complete_breakpoints[i + 1]
        if end - start > 1:  # Multiple elements in the strip
            strip_start = start + 1
            strip_end = end
            strip = data[strip_start:strip_end + 1]  # Elements in the strip

            # Check if strip is in ascending order
            if all(strip[j] < strip[j + 1] for j in range(len(strip) - 1)):
                ascending_strips.append([strip_start, strip_end])
                index_to_strip[strip_start] = [strip_start, strip_end]
                index_to_strip[strip_end] = [strip_start, strip_end]

            # Check if strip is in descending order
            elif all(strip[j] > strip[j + 1] for j in range(len(strip) - 1)):
                descending_strips.append([strip_start, strip_end])
                index_to_strip[strip_start] = [strip_start, strip_end]
                index_to_strip[strip_end] = [strip_start, strip_end]
        elif start + 1 == end:  # Single element
            single_item_strips.append([start + 1, end])
            index_to_strip[start + 1] = [start + 1, end]

    # Rebuild the complete index_to_strip mapping
    for strip in ascending_strips + descending_strips + single_item_strips:
        index_to_strip[strip[0]] = strip
        if strip[0] != strip[1]:  # Not a single element strip
            index_to_strip[strip[1]] = strip

    return ascending_strips, descending_strips, single_item_strips, index_to_strip


def improvedBreakpointReversalSort(data, heuristic=1):
    rotations = 0
    breakpoints = getBreakpoints(data)  # Initial calculation of all breakpoints
    ascending_strips, descending_strips, single_item_strips, index_to_strip = find_ordered_strips(data, breakpoints)

    while breakpoints:
        # print(len(breakpoints))

        if not descending_strips:
            if not ascending_strips:
                print("No Ascending or Descending Strips")
                return data

            # Choose the last ascending strip
            random_strip = ascending_strips[-1]
            start_idx = random_strip[0]
            end_idx = random_strip[1]

            # Reverse the strip
            data[start_idx:end_idx + 1] = list(reversed(data[start_idx:end_idx + 1]))

            # Update only the affected breakpoints
            # breakpoints = update_breakpoints(data, breakpoints, start_idx, end_idx)

            ascending_strips.remove(random_strip)
            descending_strips.append(random_strip)

            rotations += 1


        smallest_element = None
        strip = None
        if heuristic == 1:
            # Get the smallest element at the end of any descending strip
            smallest_element = min(data[strip[1]] for strip in descending_strips)

            # Find which strip contains the smallest element
            for strip in descending_strips:
                if data[strip[1]] == smallest_element:
                    break
        elif heuristic == 2:
            # Get the
            strip = random.choice(descending_strips)
            smallest_element = data[strip[1]]
        elif heuristic == 3:
            # Get last strip
            strip = descending_strips[-1]
            smallest_element = data[strip[1]]

        # Find position of smallest_element-1
        try:
            index = data.index(smallest_element - 1)
        except ValueError:
            index = -1

        # Handle different cases for reversal
        if index == -1:
            # Move the reversed strip to the beginning
            start_idx = 0
            end_idx = strip[1]
            data[start_idx:end_idx + 1] = list(reversed(data[start_idx:end_idx + 1]))
        elif index < strip[0]:
            # Index is before the strip
            start_idx = index + 1
            end_idx = strip[1]
            data[start_idx:end_idx + 1] = list(reversed(data[start_idx:end_idx + 1]))
        elif index > strip[1]:
            # Index is after the strip
            start_idx = strip[1] + 1
            end_idx = index
            data[start_idx:end_idx + 1] = list(reversed(data[start_idx:end_idx + 1]))
        else:
            # Index is within the strip - no need to reverse
            rotations += 1
            continue

        # Update only the affected breakpoints and strips
        breakpoints = update_breakpoints(data, breakpoints, start_idx, end_idx)
        ascending_strips, descending_strips, single_item_strips, index_to_strip = update_ordered_strips(
            data, ascending_strips, descending_strips, single_item_strips,
            breakpoints, start_idx, end_idx)

        rotations += 1

    print("Rotations made:", rotations)
    return data




def getTimes():
    filename = "G1.txt"

    readData = readFileData(filename)
    # print("Data:\n", readData)

    count = 100
    simpleTimes = 0
    breakpointTimes = 0
    ownTimes = 0
    improvedOwnTimes = 0

    for i in range(count):
        start = time.time()
        simpleReverseData = simpleReversalSort(readData.copy())
        simpleTimes += (time.time() - start) * 1000
        if any(simpleReverseData[i] != i + 1 for i in range(len(simpleReverseData))):
            print("Simple Reversal Sort Failed")

        start = time.time()
        breakpointData = improvedBreakpointReversalSort(readData.copy(), 1)
        breakpointTimes += (time.time() - start) * 1000
        if any(breakpointData[i] != i + 1 for i in range(len(breakpointData))):
            print("Improved Breakpoint Reversal Sort Failed")

        start = time.time()
        ownData = improvedBreakpointReversalSort(readData.copy(), 2)
        ownTimes += (time.time() - start) * 1000
        if any(ownData[i] != i + 1 for i in range(len(ownData))):
            print("Own Implementation Failed")

        start = time.time()
        improvedOwnData = improvedBreakpointReversalSort(readData.copy(), 3)
        improvedOwnTimes += (time.time() - start) * 1000
        if any(improvedOwnData[i] != i + 1 for i in range(len(improvedOwnData))):
            print("Improved Own Implementation Failed")

    print("Algorithm times for file ", filename)
    print("Simple Reversal Sort Average Time taken:", simpleTimes / count, "ms")
    print("Improved Breakpoint Reversal Sort Average Time taken:", breakpointTimes / count, "ms")
    print("Own Implementation Average Time taken:", ownTimes / count, "ms")
    print("Improved Own Implementation Average Time taken:", improvedOwnTimes / count, "ms")


if __name__ == '__main__':

    # getTimes()
    # exit(0)

    filename = "G5.txt"

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    readData = readFileData(filename)
    # print("Data:\n", readData)

    # start = time.time()
    # simpleReverseData = simpleReversalSort(readData.copy())
    # print("simpleReversalSort Time taken:", (time.time() - start) * 1000, "ms")
    # print("Correctly Sorted:", all(simpleReverseData[i] == i + 1 for i in range(len(simpleReverseData))))
    # print("Simple Reversal Sort:\n", simpleReverseData)

    start = time.time()
    breakpointData = improvedBreakpointReversalSort(readData.copy(), 1)
    print("improvedBreakpointReversalSort Time taken:", (time.time() - start) * 1000, "ms")
    print("Correctly Sorted:", all(breakpointData[i] == i + 1 for i in range(len(breakpointData))))
    # print("Improved Breakpoint Reversal Sort:\n", breakpointData)

    # start = time.time()
    # ownData = improvedBreakpointReversalSort(readData.copy(), 2)
    # print("Own Implementation Time taken:", (time.time() - start) * 1000, "ms")
    # print("Correctly Sorted:", all(ownData[i] == i + 1 for i in range(len(ownData))))
    # print("Own Implementation:\n", ownData)

    # start = time.time()
    # improvedOwnData = improvedBreakpointReversalSort(readData.copy(), 3)
    # print("Improved Own Implementation Time taken:", (time.time() - start) * 1000, "ms")
    # print("Correctly Sorted:", all(improvedOwnData[i] == i + 1 for i in range(len(improvedOwnData))))
    # print("Improved Own Implementation:\n", improvedOwnData)
