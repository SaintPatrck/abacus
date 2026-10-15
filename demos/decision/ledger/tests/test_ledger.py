import json
import os
import subprocess
import sys
import tempfile
import unittest


def ledger(*args, env):
    return subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, env=env)


class LedgerTest(unittest.TestCase):
    def test_add_then_list(self):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, LEDGER_FILE=os.path.join(d, "l.json"))
            ledger("add", "12.5", "lunch", env=env)
            ledger("add", "3", "coffee", env=env)
            out = ledger("list", env=env).stdout
            self.assertIn("12.50  lunch", out)
            self.assertIn("3.00  coffee", out)


if __name__ == "__main__":
    unittest.main()
