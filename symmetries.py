import sys; args = sys.argv[1:]
#Varshini Subramanian, Hasita Ravula, Period 7

board = args[0]
gWIDTH = 0
gHEIGHT = 0

def square(board):
    global gWIDTH, gHEIGHT
    if len(args) == 2:
        gWIDTH = int(args[1]); gHEIGHT = len(board)//gWIDTH 
    else:
        puzlen = len(board)
        y = int(puzlen ** .5 +.5)
        while(puzlen % y != 0): y-=1
        if puzlen//y == y: gWIDTH = gHEIGHT = y
        else: gWIDTH = max(puzlen//y, y); gHEIGHT = min(puzlen//y, y)

def findSymmetries(board):
    toRet = set()
    toRet.add(board)
    toRet.add(verticalReflection(board, gWIDTH, gHEIGHT))
    toRet.add(horizontalReflection(board))
    flipped90 = flip90(board, gWIDTH, gHEIGHT)
    flipped180 = flip90(flipped90, gHEIGHT, gWIDTH)
    flipped270 = flip90(flipped180, gWIDTH, gHEIGHT)
    toRet.add(flipped90); toRet.add(flipped180); toRet.add(flipped270)
    toRet.add(verticalReflection(flipped270, gHEIGHT, gWIDTH)); toRet.add(verticalReflection(flipped90, gHEIGHT, gWIDTH))
    return toRet

def verticalReflection(board, width, height):
    explodedStr = [*board]; counter = 0; tempIndices = []
    for i in range(height-1, -1, -1):
        for j in range(width*i, width*i+width):
            tempIndices.append(j)
    for i in tempIndices:
        explodedStr[counter] = board[i]
        counter += 1
    return ''.join(explodedStr)

def horizontalReflection(board):
    explodedStr = [*board]; counter = 0; tempIndices = []
    for i in range(gHEIGHT):
        for j in range(gWIDTH*i+gWIDTH, gWIDTH*i, -1):
            tempIndices.append(j-1)
    for i in tempIndices:
        explodedStr[counter] = board[i]
        counter += 1
    return ''.join(explodedStr)

def flip90(board, width, height):
    counter = 0; explodedStr = [*board]; tempIndices = []
    for i in range(0, width):
        for j in range(width * (height - 1) + i, -1, -width):
            tempIndices.append(j)
    for i in tempIndices:
        explodedStr[counter] = board[i]
        counter += 1
    return ''.join(explodedStr)

def main():
    square(board)
    for symmetry in findSymmetries(board):
        print(symmetry)

if __name__ == '__main__': main()