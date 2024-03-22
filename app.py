# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute(
        'select id, title, text, category from entries order by id desc')
    entries = cur.fetchall()
    cur = db.execute('select distinct category from entries')
    categories = cur.fetchall()
    return render_template('show_entries.html', entries=entries, categories=categories)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (title, text, category) values (?, ?, ?)',
               [request.form['title'], request.form['text'], request.form['category']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/filter', methods=['POST'])
def filter_posts():
    db = get_db()
    cur = db.execute('select id, title, text, category from entries where category = ?', [
                     request.form['category']])
    category = cur.fetchall()
    return render_template('filtered_entries.html', category=category)


@app.route('/delete', methods=['POST'])
def delete_entry():
    db = get_db()
    db.execute('delete from entries where id = ?',
               [request.form['id']])
    db.commit()
    flash('Post was deleted')
    return redirect(url_for('show_entries'))


@app.route('/edit', methods=['POST'])
def new_page():
    locate = request.form['id']
    db = get_db()
    cur = db.execute('select title, text, category, id from entries where id = ?',
                     [locate])
    locate = cur.fetchone()
    return render_template('edit_page.html', locate=locate)


@app.route('/', methods=['POST'])
def update_edit():
    db = get_db()
    db.execute('update entries set title = ?, text = ?, category = ? where id = ?',
               [request.form['title'], request.form['text'], request.form['category'],
                request.form['id']])
    db.commit()
    return redirect(url_for('show_entries'))


@app.route('/return', methods=['POST'])

def return_to():
    return redirect(url_for('show_entries'))



