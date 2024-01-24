from nim import train, play

ai = train(10000)


while True:
    print("Starting a new game")
    play(ai)
