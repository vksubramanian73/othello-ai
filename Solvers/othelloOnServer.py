import sys; args = sys.argv[1:]
#Varshini Subramanian, Period 7
numberOfHoles = 13
numberOfGames = 6

import random
import time
start_time = time.process_time()

midGameABDepth = 5
board = '.'*27 + 'ox......xo' + '.'*27
token = 'x'; opposite = 'o'
gMOVES = []
gNEIGHBORPOS = {}
gLETTERTONUMBER = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
gCORNERS = {0, 7, 56, 63}
gMOVESTOAVOID = {0: [1, 8, 9], 7:[6, 15, 14], 56: [48, 57, 49], 63: [55, 62, 54]}
gEDGES = {(1, 7, 0): {1, 2, 3, 4, 5, 6}, (1, 63, 56): {63, 62, 61, 60, 59, 58, 57, 56}, 
        (8, 56, 0): {8, 16, 24, 32, 40, 48}, (8, 63, 7): {55, 47, 39, 31, 23, 15}}
gCACHEDMOVES = {}

def setGlobals():
    global board, token, opposite, gMOVES, gNEIGHBORPOS
    if args:
        movesStart = -1
        for i,arg in enumerate(args):
            if arg.isdigit() or len(arg) == 2:
                movesStart = i
                break
        if movesStart == 2 or (movesStart == -1 and len(args) > 1): 
            board = args[0].lower()
            token = args[1].lower(); opposite = {'x', 'o'} - {token}
        elif movesStart == 1 or (movesStart == -1 and len(args) == 1):
            if len(args[0]) == 64: 
                board = args[0].lower()
                if (len(board) - board.count('.')) % 2 == 1: token = 'o'; opposite = 'x'
            elif args[0].lower() == 'o': token = 'o'; opposite = 'x'
        if movesStart != -1:
            for i in range(movesStart, len(args)):
                if args[i][0] == '-': continue
                gMOVES.append(convertMoveToInteger(args[i]))
    
    for i in range(64):
        toAppend = set()
        if i - 8 >= 0: toAppend.add(i-8)
        if i + 8 < 64: toAppend.add(i+8)
        if i % 8 != 0 and (i - 1) >= 0: toAppend.add(i-1)
        if (i + 1) % 8 != 0 and (i + 1) < 64: toAppend.add(i+1)
        if (i + 1) % 8 != 0 and (i - 7) > 0: toAppend.add(i-7)
        if i % 8 != 0 and (i + 7) < 64: toAppend.add(i+7)
        if i % 8 != 0 and (i - 9) >= 0: toAppend.add(i-9)
        if (i + 1) % 8 != 0 and (i + 9) < 64: toAppend.add(i+9)
        if i + 8 < 64: toAppend.add(i+8)
        gNEIGHBORPOS[i] = toAppend

def convertMoveToInteger(move):
    if move.isdigit(): return int(move)
    else: return gLETTERTONUMBER[move[0].upper()] + (int(move[1]) - 1)*8

def printBoard(board, possibleMoves, upperIndices):
    strBoard = ''
    for i in range(8):
        start = i*8
        end = start+8
        for j in range(start, end):
            if j in possibleMoves: strBoard += '*'
            elif j in upperIndices: strBoard += board[j].upper()
            else: strBoard += board[j]
        strBoard += '\n'
    return strBoard

