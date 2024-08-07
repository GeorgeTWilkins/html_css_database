from flask import Flask, render_template, request, redirect, url_for
import sqlite3

DATABASE = 'dndspells.db'

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/spell-view')
def spell_view():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('SELECT spell_name, spell_level FROM spell ORDER BY spell_level, spell_name ASC')
    level_to_spells = []
    #Store spells in a list where all cantrips are assigned to 0, level one to 1 etc.
    for name, level in cursor.fetchall():
        level = int(level)
        while level >= len(level_to_spells):
            level_to_spells.append([])
        level_to_spells[level].append(name)
    return render_template('spell_view.html', spells = level_to_spells)

if __name__ == '__main__':
    app.run(debug=True)