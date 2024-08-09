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


@app.route('/spell/<spell>')
def single_spell(spell):
    #Have header in a list so looping is cleaner in the html part
    single_spell_header = ['Level: ', 'Name: ', 'Description: ', 'At higher levels: ', 'School: ', 'Classes: ']
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = ('''
        SELECT spell_level AS 'Level', spell_name AS 'Name' , description AS 'Description', at_higher_levels AS 'At higher levels', school_name AS 'School', GROUP_CONCAT(class_name, ', ') AS 'Class name'
        FROM spell_user
        JOIN spell_school ON spell_user.spell_id= spell_school.spell_id
        JOIN user ON spell_user.user_id = user.id
        JOIN spell ON spell_user.spell_id = spell.id
        JOIN school on spell_school.school_id=school.id
        WHERE spell_name = ?
        GROUP BY spell_name
        ORDER BY spell_level
    ''', (spell, ))
    cursor.execute(*sql)
    ret = cursor.fetchone()
    return render_template('single_spell.html', details = ret, single_spell_header = single_spell_header)



if __name__ == '__main__':
    app.run(debug=True)