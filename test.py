a = [[0,1.0,1.0,0,0],
     [0,0,0.75,0,0],
     [0,0.25,0,0.6,0.67],
     [0,0,0.4,0,0],
     [0,0,0.33,0,0]]

total_games = sum(sum(row) for row in a)
b = [1.0 / total_games] * len(a[0])

for i in range(10):
    print b
    new = [0.0] * len(a[0])
    for j, row in enumerate(a):
        for i, val in enumerate(row):
            new[j] += b[i] * val *0.85
    b = new
