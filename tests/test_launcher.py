import unittest
from unittest.mock import patch

import launch


class LauncherTests(unittest.TestCase):
    def test_check_mode_does_not_start_jupyter(self):
        with patch.object(launch, "environment_errors", return_value=[]), patch.object(
            launch.subprocess, "run"
        ) as run:
            self.assertEqual(launch.main(["--check"]), 0)
            run.assert_not_called()

    def test_errors_prevent_launch(self):
        with patch.object(launch, "environment_errors", return_value=["missing"]), patch.object(
            launch.subprocess, "run"
        ) as run:
            self.assertEqual(launch.main([]), 1)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

