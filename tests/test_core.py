import os
import shutil
import unittest

from py_path_component_case_conflict import Conflict, find_case_conflicts


class TestFindCaseConflicts(unittest.TestCase):
    def setUp(self) -> None:
        self._dirs: list[str] = []

    def tearDown(self) -> None:
        for d in reversed(self._dirs):
            shutil.rmtree(d, ignore_errors=True)

    def _mkdtemp(self) -> str:
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp_" + str(id(object())) + "_" + str(len(self._dirs)))
        os.makedirs(d)
        self._dirs.append(d)
        return d

    def test_no_conflicts_empty_dir(self) -> None:
        d = self._mkdtemp()
        self.assertEqual(find_case_conflicts(d), [])

    def test_no_conflicts_unique_names(self) -> None:
        d = self._mkdtemp()
        for name in ("alpha", "beta", "gamma"):
            open(os.path.join(d, name), "w").close()
        self.assertEqual(find_case_conflicts(d), [])

    def test_conflict_pair_is_sorted_by_name(self) -> None:
        d = self._mkdtemp()
        os.mkdir(os.path.join(d, "Index"))
        os.mkdir(os.path.join(d, "index"))
        result = find_case_conflicts(d)
        self.assertEqual(len(result), 1)
        conflict = result[0]
        self.assertEqual(conflict.base_dir, d)
        self.assertEqual(conflict.lower_form, "index")
        self.assertEqual(conflict.paths, ("Index", "index"))

    def test_conflict_includes_all_variants(self) -> None:
        d = self._mkdtemp()
        os.mkdir(os.path.join(d, "Readme"))
        os.mkdir(os.path.join(d, "README"))
        os.mkdir(os.path.join(d, "readme"))
        result = find_case_conflicts(d)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].paths, ("README", "Readme", "readme"))
        self.assertEqual(result[0].lower_form, "readme")

    def test_multiple_independent_conflicts(self) -> None:
        d = self._mkdtemp()
        os.mkdir(os.path.join(d, "Index"))
        os.mkdir(os.path.join(d, "index"))
        os.mkdir(os.path.join(d, "Images"))
        os.mkdir(os.path.join(d, "images"))
        result = find_case_conflicts(d)
        lowers = {c.lower_form for c in result}
        self.assertEqual(lowers, {"index", "images"})

    def test_non_ascii_conflict(self) -> None:
        d = self._mkdtemp()
        os.mkdir(os.path.join(d, "café"))
        os.mkdir(os.path.join(d, "Café"))
        result = find_case_conflicts(d)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].lower_form, "café")
        self.assertEqual(result[0].paths, ("Café", "café"))

    def test_files_and_directories_count_together(self) -> None:
        d = self._mkdtemp()
        os.mkdir(os.path.join(d, "Config"))
        open(os.path.join(d, "config"), "w").close()
        result = find_case_conflicts(d)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].paths, ("Config", "config"))

    def test_names_differing_only_in_first_letter(self) -> None:
        d = self._mkdtemp()
        open(os.path.join(d, "license"), "w").close()
        open(os.path.join(d, "License"), "w").close()
        result = find_case_conflicts(d)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].paths, ("License", "license"))

    def test_single_name_has_no_conflict(self) -> None:
        d = self._mkdtemp()
        open(os.path.join(d, "ONLY"), "w").close()
        self.assertEqual(find_case_conflicts(d), [])

    def test_nonexistent_directory_raises_filenotfounderror(self) -> None:
        missing = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "does_not_exist_xyzzy",
        )
        self.assertFalse(os.path.exists(missing))
        with self.assertRaises(FileNotFoundError):
            find_case_conflicts(missing)

    def test_file_path_raises_notadirectoryerror(self) -> None:
        d = self._mkdtemp()
        f = os.path.join(d, "regular_file")
        open(f, "w").close()
        with self.assertRaises(NotADirectoryError):
            find_case_conflicts(f)

    def test_conflict_is_frozen_dataclass(self) -> None:
        c = Conflict(base_dir="/x", lower_form="y", paths=("Y", "y"))
        with self.assertRaises(Exception):
            c.base_dir = "/z"  # type: ignore[misc]

    def test_subdirectories_are_not_recursed_into(self) -> None:
        d = self._mkdtemp()
        parent = os.path.join(d, "Parent")
        os.makedirs(os.path.join(parent, "Child"))
        os.makedirs(os.path.join(parent, "child"))
        result = find_case_conflicts(d)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