def possibleMoves(board, token, opposite):
    oppositeTokenIndices = []
    for tokenIndex in [i for i,v in enumerate(board) if v == token]:
        for nbrPos in gNEIGHBORPOS[tokenIndex]:
            if board[nbrPos] == opposite: oppositeTokenIndices.append((nbrPos, nbrPos-tokenIndex))
    toRet = []; exploreMore = []; indicesToReplace = {}
    for i in oppositeTokenIndices:
        for j in gNEIGHBORPOS[i[0]]:
            if j - i[0] == i[1]:
                if j not in indicesToReplace: indicesToReplace[j] = []
                if board[j] == '.': 
                    if j not in toRet: toRet.append(j)
                    indicesToReplace[j].append(i[0])
                elif board[j] == opposite: exploreMore.append((j, i[1], i[0], indicesToReplace[j]))
    for i in exploreMore:
        charToRet = opposite; newIndex = i[0]; toAppend = [i[2], newIndex]
        while charToRet == opposite:
            if newIndex + i[1] in gNEIGHBORPOS[newIndex]: newIndex += i[1]; charToRet = board[newIndex]; toAppend.append(newIndex)
            else: break
        if charToRet == '.': 
            if newIndex not in toRet: toRet.append(newIndex)
            if newIndex in indicesToReplace: indicesToReplace[newIndex] = toAppend + indicesToReplace[newIndex]
            else: indicesToReplace[newIndex] = toAppend
    gCACHEDMOVES[(board, token, opposite)] = (toRet, indicesToReplace)
    return toRet, indicesToReplace

def preferredMove(board, possibleMoves, indicesToReplace, token):
    if (prefMv:=gCORNERS & {*possibleMoves}): return prefMv
    if len(possibleMoves) == 1: return possibleMoves
    if (passMove:=forcedPass(board, possibleMoves, token, indicesToReplace)): return passMove
    possibleMovesWithoutCX = removeCX(board, possibleMoves)
    if not possibleMovesWithoutCX: return possibleMoves
    if (wedge:=findWedges(board, possibleMovesWithoutCX, token)): return wedge
    if (edge:=safeEdge(board, possibleMovesWithoutCX, indicesToReplace)): return edge
    else: return possibleMovesWithoutCX

def removeCX(board, possibleMoves):
    temp = {*possibleMoves}
    for badCorner in [i for i in gCORNERS if board[i] == '.']:
        for moveToAvoid in gMOVESTOAVOID[badCorner]:
            if moveToAvoid in possibleMoves: temp.remove(moveToAvoid)
    return temp

def forcedPass(board, moves, token, indicesToReplace):
    opposite = 'xo'.replace(token, '')
    for i in moves:
        newBoard = makeMove(board, indicesToReplace, token, i)
        newMoves, toReplace = possibleMoves(newBoard, opposite, token)
        if len(newMoves) == 0: return {i}
    return set()

def findWedges(board, possibleMoves, token):
    opposite = 'xo'.replace(token, '')
    for i in gEDGES:
        for move in (gEDGES[i] & possibleMoves):
            for j in range(1, 4):
                if move + j*i[0] > i[1] or move - j*i[0] < i[2]: break
                elif board[move + j*i[0]] == board[move - j*i[0]] == opposite: return {move}
    return set()

def safeEdge(board, possibleMoves, indicesToReplace):
    temp = {*possibleMoves}
    for i in gEDGES:
        for move in (gEDGES[i] & temp):
            for i in gMOVESTOAVOID:
                if gMOVESTOAVOID[i][2] in indicesToReplace[move] and board[i] == '.': temp.remove(move)
    for i in gEDGES:
        for move in (gEDGES[i] & temp):
            if board[move + i[0]] == opposite and board[move - i[0]] == token:
                newPos = -1
                for j in range(move - i[0], i[2] - 1, -i[0]):
                    if board[j] == token: continue
                    else: newPos = j; break
                if newPos != -1 and board[newPos] == '.': temp.remove(move)
            elif board[move - i[0]] == opposite and board[move + i[0]] == token:
                newPos = -1
                for j in range(move + i[0], i[1] + 1, i[0]):
                    if board[j] == token: continue
                    else: newPos = j; break
                if newPos != -1 and board[newPos] == '.': temp.remove(move)  
    if (edge:=bestEdgeToken(board, temp, indicesToReplace)): return edge 
    else: return minimizeFrontiers(board, temp, indicesToReplace)

