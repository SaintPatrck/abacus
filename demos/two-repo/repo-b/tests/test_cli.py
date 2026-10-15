import os
import subprocess
import sys
import tempfile
import unittest


class CliTest(unittest.TestCase):
    def test_lines(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("a\nb\n")
        out = subprocess.run([sys.executable, "-m", "wcreport", f.name], capture_output=True, text=True).stdout
        os.unlink(f.name)
        self.assertEqual(out.strip(), "2 lines")


if __name__ == "__main__":
    unittest.main()
