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

    def test_resolve_host_uses_configured_prefix(self):
        with mock.patch.object(axe, "HOST_PREFIX", "10.20.30."):
            self.assertEqual(axe.resolve_host("12"), "10.20.30.12")

    def test_connect_timeout_comes_from_environment_on_reload(self):
        with mock.patch.dict(os.environ, {"AXE_CONNECT_TIMEOUT": "21"}, clear=False):
            loader = importlib.machinery.SourceFileLoader("axe_module_timeout", str(AXE_PATH))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            reloaded = importlib.util.module_from_spec(spec)
            loader.exec_module(reloaded)
        self.assertEqual(reloaded.CONNECT_TIMEOUT, 21)

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

    def test_getwinsize_falls_back_without_tty(self):
        with mock.patch.object(axe.sys.stdout, "fileno", side_effect=OSError):
            self.assertEqual(axe.getwinsize(), (24, 80))

    def test_help_flag_prints_help(self):
        with mock.patch("builtins.print") as mocked_print:
            exit_code = axe.main(["--help"])
        self.assertEqual(exit_code, 0)
        mocked_print.assert_called_once_with(axe.HELP, end="")

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

    def test_print_batch_summary_without_failures(self):
        with mock.patch("builtins.print") as mocked_print:
            exit_code = axe.print_batch_summary("command execution", ["2", "3"], [])
        self.assertEqual(exit_code, 0)
        mocked_print.assert_any_call("Completed command execution on all hosts.")
        mocked_print.assert_any_call("Summary: total=2, succeeded=2, failed=0")

    def test_print_batch_summary_with_failures(self):
        failures = [{"host": "2", "error": "timeout"}, {"host": "4", "error": "auth failed"}]
        with mock.patch("builtins.print") as mocked_print:
            exit_code = axe.print_batch_summary("SCP", ["2", "3", "4"], failures)
        self.assertEqual(exit_code, 1)
        mocked_print.assert_any_call("Completed SCP with failures on: 2, 4")
        mocked_print.assert_any_call("Summary: total=3, succeeded=1, failed=2")
        mocked_print.assert_any_call("  2: timeout")
        mocked_print.assert_any_call("  4: auth failed")

    def test_run_command_continues_after_host_failure(self):
        with mock.patch.object(axe, "astute_ssh", side_effect=[RuntimeError("timeout"), None]) as ssh_mock, \
             mock.patch("builtins.print") as mocked_print:
            exit_code = axe.run_command(["2", "3"], ["hostname"])
        self.assertEqual(exit_code, 1)
        self.assertEqual(ssh_mock.call_count, 2)
        mocked_print.assert_any_call("Completed command execution with failures on: 2")

    def test_run_scp_continues_after_host_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "demo.txt"
            file_path.write_text("demo", encoding="utf-8")
            with mock.patch.object(axe, "astute_scp", side_effect=[RuntimeError("timeout"), None]) as scp_mock, \
                 mock.patch("builtins.print") as mocked_print:
                exit_code = axe.run_scp(["2", "3"], [str(file_path)])
        self.assertEqual(exit_code, 1)
        self.assertEqual(scp_mock.call_count, 2)
        mocked_print.assert_any_call("Completed SCP with failures on: 2")

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

    def test_expect_and_send_password_uses_configured_timeout(self):
        child = mock.Mock()
        child.expect.return_value = 0
        with mock.patch.object(axe, "CONNECT_TIMEOUT", 27):
            axe.expect_and_send_password(child, "secret")
        child.expect.assert_called_once_with(
            [r"[Pp]assword:", r"Permission denied", r"Connection refused", r"No route to host", axe.pexpect.EOF, axe.pexpect.TIMEOUT],
            timeout=27,
        )
        child.sendline.assert_called_once_with("secret")

    def test_expect_and_send_password_classifies_auth_failure(self):
        child = mock.Mock()
        child.expect.return_value = 1
        with self.assertRaisesRegex(RuntimeError, "Authentication failed"):
            axe.expect_and_send_password(child, "secret")

    def test_expect_and_send_password_classifies_connection_refused(self):
        child = mock.Mock()
        child.expect.return_value = 2
        with self.assertRaisesRegex(RuntimeError, "Connection refused"):
            axe.expect_and_send_password(child, "secret")

    def test_wait_for_child_classifies_remote_close(self):
        child = mock.Mock()
        child.expect.return_value = 1
        with self.assertRaisesRegex(RuntimeError, "Connection closed by remote host"):
            axe.wait_for_child(child)
        child.close.assert_called_once()

    def test_wait_for_child_classifies_timeout(self):
        child = mock.Mock()
        child.expect.return_value = 3
        with self.assertRaisesRegex(RuntimeError, "Timed out waiting for remote command to finish"):
            axe.wait_for_child(child)
        child.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
