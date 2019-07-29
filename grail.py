import random
from enum import Enum


# num cards
NUM_WHITE = 84
NUM_BLACK = 76

# card freqs
NUM_GRAIL = 16
NUM_DESPAIR = 15
NUM_DESOLATION = 2

INIT_HAND_SIZE = 5

class WhiteCard(Enum):
  OTHER = 1
  GRAIL = 2

class BlackCard(Enum):
  OTHER = 1
  DESPAIR = 2
  DESOLATION = 3

class Location(Enum):
  CASTLE = 1
  GRAIL = 2

def card_names(cards):
  return [c.name if c else " " for c in cards]

class Player(object):
  def __init__(self, name="", strategy=None):
    self.name = name
    self.hand = []
    self.moved = False
    self.health = 4
    if strategy:
      self.strategy = strategy
    else:
      self.strategy = DoNothingStrat()
    self.location  = Location.CASTLE

  def turn(self, game):
    self.strategy.turn(game, self)
    self.moved = False

  def take_card(self, card):
    self.hand.remove(card)

  def print_hand(self):
    print(self.hand)

class SometimesDraw(object):
  def turn(self, game, player):
    i = random.randint(1, 10)
    if i <= 2:
      game.draw_white(player, 2)

class GrailStrat1(object):
  def turn(self, game, player):
    num_grail = player.hand.count(WhiteCard.GRAIL)
    if player.location != Location.GRAIL:
      if num_grail >= 3:
    	game.validate_and_move(player, Location.GRAIL)
      else:
        game.draw_white(player, 2)
    elif player.location == Location.GRAIL:
      if num_grail > 0:
        player.take_card(WhiteCard.GRAIL)
    	game.validate_and_apply(player, WhiteCard.GRAIL)
      else: 
    	game.validate_and_move(player, Location.CASTLE)

class GrailHealthStrat(object):
  def turn(self, game, player):
    num_grail = player.hand.count(WhiteCard.GRAIL)
    if player.location != Location.GRAIL:
      if num_grail >= 3:
    	game.validate_and_move(player, Location.GRAIL)
        if player.health > 2:
          player.health -= 1
          player.take_card(WhiteCard.GRAIL)
    	  game.validate_and_apply(player, WhiteCard.GRAIL)
      else:
        game.draw_white(player, 2)
        num_grail = player.hand.count(WhiteCard.GRAIL)
        if player.health > 2 and num_grail > 3:
          player.health -= 1
    	  game.validate_and_move(player, Location.GRAIL)
    elif player.location == Location.GRAIL:
      if num_grail > 0:
        player.take_card(WhiteCard.GRAIL)
    	game.validate_and_apply(player, WhiteCard.GRAIL)
        if player.health > 2 and num_grail == 1:
    	  game.validate_and_move(player, Location.CASTLE)
      else: 
    	game.validate_and_move(player, Location.CASTLE)
        if player.health > 2:
          player.health -= 1
          game.draw_white(player, 2)

class Game(object):
  def __init__(self, players=None):
    if not players:
      self.players = []
    else:
      self.players = players
    self.cur_player = 0
    self.reset()

  def reset(self):
    self.white_discard = []
    self.black_discard = []
    self.white_deck = NUM_GRAIL*[WhiteCard.GRAIL] + (NUM_WHITE - NUM_GRAIL)*[WhiteCard.OTHER]
    self.black_deck = NUM_DESOLATION*[BlackCard.DESOLATION] + NUM_DESPAIR*[BlackCard.DESPAIR] + (NUM_BLACK - (NUM_DESPAIR + NUM_DESOLATION))*[BlackCard.OTHER]
    self.the_grail = 7*[None] # no cards
    self.the_grail_status = None
    self.shuffle()
    self.deal()

  def shuffle(self):
    random.shuffle(self.white_deck)
    random.shuffle(self.black_deck)
  
  def deal(self):
    for player in self.players:
      player.hand = self.white_deck[:INIT_HAND_SIZE]
      self.draw_white(player, INIT_HAND_SIZE)

  def draw(self, deck, player, n=1):
      """ returns remaining deck """
      return deck[:n], deck[n:]

  def draw_white(self, player, n=1):
      if n > len(self.white_deck):
        first_draw = len(self.white_deck)
        hand, deck = self.draw(self.white_deck, player, first_draw)
      	player.hand.extend(hand)
	random.shuffle(self.white_discard)
        self.white_deck = self.white_discard
        n = n - first_draw 
       # add discard to white deck after drawing
      hand, deck = self.draw(self.white_deck, player, n=n)
      player.hand.extend(hand)
      self.white_deck = deck

  def draw_black(self, player, n=1):
      result = []
      if n > len(self.black_deck):
        first_draw = len(self.black_deck)
        hand, deck = self.draw(self.black_deck, player, first_draw)
        result.extend(hand)
	random.shuffle(self.black_discard)
        self.black_deck = self.black_discard
        n = n - first_draw 
      cards, deck = self.draw(self.black_deck, player, n=n)
      self.black_deck = deck 
      result.extend(cards)
      return result

  def print_deck(self):
    print([c.name for c in self.white_deck])
    print([c.name for c in self.black_deck])
    print("white_deck: {}, black_deck: {}".format(len(self.white_deck), len(self.black_deck)))
 
  def print_grail(self):
    print("The Grail: {}".format(card_names(self.the_grail)))

  def print_hands(self):
    for i, player in enumerate(self.players):
      print("Player {}: {}".format(i, [c.name for c in player.hand]))

  def validate_and_apply(self, player, card):
    if card == WhiteCard.GRAIL and player.location != Location.GRAIL:
      raise Exception('validation error on apply')
    self.apply_card(card)
    return True

  def validate_and_move(self, player, location):
    player.moved = True
    if location != player.location:
    	player.location = location
	return True
    raise Exception('validation error on move')

  def apply_card(self, card):
    if card == BlackCard.DESPAIR:
      for i in range(7):
        cur_index = 6 - i
        c = self.the_grail[cur_index]
        if not c:
          self.the_grail[cur_index] = card
	  break
        elif c == WhiteCard.GRAIL:
          self.the_grail[cur_index] = None
          break
    elif card == BlackCard.DESOLATION:
      for i in range(7):
        cur_index = 6 - i
        c = self.the_grail[cur_index]
        if not c or c == WhiteCard.GRAIL:
          self.the_grail[cur_index] = card
          break
    elif card == WhiteCard.GRAIL:
      for i in range(7):
        c = self.the_grail[i]
        if not c:
          self.the_grail[i] = card
	  break
        elif c != WhiteCard.GRAIL:
          self.the_grail[i] = None
  	  break
    if card == BlackCard.DESPAIR or card == BlackCard.DESOLATION or card == WhiteCard.GRAIL:
       #self.print_grail()
       pass

    if type(card) == BlackCard:
      self.black_discard.append(card)
    if type(card) == WhiteCard:
      self.white_discard.append(card)

  def check_grail(self):
    r = None
    if all([c == WhiteCard.GRAIL for c in self.the_grail]):
      r = True
    elif all([type(c) == BlackCard for c in self.the_grail]):
      r = False
    self.the_grail_status = r 
    return r

  def turn(self):
    cur_player = self.players[self.cur_player]
    if cur_player.health > 0:
      drawn_black = self.draw_black(cur_player, n=1)
      self.apply_card(drawn_black[0])
      cur_player.turn(self)
    self.cur_player = (self.cur_player + 1) % len(self.players)

