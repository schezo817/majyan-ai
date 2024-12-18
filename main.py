import numpy as np

class Tile:
    # 牌の定義
    def __init__(self, suit, rank):
        self.suit = suit  
        self.rank = rank 

    def __repr__(self):
        return f"{self.suit}{self.rank}"
    
class Hand:
    # 手牌の定義
    def __init__(self):
        self.tiles = []

    def add_tile(self, tile):
        self.tiles.append(tile)

    def remove_tile(self, tile):
        self.tiles.remove(tile)

    def is_valid_hand(self):
        from collections import Counter

        def is_sequence(tiles):
            return len(tiles) == 3 and tiles[0].rank + 1 == tiles[1].rank and tiles[1].rank + 1 == tiles[2].rank

        def is_triplet(tiles):
            return len(tiles) == 3 and tiles[0].rank == tiles[1].rank == tiles[2].rank

        def can_form_melds(tiles):
            if len(tiles) == 0:
                return True
            if len(tiles) < 3:
                return False
            tiles.sort(key=lambda x: (x.suit, x.rank))
            for i in range(len(tiles) - 2):
                if is_sequence(tiles[i:i+3]) or is_triplet(tiles[i:i+3]):
                    new_tiles = tiles[:i] + tiles[i+3:]
                    if can_form_melds(new_tiles):
                        return True
            return False

        tile_counts = Counter((tile.suit, tile.rank) for tile in self.tiles)
        pairs = [tile for tile, count in tile_counts.items() if count >= 2]

        for pair in pairs:
            remaining_tiles = []
            for tile in self.tiles:
                if (tile.suit, tile.rank) == pair and tile_counts[pair] > 0:
                    tile_counts[pair] -= 1
                else:
                    remaining_tiles.append(tile)
            if can_form_melds(remaining_tiles):
                return True
        return False

    def __repr__(self):
        return f"Hand({self.tiles})"
    
class Game:
    def __init__(self):
        self.players = [Hand() for _ in range(4)]
        self.wall = self.create_wall()
        self.dead_wall = []

    def create_wall(self):
        suits = ['萬', '筒', '索']
        ranks = list(range(1, 10))
        honors = ['東', '南', '西', '北', '白', '發', '中']
        wall = [Tile(suit, rank) for suit in suits for rank in ranks] * 4
        wall += [Tile(honor, 1) for honor in honors] * 4
        np.random.shuffle(wall)
        return wall
    
    def draw_tile(self, player):
        if len(self.wall) > 0:
            tile = self.wall.pop()
            player.add_tile(tile)
            return tile
        else:
            raise ValueError("No more tiles in the wall")

    def deal_tiles(self):
        for _ in range(13):
            for player in self.players:
                player.add_tile(self.wall.pop())
        # 王牌の取り分け
        self.dead_wall = self.wall[-14:]
        self.wall = self.wall[:-14]

    def __repr__(self):
        return f"Game(players={self.players}, wall={len(self.wall)} tiles left)"
    
class AIPlayer(Hand):
    def choose_discard(self):
        # シンプルな戦略: ランダムに1枚捨てる
        return self.tiles.pop(np.random.randint(len(self.tiles)))

    def __repr__(self):
        sorted_tiles = sorted(self.tiles, key=lambda x: (x.suit, x.rank))
        return f"AIPlayer({sorted_tiles})"
    
class GameWithAI(Game):
    def __init__(self):
        super().__init__()
        self.players = [AIPlayer() for _ in range(4)]
        self.discards = [[] for _ in range(4)] 

    def is_wind_tile(self, tile):
        return tile.suit in ['東', '南', '西', '北']

    def play_turn(self, player_index):
        player = self.players[player_index]
        try:
            drawn_tile = self.draw_tile(player)
            print(f"プレイヤー {player_index} がツモった牌 {drawn_tile}")
            # ゲーム終了条件: 4面子1雀頭の形
            if player.is_valid_hand():
                print(f"プレイヤー {player_index} の手牌は4面子1雀頭の形です。")
                print(f"プレイヤー {player_index} の最終手牌: {player}")
                print("ゲーム終了")
                return True 
            discard = player.choose_discard()
            print(f"プレイヤー {player_index} が捨てる牌 {discard}")
            print(f"プレイヤー {player_index} の手牌: {player}")
            # 四風連打のチェック
            if len(self.discards[0]) == 1:
                first_discard = self.discards[0][0]
                if all(self.is_wind_tile(self.discards[i][0]) and self.discards[i][0].suit == first_discard.suit for i in range(4)):
                    print("四風連打が発生しました。ゲーム終了")
                    return True
        except ValueError as e:
            print(f"プレイヤー {player_index} がツモれません: {e}")

    def play_game(self):
        self.deal_tiles()
        turn = 0
        while len(self.wall) > 0:
            self.play_turn(turn % 4)
            turn += 1
        print("ゲーム終了")
        for i, player in enumerate(self.players):
            print(f"プレイヤー {i} の最終手牌: {player}")
        print(f"王牌: {self.dead_wall}")

if __name__ == "__main__":
    game = GameWithAI()
    game.play_game()