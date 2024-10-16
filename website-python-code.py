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

@app.route('/add-spell-input')
def add_spell_input():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('''
            SELECT class_name FROM user ORDER BY class_name ASC
               ''')
    classes = cursor.fetchall()
    cursor.execute('''
        SELECT school_name FROM school ORDER BY school_name ASC
           ''')
    schools = cursor.fetchall()
    return render_template('add_spell.html', schools=schools, classes=classes)

@app.route('/add_spell_save', methods = ['GET'])
def add_spell_save():  
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    #Try and except so that if someone enters a duplicate spell name, it won't work
    try:
        if request.method == 'GET':
            spl, spn, desc, ahl, sch, cls = request.args.get('spl'), request.args.get('spn'), request.args.get('desc'), request.args.get('ahl'), request.args.get('sch'), request.args.getlist('cls')
            sql_spell = '''
                INSERT INTO spell (spell_level, spell_name, description, at_higher_levels) 
                VALUES (?, ?, ?, ?);
            ''', (spl, spn, desc, ahl)
            cursor.execute(*sql_spell)
            #If multiple classes have been added it will loop through and add them all
            if len(cls) > 0:
                for i in range(len(cls)):
                    sql_class = '''
                        INSERT INTO spell_user (spell_id, user_id)
                        VALUES ((SELECT id FROM spell WHERE spell_name = ?), (SELECT id FROM user WHERE class_name = ?))
                    ''', (spn, cls[i])
                    cursor.execute(*sql_class)
                sql_school = '''
                    INSERT INTO spell_school (spell_id, school_id)
                    VALUES ((SELECT id FROM spell WHERE spell_name = ?), (SELECT id FROM school WHERE school_name = ?))
                ''', (spn, sch)
                cursor.execute(*sql_school)
                #Make sure that at_higher_levels is NULL if need be
                cursor.execute('''
                    UPDATE spell 
                    SET at_higher_levels = NULL 
                    WHERE at_higher_levels = '';
                ''')
                db.commit()
                #Make it so they can view their spell once they are done.
                return redirect(url_for('single_spell', spell=spn))
            else:
                return redirect(url_for('home_page'))#failed
    except: #Not a great thing because if something else breaks, it will still go here
        return redirect(url_for('single_spell', spell=spn))#failed
        
    else:
        # This should never happen, but just incase
        schools = ['Abjuration', 'Conjuration', 'Divination', 'Enchantment', 'Evocation', 'Illusion', 'Necromancy', 'Transmutation']
        return render_template('add_spell_input.html', schools=schools)


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