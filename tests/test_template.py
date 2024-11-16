import unittest


class TestTemplate(unittest.TestCase):
    def setUp(self):
        pass

    def test_hello_world(self):
        self.assertEqual("Hello, world!", "Hello, world!")


if __name__ == "__main__":
    unittest.main()
