#This script creates a text file containing the NYC street grid

'''Assumptions:
1. Includes NYC streets from 42nd to 57th street and from 5th to 11th Ave, excepting Broadway
2. Blocks are 900 x 264 feet
3. Car cells are 30 feet long (rounding up to 270' for streets)
4. One-way and two-way roads follow the real street grid
'''
'''
EXAMPLE
f= open("guru99.txt","w+")
for i in range(10):
     f.write("This is line %d\r\n" % (i+1))
f.close()
'''

#Manhattan Grid Creation Script
#Includes all real manhattan streets from 5th to 11th ave and 42nd to 57th st
f = open('manhattan_accidents_construction.txt','w+')
#Make intersections
for i in range(7): #x direction (E->W)
    for j in range(16): #y direction (S->N)
        f.write("v%d_%d: %d,%d\r\n" % (i+1, j+1, i*45, j*13))
f.write("\r\n")

#Make edges
'''
#Default setting
avs = ['3:3', '5:0', '0:5', '5:0', '0:5', '5:0', '0:5'] #Lane #s Avs 11th - 5th
sts = ['2:2', '0:2', '2:0', '0:2', '2:0', '0:2', '2:0', '0:2', '2:0', '0:2', \
            '2:0', '0:2', '2:0', '0:2', '2:0', '2:2'] #Lane #s Sts 42nd-57th
#Bad weather setting - Reduce lanes by 50%, rounded down
avs = ['1:1', '2:0', '0:2', '2:0', '0:2', '2:0', '0:2'] #Lane #s Avs 11th - 5th
sts = ['1:1', '0:1', '1:0', '0:1', '1:0', '0:1', '1:0', '0:1', '1:0', '0:1', \
            '1:0', '0:1', '1:0', '0:1', '1:0', '1:1'] #Lane #s Sts 42nd-57th
'''
#Accidents and construction setting - Accidents on 42nd st and 7th ave; construction on 11th ave, lane number changes
avs = ['1:1', '5:0', '0:5', '5:0', '0:5', '5:0', '0:5'] #Lane #s Avs 11th - 5th
sts = ['2:2', '0:2', '2:0', '0:2', '2:0', '0:2', '2:0', '0:2', '2:0', '0:2', \
            '2:0', '0:2', '2:0', '0:2', '2:0', '2:2'] #Lane #s Sts 42nd-57th ACCIDENT CHANGES MADE MANUALLY AFTER


#Set avenue edges S to N
for i in range(15):
    for j in range(7):
        f.write("v%d_%d:v%d_%d: %s\r\n" % (j+1, i+1, j+1, i+2, avs[j]))
#Set street edges W to E
for i in range(6):
    for j in range(16):
        f.write("v%d_%d:v%d_%d: %s\r\n" % (i+1, j+1, i+2, j+1, sts[j]))
f.close()
