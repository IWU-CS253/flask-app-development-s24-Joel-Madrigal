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
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        rv = self.app.post('/delete', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category',
            id='1'
        ), follow_redirects=True)

        assert b'No entries here so far' in rv.data
        assert b'&lt;Hello&gt;' not in rv.data

    def test_filter(self):
        self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        rb = self.app.post('/filter', data=dict(
            category='A category'
        ), follow_redirects=True)

        assert b'Unbelievable.  No entries here so far' not in rb.data
        assert b'<strong>HTML</strong> allowed here' in rb.data
        assert b'A category' in rb.data

        rz = self.app.post('/filter', data=dict(
            category='wrong category'
        ), follow_redirects=True)

        assert b'Unbelievable.  No entries here so far' in rz.data
        assert b'<strong>HTML</strong> allowed here' not in rz.data
        assert b'A category' not in rz.data


if __name__ == '__main__':
    unittest.main()
