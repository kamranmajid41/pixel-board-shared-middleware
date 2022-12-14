import numpy as np
import cv2
from PIL import ImageColor

class CrossOut:
    def __init__(self, raw_board, palette):
        self.palette = [ImageColor.getrgb(x) for x in palette]
        self.palette = [(x[2], x[1], x[0]) for x in self.palette]

        print(len(raw_board))
        self.image = np.array([[self.palette[i] for i in row] for row in raw_board], dtype=np.uint8)

        self.ROW = len(self.image)
        self.COL = len(self.image[0])
        self.regions = {}

    def haris_corner_detection(self):
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        gray_image = np.float32(gray_image)
        
        # Applying the function
        dst = cv2.cornerHarris(gray_image, blockSize=2, ksize=3, k=0.04)
        
        # dilate to mark the corners
        dst = cv2.dilate(dst, None)

        # mark feature spots with green 
        self.image[dst > 0.1 * dst.max()] = [1, 254, 1]

        # create new array to isolate green spots 
        density_map = []
        for i in range(len(self.image)):
            curr = []
            for j in range(len(self.image[i])):
                if set(self.image[i][j]) == set([1, 254, 1]):
                    curr.append([0, 255, 0])
                    continue
                curr.append([255, 255, 255])
            density_map.append(curr)

        usable_map = np.array(density_map)
        map = np.array(density_map, dtype = np.uint8)

        binary_map = []
        for row in usable_map:
            curr = [] 
            for rgb in row:
                if set(rgb) == set([255, 255, 255]):
                    curr.append(0)
                    continue 
                curr.append(1)
            binary_map.append(curr)


        return map, binary_map


    def isSafe(self, M, row, col, visited):
        return ((row >= 0) and (row < self.ROW) and
                (col >= 0) and (col < self.COL) and
                (M[row][col] and not visited[row][col]))
    

    def DFS(self, M, row, col, visited, count):
        rowNbr = [-1, -1, -1, 0, 0, 1, 1, 1]
        colNbr = [-1, 0, 1, -1, 1, -1, 0, 1]

        # Mark this cell as visited
        visited[row][col] = True

        # Recur for all connected neighbours
        for k in range(8):
            if (self.isSafe(M, row + rowNbr[k], col + colNbr[k], visited)):
                count[0] += 1
                self.DFS(M, row + rowNbr[k], col + colNbr[k], visited, count)
    

    def largestRegion(self, M):
        # Make a bool array to mark visited cells.
        # Initially all cells are unvisited
        visited = [[0] * self.COL for i in range(self.ROW)]
    
        # Initialize result as 0 and traverse
        # through the all cells of given matrix
        result = -999999999999
        for i in range(self.ROW):
            for j in range(self.COL):
                # If a cell with value 1 is not visited yet, then new region found
                if (M[i][j] and not visited[i][j]):
                    count = [1]
                    self.DFS(M, i, j, visited, count)
                    # store new region in map 
                    self.regions[count[0]] = (i, j)
        return self.regions


    def add_X(self, map, size, coords):
        # intelligently add an X on the specified region
        row = coords[0]
        col = coords[1]
        # Set X color
        color = [0, 0, 0] if set(self.image[row][col]) == set([0, 0, 255]) else [0, 0, 255]
        j = int(np.sqrt(size) - 1)
        for i in range(int(np.sqrt(size))):
            if row + i < self.ROW and col + i < self.COL and col + j < self.COL:
                map[row + i][col + i] = color
                map[row + i][col + j] = color 
                j -= 1
        return map


    def get_desc_regions(self):
        _, binary_map = self.haris_corner_detection()
        regions = self.largestRegion(binary_map)
        # Region list to store sizes in descending order and coordinates
        regions_list = list(reversed(sorted(regions.keys())))
        desc_regions = []
        for size in regions_list: 
            desc_regions.append((size, regions[size]))

        return desc_regions

def color_distance(pixel, bg):
    r, g, b = pixel
    color_diff = 0
    cr, cg, cb = bg
    color_diff = np.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
    return color_diff
