import importlib.machinery
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


AXE_PATH = Path(__file__).resolve().parents[1] / "axe"
LOADER = importlib.machinery.SourceFileLoader("axe_module", str(AXE_PATH))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
axe = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(axe)


class AxeTests(unittest.TestCase):
    def test_resolve_host_accepts_short_number(self):
        self.assertEqual(axe.resolve_host("12"), "192.222.1.12")

    def test_resolve_host_accepts_ipv4(self):
        self.assertEqual(axe.resolve_host("10.0.0.8"), "10.0.0.8")

    def test_resolve_host_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            axe.resolve_host("999")

    def test_normalize_destination_defaults_to_source_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "demo.txt"
            file_path.write_text("demo", encoding="utf-8")
            self.assertEqual(axe.normalize_destination(str(file_path), None), temp_dir + "/")

    def test_normalize_destination_maps_home_directory_to_tilde(self):
        with mock.patch.dict(os.environ, {"HOME": "/tmp/demo-home"}, clear=False):
            self.assertEqual(axe.normalize_destination("demo.txt", "/tmp/demo-home"), "~")

    def test_main_reports_missing_copy_source(self):
        with mock.patch("builtins.print") as mocked_print:
            exit_code = axe.main(["1", "-s", "missing-file"])
        self.assertEqual(exit_code, 1)
        mocked_print.assert_called_with("Failed. No such file or directory: missing-file")


if __name__ == "__main__":
    unittest.main()
