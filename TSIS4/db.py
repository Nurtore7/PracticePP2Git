import psycopg2
from datetime import datetime

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host='localhost',
                database='snake_game',
                user='postgres',
                password='Nurtore2008'
            )
            self.cursor = self.conn.cursor()
            print("✓ Database connected!")
        except Exception as e:
            print(f"✗ Database error: {e}")
            self.conn = None
            self.cursor = None
    
    def get_or_create_player(self, username):
        if not self.cursor:
            return 1
        try:
            self.cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                self.cursor.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
                player_id = self.cursor.fetchone()[0]
                self.conn.commit()
                return player_id
        except:
            return 1
    
    def save_game_session(self, player_id, score, level_reached):
        if not self.cursor:
            return
        try:
            self.cursor.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                (player_id, score, level_reached)
            )
            self.conn.commit()
        except:
            pass
    
    def get_leaderboard(self):
        if not self.cursor:
            return []
        try:
            self.cursor.execute("""
                SELECT p.username, gs.score, gs.level_reached, gs.played_at
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            return self.cursor.fetchall()
        except:
            return []
    
    def get_personal_best(self, player_id):
        if not self.cursor:
            return 0
        try:
            self.cursor.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s", (player_id,))
            result = self.cursor.fetchone()
            return result[0] if result[0] else 0
        except:
            return 0
    
    def close(self):
        if self.conn:
            self.conn.close()