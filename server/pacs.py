import os
import shutil
import time

class RemotePACS:
    """
    Simulates a remote PACS system. In the future, this will connect to a real PACS server.
    """

    def __init__(self, remote_url: str):
        """
        Initialize Remote PACS connection.

        :param remote_url: URL of the remote PACS server.
        """
        self.remote_url = remote_url  # Placeholder, replace with actual PACS connection

    def download_series(self, series_instance_uid: str, destination_folder: str) -> bool:
        """
        Simulates downloading a DICOM series from a remote PACS to the local system.

        :param series_instance_uid: The Series Instance UID of the requested series.
        :param destination_folder: The local folder where the series will be stored.
        :return: True if the download is successful, False otherwise.
        """
        print(f"[RemotePACS] Downloading series {series_instance_uid} from {self.remote_url}...")

        # Simulate a network delay for downloading
        time.sleep(2)

        # Simulate storing a fake DICOM file
        os.makedirs(destination_folder, exist_ok=True)
        fake_dicom_path = os.path.join(destination_folder, f"{series_instance_uid}.dcm")

        with open(fake_dicom_path, "w") as f:
            f.write("Fake DICOM content")  # Replace with actual DICOM download logic

        print(f"[RemotePACS] Download complete: {fake_dicom_path}")
        return True


class OrchestratorPACS:
    """
    Manages DICOM retrieval by first checking the local system, then falling back to RemotePACS.
    """

    def __init__(self, local_directory: str, remote_pacs: RemotePACS):
        """
        Initialize the Orchestrator PACS system.

        :param local_directory: The base directory where DICOM series are stored locally.
        :param remote_pacs: An instance of RemotePACS for downloading missing series.
        """
        if not os.path.isdir(local_directory):
            raise ValueError(f"Directory does not exist: {local_directory}")

        self.local_directory = local_directory
        self.remote_pacs = remote_pacs

    def _is_series_valid(self, series_path: str) -> bool:
        """
        Check if a DICOM series is valid by ensuring it contains at least one non-empty file.

        :param series_path: The folder path of the DICOM series.
        :return: True if the series contains at least one file > 0 bytes, False otherwise.
        """
        if not os.path.isdir(series_path):
            return False

        for file in os.listdir(series_path):
            file_path = os.path.join(series_path, file)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                return True  # Found a valid file

        return False  # No valid files found

    def get_series(self, series_instance_uid: str) -> str:
        """
        Retrieves a DICOM series from the local storage or downloads it from the remote PACS.

        :param series_instance_uid: The Series Instance UID of the requested series.
        :return: The path to the local folder containing the DICOM series.
        """
        series_path = os.path.join(self.local_directory, series_instance_uid)

        if self._is_series_valid(series_path):
            print(f"[OrchestratorPACS] Series {series_instance_uid} found locally.")
            return series_path

        print(f"[OrchestratorPACS] Series {series_instance_uid} not found locally or is incomplete. Fetching from RemotePACS...")

        success = self.remote_pacs.download_series(series_instance_uid, series_path)

        if success:
            return series_path
        else:
            raise RuntimeError(f"Failed to retrieve series {series_instance_uid} from RemotePACS.")
