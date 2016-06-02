__author__ = '$USER'
import logging
import unittest


logging.basicConfig(level=logging.DEBUG)

#set( $TestCaseName = $NAME.replace("Test", "") )
class ${TestCaseName}TestCase(unittest.TestCase):
    def test_01(self):
        $END

if __name__ == '__main__':
    unittest.main()
