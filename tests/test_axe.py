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

    def test_main_rejects_command_without_hosts(self):
        with mock.patch("builtins.print") as mocked_print:
            exit_code = axe.main(["-c", "hostname"])
        self.assertEqual(exit_code, 1)
        mocked_print.assert_called_with("Failed. No host specified for command execution.")

    def test_main_rejects_scp_without_hosts(self):
        with mock.patch("builtins.print") as mocked_print:
            exit_code = axe.main(["-s", "demo.txt"])
        self.assertEqual(exit_code, 1)
        mocked_print.assert_called_with("Failed. No host specified for SCP.")

    def test_ssh_command_mode_waits_for_completion(self):
        child = mock.Mock()
        with mock.patch.object(axe.pexpect, "spawn", return_value=child) as spawn_mock, \
             mock.patch.object(axe, "expect_and_send_password") as expect_mock, \
             mock.patch.object(axe, "wait_for_child") as wait_mock, \
             mock.patch.object(axe, "interact_with_child") as interact_mock:
            axe.ssh("root", "secret", "10.0.0.8", command="hostname")

        spawn_mock.assert_called_once()
        expect_mock.assert_called_once_with(child, "secret")
        wait_mock.assert_called_once_with(child)
        interact_mock.assert_not_called()
        self.assertIs(child.logfile_read, axe.sys.stdout)

    def test_scp_waits_for_completion(self):
        child = mock.Mock()
        with mock.patch.object(axe.pexpect, "spawn", return_value=child) as spawn_mock, \
             mock.patch.object(axe, "expect_and_send_password") as expect_mock, \
             mock.patch.object(axe, "wait_for_child") as wait_mock:
            axe.scp("root", "secret", "10.0.0.8", "demo.txt", destination="/tmp")

        spawn_mock.assert_called_once()
        expect_mock.assert_called_once_with(child, "secret")
        wait_mock.assert_called_once_with(child)
        self.assertIs(child.logfile_read, axe.sys.stdout)


if __name__ == "__main__":
    unittest.main()
