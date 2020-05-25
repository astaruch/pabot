import sys
import tempfile
import textwrap
import unittest
import shutil
import subprocess
import os

class PabotArgfileTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.mkdir('{}/tests'.format(self.tmpdir))


    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _run_tests_with_argfile(self, testfile_path, testfile_content, argfile_path, argfile_content, datasources):
        robot_file = open('{}/{}'.format(self.tmpdir, testfile_path), 'w')
        robot_file.write(textwrap.dedent(testfile_content))
        robot_file.close()
        datasources_abs_paths = ''.join(['{}/{}'.format(self.tmpdir, datasource) for datasource in datasources])
        with open('{}/{}'.format(self.tmpdir, argfile_path), 'w') as f:
            f.write(textwrap.dedent(argfile_content))
        process = subprocess.Popen(
            [sys.executable, '-m' 'pabot.pabot',
            '--argumentfile1', '{}/{}'.format(self.tmpdir, argfile_path),
            datasources_abs_paths],
            cwd=self.tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return process.communicate(), process.returncode

    def test_argfile_without_datasource(self):
        testfile_path = 'tests/test.robot'
        testfile_content = """
        *** Test Cases ***
        Test 1
            Log     ${VALUE}
            Should Be True  ${VALUE} == 1
        """
        argfile_path = 'argfile.txt'
        argfile_content = """
        --variable VALUE:1
        """
        datasources = [testfile_path]

        (stdout, stderr), rc = self._run_tests_with_argfile(testfile_path, testfile_content, argfile_path, argfile_content, datasources)
        self.assertEqual(rc, 0)
        if sys.version_info < (3, 0):
            self.assertIn('PASSED', stdout)
        else:
            self.assertIn(b'PASSED', stdout)

    def test_argfile_with_datasource(self):
        testfile_path = 'tests/test.robot'
        testfile_content = """
        *** Test Cases ***
        Test 1
            Log     ${VALUE}
            Should Be True  ${VALUE} == 1
        """
        argfile_path = 'argfile.txt'
        argfile_content = """
        --variable VALUE:1
        # Path to the test should be relative to the pabot working directory
        {}
        """.format(testfile_path)
        datasources = []

        (stdout, stderr), rc = self._run_tests_with_argfile(testfile_path, testfile_content, argfile_path, argfile_content, datasources)
        self.assertEqual(rc, 0)
        if sys.version_info < (3, 0):
            self.assertIn('PASSED', stdout)
        else:
            self.assertIn(b'PASSED', stdout)
