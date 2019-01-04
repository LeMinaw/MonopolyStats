from monopoly import Game


game = Game()
for i in range(100000):
    game.make_turn()
game.print_probas()