def test_grail_case(cards, expected, expected_state):
  g = Game()
  for card in cards:
    g.apply_card(card)

  if expected_state != g.check_grail():
    print("expected_state: {}\ngot_state: {}".format(expected_state, g.the_grail_status))

  if expected != g.the_grail:
    print("input: {}\nexpected: {}\ngot: {}\n\n".format(card_names(cards), card_names(expected), card_names(g.the_grail)))
    return False
  else:
    print("passed")
    return True

def test_grail():
  num_correct = 0
  cases = [(7*[BlackCard.DESPAIR], 7*[BlackCard.DESPAIR], False),
	   (6*[BlackCard.DESPAIR] + [BlackCard.DESOLATION], [BlackCard.DESOLATION] + 6*[BlackCard.DESPAIR], False),
	   (7*[WhiteCard.GRAIL], 7*[WhiteCard.GRAIL], True),
	   (6*[BlackCard.DESPAIR] + [WhiteCard.GRAIL],  [WhiteCard.GRAIL] + 6*[BlackCard.DESPAIR], None),
	   (6*[BlackCard.DESPAIR] + 2*[WhiteCard.GRAIL], [WhiteCard.GRAIL, None] + 5*[BlackCard.DESPAIR], None),
	   (6*[BlackCard.DESPAIR] + 12*[WhiteCard.GRAIL], 6*[WhiteCard.GRAIL] + [None], None),
	   (6*[BlackCard.DESPAIR] + 13*[WhiteCard.GRAIL], 7*[WhiteCard.GRAIL], True),
	   ([BlackCard.DESPAIR] + [WhiteCard.GRAIL], [WhiteCard.GRAIL] + 5*[None] + [BlackCard.DESPAIR], None),
	   ([WhiteCard.GRAIL] + [BlackCard.DESPAIR], [WhiteCard.GRAIL] + 5*[None] + [BlackCard.DESPAIR], None),
	   (6* [WhiteCard.GRAIL] + [BlackCard.DESPAIR, BlackCard.DESOLATION], 5*[WhiteCard.GRAIL] + [BlackCard.DESOLATION, BlackCard.DESPAIR], None),
	   (6* [WhiteCard.GRAIL] + [BlackCard.DESOLATION, BlackCard.DESPAIR], 5*[WhiteCard.GRAIL] + [None, BlackCard.DESOLATION], None)]

  for cards, expected, expected_state in cases: 
    correct = test_grail_case(cards, expected, expected_state)
    if correct:
      num_correct += 1
  
  print("{}/{} {:.0%} correct".format(num_correct, len(cases), num_correct*1.0/len(cases)))

def grail_player(name):
  return Player(name=name, strategy=GrailStrat1())

def health_player(name):
  return Player(name=name, strategy=GrailHealthStrat())

def rand_player(name):
  return Player(name=name, strategy=SometimesDraw())

def simulate_grail(players):
 g = Game(players=players)
 max_turn = 10000
 turn = 0
 while turn < max_turn:
   turn += 1
   g.turn()
   grail_status = g.check_grail()
   if grail_status is not None:
     if grail_status:
       return turn, grail_status
     else:
       return turn, grail_status
 return turn, None

def multi_sim(players):
  num_sim = 1000
  successes = []
  failures = []
  for i in range(num_sim):
    turn, result = simulate_grail(players)
    #print "turns: {}, result: {}".format(turn, result)
    if result:
      successes.append(turn)
    else:
      failures.append(turn)
  print("{} success. {} failures \n".format(len(successes), len(failures)))
  if successes:
    print("{} mean success turns".format(sum(successes) * 1.0/len(successes)))
  if failures:
    print("{} mean failure turns".format(sum(failures) * 1.0/len(failures)))


num_players = 6
for p in range(num_players):
  players = [health_player("Player {}".format(i)) if i < p else rand_player("Player {}".format(i)) for i in range(num_players)]
  print("{} players using health strat".format(p + 1))
  multi_sim(players=players)