def bestEdgeToken(board, possibleMoves, indicesToReplace):
    toRet = []; tokensFlipped = -1; moveToRet = -1
    for corner in [i for i in gCORNERS if board[i] == token or board[i] == opposite]:
        for move in gMOVESTOAVOID[corner]:
            if move in possibleMoves: toRet.append((move, indicesToReplace[move]))
    for i in gEDGES:
        for move in (gEDGES[i] & possibleMoves):
            if board[move + i[0]] == board[move - i[0]] == '.': toRet.append((move, indicesToReplace[move]))
            if board[move + i[0]] == opposite:
                newPos = -1
                for j in range(move + i[0], i[1] + 1, i[0]):
                    if board[j] == opposite: continue
                    else: newPos = j; break
                if newPos != -1 and board[newPos] == token: toRet.append((move, indicesToReplace[move]))
            elif board[move - i[0]] == opposite:
                newPos = -1
                for j in range(move - i[0], i[2] - 1, -i[0]):
                    if board[j] == opposite: continue
                    else: newPos = j; break
                if newPos != -1 and board[newPos] == token: toRet.append((move, indicesToReplace[move]))
            elif board[move + i[0]] == token and board[move - i[0]] == '.': toRet.append((move, indicesToReplace[move]))
            elif board[move + i[0]] == '.' and board[move - i[0]] == token: toRet.append((move, indicesToReplace[move]))
    for i in toRet:
        if len(i[1]) > tokensFlipped: moveToRet = i[0]; tokensFlipped = len(i[1])
    if moveToRet != -1: return {moveToRet}
    else: return set()

def minimizeFrontiers(board, possibleMoves, indicesToReplace):
    emptySpaces = []; counter = -1
    for i in possibleMoves:
        counter = 0
        for index in indicesToReplace[i] + [i]:
            for nbr in [*gNEIGHBORPOS[index]]:
                if board[nbr] == '.' and nbr not in possibleMoves: counter += 1
        emptySpaces.append((i, counter))
    leastNumber = counter; moveToRet = -1
    for i in emptySpaces:
        if i[1] < leastNumber: moveToRet = i[0]; leastNumber = i[1]
    if moveToRet == -1: return possibleMoves
    else: return {moveToRet}

def alphabeta(board, token, lowerBound, upperBound):
    opposite = 'xo'.replace(token, '')
    if (board, token, opposite) in gCACHEDMOVES: 
        moves, indicesToReplace = gCACHEDMOVES[(board, token, opposite)]
    else: moves, indicesToReplace = possibleMoves(board, token, opposite)
    if (board, opposite, token) in gCACHEDMOVES: 
        eMoves, eIndicesToReplace = gCACHEDMOVES[(board, opposite, token)]
    else: eMoves, eIndicesToReplace = possibleMoves(board, opposite, token)
    if len(moves) == 0: 
        if len(eMoves) == 0: return [board.count(token) - board.count(opposite)]
        else: 
            ab = alphabeta(board, opposite, -upperBound, -lowerBound) + [-1]
            ab[0] = -ab[0]
            return ab
    bestSoFar = [lowerBound - 1]
    for move in moves:
        newBoard = makeMove(board, indicesToReplace, token, move)
        ab = alphabeta(newBoard, opposite, -upperBound, -lowerBound)
        if -ab[0] < lowerBound: continue
        if -ab[0] > upperBound: return [-ab[0]]
        bestSoFar = [-ab[0]] + ab[1:] + [move]
        lowerBound = -ab[0] + 1
    return bestSoFar

def boardEvaluation(board, token):
    total = 0; opposite = 'xo'.replace(token, '') 
    total += board.count(token)/100
    if (board, token, opposite) in gCACHEDMOVES: 
        moves, indicesToReplace = gCACHEDMOVES[(board, token, opposite)]
    else: moves, indicesToReplace = possibleMoves(board, token, opposite)
    total += len(moves)
    if len(moves) == 0: total -= 50
    if board.count(token) == 0: total -= 50
    for i in gCORNERS:
        if board[i] == token: total += 10
    for i in gMOVESTOAVOID: 
        for j in gMOVESTOAVOID[i]:
            if board[j] == token:
                if board[i] == opposite or board[i] == '.': total -= 4
                elif board[i] == token: total += 4
    return total

