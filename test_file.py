import os
import app as flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    def test_delete(self):
        self.app.post('/add', data=dict(
            title='thing',
            text='stuff',
            category='A category'
        ), follow_redirects=True)

        rv = self.app.post('/delete', data=dict(
            title='thing',
            text='stuff',
            category='A category',
            id='1'
        ), follow_redirects=True)

        assert b'No entries here so far' in rv.data
        assert b'stuff' not in rv.data
        assert b'A category' not in rv.data
        assert b'thing' not in rv.data

    def test_filter(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        rb = self.app.post('/filter', data=dict(
            category='A category'
        ), follow_redirects=True)

        assert b'&lt;Hello&gt;' in rb.data
        assert b'<strong>HTML</strong> allowed here' in rb.data
        assert b'A category' in rb.data

        rz = self.app.post('/filter', data=dict(
            category='wrong category'
        ), follow_redirects=True)

        assert b'&lt;Hello&gt;' not in rz.data
        assert b'<strong>HTML</strong> allowed here' not in rz.data
        assert b'A category' not in rz.data

    def test_edit_page(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        rv = self.app.post('/edit', data=dict(
            id='1'
        ), follow_redirects=True)

        assert b'&lt;Hello&gt;' in rv.data
        assert b'&lt;strong&gt;HTML&lt;/strong&gt; allowed here' in rv.data
        assert b'A category' in rv.data

        rb = self.app.post('/edit', data=dict(
            id='2'
        ), follow_redirects=True)

        assert b'&lt;Hello&gt;' not in rb.data
        assert b'&lt;strong&gt;HTML&lt;/strong&gt; allowed here' not in rb.data
        assert b'A category' not in rb.data

    def test_edit(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        rv = self.app.post('/', data=dict(
            title='<Helloowi>',
            text='<strong>HTMLio</strong> allowed here',
            category='A categories',
            id='1'
        ), follow_redirects=True)

        assert b'&lt;Hello&gt;' not in rv.data
        assert b'&lt;strong&gt;HTML&lt;/strong&gt; allowed here' not in rv.data
        assert b'A category' not in rv.data

        assert b'&lt;Helloowi&gt;' in rv.data
        assert b'<strong>HTMLio</strong> allowed here' in rv.data
        assert b'A categories' in rv.data

    def test_return(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        self.app.post('/filter', data=dict(
            category='A category'
        ), follow_redirects=True)

        rv = self.app.post('/return', follow_redirects=True)

        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data


if __name__ == '__main__':
    unittest.main()
