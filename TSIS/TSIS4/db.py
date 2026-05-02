import psycopg2
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        if self.conn:
            self.create_tables()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="phonebook_db",
                user="postgres",
                password="210807",
                port="5432"
            )
            self.conn.autocommit = True
            print("✓ Database connected successfully!")
            return True
        except Exception as e:
            print(f"✗ Database connection error: {e}")
            self.conn = None
            return False
    
    def create_tables(self):
        """Create game tables"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES game_players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            self.conn.commit()
            cursor.close()
            print("✓ Game tables created/verified")
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
    
    def get_or_create_player(self, username):
        """Get existing player or create new one"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM game_players WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result:
                player_id = result[0]
            else:
                cursor.execute("INSERT INTO game_players (username) VALUES (%s) RETURNING id", (username,))
                player_id = cursor.fetchone()[0]
            
            self.conn.commit()
            cursor.close()
            return player_id
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def save_game_result(self, username, score, level):
        """Save game result to database"""
        if not self.conn:
            return False
        
        player_id = self.get_or_create_player(username)
        if not player_id:
            return False
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO game_sessions (player_id, score, level_reached, played_at)
                VALUES (%s, %s, %s, %s)
            """, (player_id, score, level, datetime.now()))
            
            self.conn.commit()
            cursor.close()
            print(f"✓ Saved: {username} - Score: {score}")
            return True
        except Exception as e:
            print(f"✗ Error saving: {e}")
            return False
    
    def get_leaderboard(self, limit=10):
        """Get top 10 scores"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT gp.username, gs.score, gs.level_reached, gs.played_at
                FROM game_sessions gs
                JOIN game_players gp ON gs.player_id = gp.id
                ORDER BY gs.score DESC
                LIMIT %s
            """, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"✗ Error: {e}")
            return []
    
    def get_personal_best(self, username):
        """Get player's best score"""
        if not self.conn:
            return 0
        
        player_id = self.get_or_create_player(username)
        if not player_id:
            return 0
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT MAX(score) FROM game_sessions
                WHERE player_id = %s
            """, (player_id,))
            
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result and result[0] else 0
        except Exception as e:
            print(f"✗ Error: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")