def midgameAlphaBeta(board, token, lowerBound, upperBound, depth):
    opposite = 'xo'.replace(token, '')
    if (board, token, opposite) in gCACHEDMOVES: 
        moves, indicesToReplace = gCACHEDMOVES[(board, token, opposite)]
    else: moves, indicesToReplace = possibleMoves(board, token, opposite)
    if (board, opposite, token) in gCACHEDMOVES: 
        eMoves, eIndicesToReplace = gCACHEDMOVES[(board, opposite, token)]
    else: eMoves, eIndicesToReplace = possibleMoves(board, opposite, token)
    if len(moves) == 0 and len(eMoves) > 0: 
        ab = midgameAlphaBeta(board, opposite, -upperBound, -lowerBound, depth) + [-1]
        ab[0] = -ab[0]
        return ab
    elif depth == midGameABDepth or len(moves) == len(eMoves) == 0: 
        return [boardEvaluation(board, token) - boardEvaluation(board, opposite)]
    bestSoFar = [lowerBound - 1]
    for move in moves:
        newBoard = makeMove(board, indicesToReplace, token, move)
        ab = midgameAlphaBeta(newBoard, opposite, -upperBound, -lowerBound, depth+1)
        if -ab[0] < lowerBound: continue
        if -ab[0] > upperBound: return [-ab[0]]
        bestSoFar = [-ab[0]] + ab[1:] + [move]
        lowerBound = -ab[0] + 1
    return bestSoFar

def printMoves(possibleMoves, token):
    toRet = 'Possible moves for ' + token + ': '
    for i,v in enumerate([*possibleMoves]):
        toRet += str(v)
        if (i + 1) < len(possibleMoves):
            toRet += ', '
    return toRet

def makeMove(board, indicesToReplace, token, move):
    boardLst = [*board]
    boardLst[move] = token
    for i in indicesToReplace[move]:
        boardLst[i] = token
    return ''.join(boardLst)

def playGame(board, token, opposite):
    counter = 1; transcript = []
    while board.count('.') >= 1 and board.count('x') >= 1 and board.count('o') >= 1:
        if counter % 2 == 1: player = 'x'; opponent = 'o'
        else: player = 'o'; opponent = 'x'
        moves, indicesToReplace = possibleMoves(board, player, opponent)
        if len(moves) == 0:
            transcript.append(-1); counter += 1
            moves, indicesToReplace = possibleMoves(board, opponent, player)
            player, opponent = opponent, player
        if len(moves) == 0: 
            transcript.append(-1)
            return transcript, board.count(token), len(board) - board.count('.'), board.count(opposite)
        if player == token: 
            if board.count('.') < numberOfHoles: 
                ab = alphabeta(board, token, -65, 65)
                bestMoves = ab[1:]
            else: 
                ab = midgameAlphaBeta(board, token, -200, 200, 0)
                bestMoves = ab[1:]
            move = bestMoves[len(bestMoves) - 1]
        else: move = random.choice([*moves])
        transcript.append(move)
        board = makeMove(board, indicesToReplace, player, move)
        counter += 1
    return transcript, board.count(token), len(board) - board.count('.'), board.count(opposite)

def playScript(number):
    global gCACHEDMOVES
    player_count = 0; total_tokens = 0; strToRet = ''; cumScores = []; board = ''
    for i in range(1, number + 1):
        board = '.'*27 + 'ox......xo' + '.'*27
        if i % 2 == 0: token = 'o'; opponent = 'x'
        else: token = 'x'; opponent = 'o'
        transcript, token_count, total_count, opposite_count = playGame(board, token, opponent)
        player_count += token_count; total_tokens += total_count
        score = str(token_count - opposite_count) 
        strToRet += score
        if len(score) == 1: strToRet += '   '  
        else: strToRet += '  '
        if i % (number/10) == 0: strToRet += '\n'
        cumScores.append(((token_count - opposite_count), i, token, transcript))
        cumScores = sorted(cumScores)
        gCACHEDMOVES = {}
        print(f"Score so far: {'{0:1.3g}'.format((player_count/total_tokens) * 100)}%")
    print(strToRet)
    print(f"My token count: {player_count}")
    print(f"Total token count: {total_tokens}")
    print(f"Terminal AB Limit: {numberOfHoles}")
    print(f"Midgame AB Depth: {midGameABDepth}")
    print(f"Score so far: {'{0:1.3g}'.format((player_count/total_tokens) * 100)}%")
    print(f"Game {cumScores[0][1]} as {cumScores[0][2]} => {cumScores[0][0]}: {' '.join(map(str, cumScores[0][3]))}")
    print(f"Game {cumScores[1][1]} as {cumScores[1][2]} => {cumScores[1][0]}: {' '.join(map(str, cumScores[1][3]))}")

