import contextlib
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import pikepdf

import unlock_pdf


class UnlockTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "protected.pdf"

    def make_pdf(self, password=""):
        pdf = pikepdf.new()
        pdf.add_blank_page()
        pdf.save(
            self.path,
            encryption=pikepdf.Encryption(owner="owner", user=password),
        )
        pdf.close()

    def test_double_click_keeps_result_visible(self):
        self.make_pdf()
        with (
            mock.patch.object(sys, "argv", ["unlock_pdf.exe"]),
            mock.patch.object(sys, "frozen", True, create=True),
            mock.patch.object(unlock_pdf, "choose_file", return_value=str(self.path)),
            mock.patch.object(unlock_pdf, "pause") as pause,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(unlock_pdf.main(), 0)
        pause.assert_called_once()
        with pikepdf.open(self.path) as pdf:
            self.assertFalse(pdf.is_encrypted)

    def test_password_failure_is_visible_and_returns_failure(self):
        self.make_pdf("secret")
        with (
            mock.patch.object(sys, "argv", ["unlock_pdf.exe", str(self.path)]),
            mock.patch.object(sys, "frozen", True, create=True),
            mock.patch.object(unlock_pdf, "pause") as pause,
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(unlock_pdf.main(), 1)
        pause.assert_called_once()
        self.assertIn("FAIL", output.getvalue())
        with pikepdf.open(self.path, password="secret") as pdf:
            self.assertTrue(pdf.is_encrypted)

    def test_existing_backup_is_not_overwritten(self):
        self.make_pdf()
        backup = self.path.with_name("protected.locked.pdf")
        backup.write_bytes(b"existing backup")
        self.assertTrue(unlock_pdf.unlock(self.path, backup=True).startswith("FAIL"))
        self.assertEqual(backup.read_bytes(), b"existing backup")
        with pikepdf.open(self.path) as pdf:
            self.assertTrue(pdf.is_encrypted)
        self.assertEqual(set(Path(self.directory.name).iterdir()), {self.path, backup})

    def test_missing_path_returns_failure(self):
        with (
            mock.patch.object(sys, "argv", ["unlock_pdf.py", str(self.path)]),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()) as output,
        ):
            self.assertEqual(unlock_pdf.main(), 1)
        self.assertIn("找不到 PDF", output.getvalue())

    def test_python_context_menu_runs_the_script(self):
        registry = types.SimpleNamespace(
            HKEY_CURRENT_USER=object(),
            REG_SZ=1,
            CreateKeyEx=mock.MagicMock(),
            SetValueEx=mock.MagicMock(),
        )
        with (
            mock.patch.object(sys, "platform", "win32"),
            mock.patch.dict(sys.modules, {"winreg": registry}),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertTrue(unlock_pdf.context_menu(True))
        commands = [
            call.args[4]
            for call in registry.SetValueEx.call_args_list
            if "--pause" in call.args[4]
        ]
        self.assertEqual(len(commands), 3)
        self.assertIn(f'"{Path(unlock_pdf.__file__).resolve()}"', commands[0])


if __name__ == "__main__":
    unittest.main()
