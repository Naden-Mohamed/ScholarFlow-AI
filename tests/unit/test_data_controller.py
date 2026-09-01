from unittest.mock import MagicMock, patch

import pytest

from src.controllers.DataController import DataController
from src.models.Enums.ResponseEnum import ResponseStatus

pytestmarker = pytest.mark.unit


@pytest.fixture
def data_controller():
    return DataController()


class TestDataController:
    def test_reject_not_allowed_filetype(self, data_controller):
        fake_file = MagicMock(content_type="application/x-msdownload", size=1000)
        result, status = data_controller.validate_uploaded_file(file=fake_file)
        assert result == False
        assert status == ResponseStatus.FILE_TYPE_NOT_SUPPORTED.value

    def test_rejects_oversize_file(self, data_controller):
        oversize = 11 * 1024 * 1024
        fake_file = MagicMock(content_type="application/pdf", size=oversize)
        result, status = data_controller.validate_uploaded_file(file=fake_file)
        assert result == False
        assert status == ResponseStatus.FILE_SIZE_EXCEEDED.value

    def test_rejects_file_without_size_defined(self, data_controller):
        fake_file = MagicMock(content_type="application/pdf", size=None)
        result, _ = data_controller.validate_uploaded_file(file=fake_file)
        assert result == False

    def test_generated_filename_has_random_prefix(self, data_controller):
        _, unique_file_name = data_controller.generate_unique_filename(
            original_filename="test.pdf",
            project_id="5",
        )
        assert unique_file_name.endswith("_test.pdf")
        random_prefix = unique_file_name.split("_")[0]
        assert len(random_prefix) == 8

    def test_filename_is_sanitized(self, data_controller):
        result = data_controller.get_clean_file_name("my research paper! @2026#.pdf")

        assert result == "myresearchpaper2026.pdf"

    def test_generate_unique_filename(self, data_controller):
        with patch(
            "controllers.DataController.ProjectController"
        ) as project_controller:
            project_controller.return_value.get_project_path.return_value = (
                "tmp/project"
            )

        with (
            patch.object(
                data_controller, "generate_random_strings", return_value="abc12345"
            ),
            patch("os.path.exists", return_value=False),
        ):
            full_path, file_id = data_controller.generate_unique_filename(
                original_filename="paper.pdf",
                project_id="project-1",
            )

        assert file_id == "abc123_paper.pdf"
        assert "paper.pdf" in full_path

    @pytest.mark.parametrize(
        "malicious_name",
        [
            "../../etc/passwd",
            "../../../secrets.env",
            "..\\..\\windows\\system32\\config",
            "/etc/passwd",
        ],
    )
    def test_path_traversal_is_stripped(self, data_controller, malicious_name):
        result = data_controller.generate_unique_filename(
            original_filename=malicious_name,
            project_id="5",
        )
        assert "/" not in result
        assert "\\" not in result
        assert ".." not in result

    def test_none_filename_does_not_crash(self, data_controller):
        result = data_controller.generate_unique_filename(
            None,
            project_id="5",
        )
        return result
