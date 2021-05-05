import sqlite3

class Database:
    '''The database stores all the added songs and their paths'''
    
    def __init__(self, db_file):
        self.connection = None
        try:
            # Creating the connection with the database
            self.connection = sqlite3.connect(db_file)
            self.my_cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(e)  # Print the error if any

        with self.connection:  # Making the connection
            # Creating the main song table
            self.my_cursor.execute('CREATE TABLE IF NOT EXISTS Audio (audio text, audio_path text);')

    def insert_in_table(self, audio):
        try:
            with self.connection:
                sql = 'INSERT INTO Audio(audio, audio_path) VALUES(?,?)'
                # Executing the insertion statement
                self.my_cursor.execute(sql, audio)
                # Saving the changes
                self.connection.commit()
        except sqlite3.ProgrammingError:
            print("Can't add nothing")

    def extract_audio(self, audio_name=''):
        with self.connection:
            # Next, we make the sql statement so that we avoid SQL Injections
            sql = "SELECT * FROM Audio WHERE audio LIKE '%'||?||'%'"
            self.my_cursor.execute(sql, (audio_name,))
            audio = self.my_cursor.fetchall()
        return audio

    def delete_audio(self, audio):
        with self.connection:
            sql = "DELETE FROM Audio WHERE audio = ?"
            self.my_cursor.execute(sql, (audio,))
            self.connection.commit()