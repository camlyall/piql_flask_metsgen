from main import app
import unittest


class FlaskTestCase(unittest.TestCase):

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_metsgen(self):
        file_path_to_send = "sample_input/01538a96-c96e-4334-ad72-7934a7a22553/data/objects"
        tester = app.test_client(self)
        response = tester.post(f'/mets?filepath={file_path_to_send}')
        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
    