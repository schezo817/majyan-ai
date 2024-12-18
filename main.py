import numpy as np
from collections import Counter

# 牌の定義
class Tile:
    def __init__(self, suit, rank):
        self.suit = suit  # 萬, 筒, 索, 東, 南, 西, 北, 白, 發, 中
        self.rank = rank  # 1-9 (萬, 筒, 索), 1 (東, 南, 西, 北, 白, 發, 中)

    def __repr__(self):
        return f"{self.suit}{self.rank}"

# 手牌の定義    
class Hand:
    def __init__(self):
        self.tiles = [] # 手牌
        self.role = Role()

    # 手牌に牌を追加
    def add_tile(self, tile):
        self.tiles.append(tile) 

    # 手牌から牌を削除
    def remove_tile(self, tile):
        self.tiles.remove(tile)

    # 手牌が4面子1雀頭の形を成しているかどうかを判定
    def is_valid_hand(self):
        # 手牌の牌の種類と枚数を数える
        tile_counts = Counter((tile.suit, tile.rank) for tile in self.tiles)
        pairs = [tile for tile, count in tile_counts.items() if count >= 2]

        for pair in pairs:
            remaining_tiles = []
            for tile in self.tiles:
                if (tile.suit, tile.rank) == pair and tile_counts[pair] > 0:
                    tile_counts[pair] -= 1
                else:
                    remaining_tiles.append(tile)
            if self.role.can_form_melds(remaining_tiles):
                return True
        return False

    def __repr__(self):
        return f"Hand({self.tiles})"
    
#　役の定義
class Role:
    # 面子の判定
    def is_sequence(self,tiles):
        return len(tiles) == 3 and tiles[0].rank + 1 == tiles[1].rank and tiles[1].rank + 1 == tiles[2].rank

    # 刻子の判定
    def is_triplet(self, tiles):
        return len(tiles) == 3 and tiles[0].rank == tiles[1].rank == tiles[2].rank
    
    # 4面子1雀頭の形を成しているかどうかを再帰的に判定
    def can_form_melds(self, tiles):
        if len(tiles) == 0:
            return True
        if len(tiles) < 3:
            return False
        tiles.sort(key=lambda x: (x.suit, x.rank))
        for i in range(len(tiles) - 2):
            if self.is_sequence(tiles[i:i+3]) or self.is_triplet(tiles[i:i+3]):
                new_tiles = tiles[:i] + tiles[i+3:]
                if  self.can_form_melds(new_tiles):
                    return True
            return False

    # 七対子の判定
    def is_seven_pairs(tiles):
        if len(tiles) != 14:
            return False
        tile_counts = Counter((tile.suit, tile.rank) for tile in tiles)
        return all(count == 2 for count in tile_counts.values())
    
    # 国士無双の判定
    def is_thirteen_orphans(tiles):
        if len(tiles) != 14:
            return False
        required_tiles = set([
            ('萬', 1), ('萬', 9),
            ('筒', 1), ('筒', 9),
            ('索', 1), ('索', 9),
            ('東', 1), ('南', 1), ('西', 1), ('北', 1),
            ('白', 1), ('發', 1), ('中', 1)
        ])
        tile_counts = Counter((tile.suit, tile.rank) for tile in tiles)
        tile_set = set(tile_counts.keys())
        # 必要な牌がすべて含まれているかをチェック
        if not required_tiles.issubset(tile_set):
            return False
        # 必要な牌が13種類であり、かつもう1枚同じ牌が含まれているかをチェック
        return len(tile_set) == 13 and any(count == 2 for count in tile_counts.values())

# ゲームの定義 
class Game:
    def __init__(self):
        self.players = [Hand() for _ in range(4)]
        self.wall = self.create_wall()
        self.dead_wall = []

    # 牌山の生成
    def create_wall(self):
        suits = ['萬', '筒', '索']
        ranks = list(range(1, 10))
        honors = ['東', '南', '西', '北', '白', '發', '中']
        wall = [Tile(suit, rank) for suit in suits for rank in ranks] * 4
        wall += [Tile(honor, 1) for honor in honors] * 4
        np.random.shuffle(wall)
        return wall
    
    # 牌をツモ
    def draw_tile(self, player):
        if len(self.wall) > 0:
            tile = self.wall.pop()
            player.add_tile(tile)
            return tile
        else:
            raise ValueError("No more tiles in the wall")

    # 牌を配る
    def deal_tiles(self):
        for _ in range(13):
            for player in self.players:
                player.add_tile(self.wall.pop())
        # 王牌の取り分け
        self.dead_wall = self.wall[-14:]
        self.wall = self.wall[:-14]

    def __repr__(self):
        return f"Game(players={self.players}, wall={len(self.wall)} tiles left)"
    
# AIプレイヤーの定義
class AIPlayer(Hand):
    # 捨てる牌を選ぶ
    def choose_discard(self):
        # シンプルな戦略: ランダムに1枚捨てる
        return self.tiles.pop(np.random.randint(len(self.tiles)))

    def __repr__(self):
        sorted_tiles = sorted(self.tiles, key=lambda x: (x.suit, x.rank))
        return f"AIPlayer({sorted_tiles})"

# AIを使ったゲームの定義    
class GameWithAI(Game):
    def __init__(self):
        super().__init__()
        self.players = [AIPlayer() for _ in range(4)]
        self.discards = [[] for _ in range(4)] 

    # 風牌かどうかを判定
    def is_wind_tile(self, tile):
        return tile.suit in ['東', '南', '西', '北']
    
    # ゲーム終了条件のチェック
    def check_game_end(self, player_index):
        player = self.players[player_index]
        # ゲーム終了条件: 4面子1雀頭の形
        if player.is_valid_hand():
            print(f"プレイヤー {player_index} の手牌は4面子1雀頭の形です。")
            print(f"プレイヤー {player_index} の最終手牌: {player}")
            print("ゲーム終了")
            return True
        # ゲーム終了条件: 七対子
        if Role.is_seven_pairs(player.tiles):
            print(f"プレイヤー {player_index} の手牌は七対子です。")
            print(f"プレイヤー {player_index} の最終手牌: {player}")
            print("ゲーム終了")
            return True
        # ゲーム終了条件: 国士無双
        if Role.is_thirteen_orphans(player.tiles):
            print(f"プレイヤー {player_index} の手牌は国士無双です。")
            print(f"プレイヤー {player_index} の最終手牌: {player}")
            print("ゲーム終了")
            return True
        return False
    
    # 四風連打のチェック
    def check_four_wind_discards(self):
        if len(self.discards[0]) == 1:
            first_discard = self.discards[0][0]
            if all(self.is_wind_tile(self.discards[i][0]) and self.discards[i][0].suit == first_discard.suit for i in range(4)):
                print("四風連打が発生しました。ゲーム終了")
                return True
        return False


    # ターンのプレイ
    def play_turn(self, player_index):
        player = self.players[player_index]
        try:
            drawn_tile = self.draw_tile(player)
            print(f"プレイヤー {player_index} がツモった牌 {drawn_tile}")
            # あがったらゲーム終了
            if self.check_game_end(player_index):
                return True
            discard = player.choose_discard()
            print(f"プレイヤー {player_index} が捨てる牌 {discard}")
            print(f"プレイヤー {player_index} の手牌: {player}")
            if self.check_four_wind_discards():
                return True
        except ValueError as e:
            print(f"プレイヤー {player_index} がツモれません: {e}")

    # ゲームのプレイ
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