def snapshot(board, token, move, upperIndices):
    opposite = 'xo'.replace(token, ''); nextToken = opposite
    if move != -1: print(f"{token} plays to {move}"); token, opposite = opposite, token
    moves, indicesToReplace = possibleMoves(board, token, opposite) 
    print(printBoard(board, moves, upperIndices))
    print(f"{board} {board.count('x')}/{board.count('o')}")
    if board.count('.') != 0:
        if len(moves) == 0: 
            moves, indicesToReplace = possibleMoves(board, opposite, token)
            printmoves = printMoves(moves, opposite)
            nextToken = token
        else: 
            printmoves = printMoves(moves, token)
        print(printmoves)
    return indicesToReplace, nextToken, moves

def individualMoveProcessing(board, token, moves):
    opposite = 'xo'.replace(token, '')
    indicesToReplace, nextToken, possibleMoves = snapshot(board, token, -1, [])
    print(f"My preferred move is {preferredMove(board, possibleMoves, indicesToReplace, opposite)}")
    if board.count('.') < numberOfHoles:
        ab = alphabeta(board, token, -65, 65)
        print(f"Min score: {ab[0]}; move sequence: {ab[1:]}")
    else:
        ab = midgameAlphaBeta(board, token, -200, 200, 0)
        print(f"Min score: {ab[0]}; move sequence: {ab[1:]}")
    for i, move in enumerate(moves):
        if i != 0 and nextToken != token: token, opposite = opposite, token
        board = makeMove(board, indicesToReplace, token, move)
        upperIndices = indicesToReplace[move] + [move]
        indicesToReplace, nextToken, possibleMoves = snapshot(board, token, move, upperIndices)
        if i != len(moves): 
            print(f"My preferred move is {preferredMove(board, possibleMoves, indicesToReplace, opposite)}")
            if board.count('.') < numberOfHoles:
                ab = alphabeta(board, token, -65, 65)
                print(f"Min score: {ab[0]}; move sequence: {ab[1:]}")
            else:
                ab = midgameAlphaBeta(board, token, -200, 200, 0)
                print(f"Min score: {ab[0]}; move sequence: {ab[1:]}")

def main():
    setGlobals()
    if args:
        individualMoveProcessing(board, token, gMOVES)
        print(f"Elapsed time: {time.process_time() - start_time}s")
    else: 
        playScript(numberOfGames)
        print(f"Elapsed time: {time.process_time() - start_time}s")

class Strategy:
    logging = True 
    setGlobals()
    def best_strategy(self, board, token, best_move, running):
        global gNEIGHBORPOS, gCORNERS, gCACHEDMOVES, gCACHEDMOVES, gEDGES
        if running.value:
            moves, indicesToReplace = possibleMoves(board, token, 'xo'.replace(token, ''))
            bestMoves = [*preferredMove(board, moves, indicesToReplace, token)]
            best_move.value = bestMoves[len(bestMoves) - 1]
            if board.count('.') < numberOfHoles:
                ab = alphabeta(board, token, -64, 64)[1:]
                best_move.value = ab[len(ab) - 1]
            else: 
                ab = midgameAlphaBeta(board, token, -200, 200, 0)[1:]
                best_move.value = ab[len(ab) - 1]

if __name__ == '__main__': main()