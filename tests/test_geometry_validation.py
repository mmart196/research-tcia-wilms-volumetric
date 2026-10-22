"""Protect intended-ROI selection when an RTSTRUCT contains other targets."""
import sys
import tempfile
import unittest
from pathlib import Path

import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, RTStructureSetStorage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from validate_geometry import validate


class IntendedRoiValidationTests(unittest.TestCase):
    def test_target_identity_is_checked_and_another_roi_is_not_added(self):
        ds = Dataset()
        ds.file_meta = FileMetaDataset()
        ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = RTStructureSetStorage
        ds.file_meta.MediaStorageSOPInstanceUID = "1.2.3.8"
        ds.SOPClassUID = RTStructureSetStorage
        ds.SOPInstanceUID = "1.2.3.8"
        ds.SeriesInstanceUID = "1.2.3.4"
        target, decoy = Dataset(), Dataset()
        target.ROINumber, target.TrackingUID, target.ROIVolume = 2, "2.25.123", .4
        decoy.ROINumber, decoy.TrackingUID, decoy.ROIVolume = 1, "2.25.456", 900
        ds.StructureSetROISequence = [decoy, target]
        roi = Dataset()
        roi.ReferencedROINumber = 2
        contours = []
        for z in [0, 2]:
            c = Dataset()
            c.ContourGeometricType = "CLOSED_PLANAR"
            c.NumberOfContourPoints = 4
            c.ContourData = [0, 0, z, 10, 0, z, 10, 10, z, 0, 10, z]
            contours.append(c)
        roi.ContourSequence = contours
        ds.ROIContourSequence = [roi]
        row = {"series_uid": "1.2.3.4", "metadata_tracking_uid": "2.25.123",
               "raw_roi_number": "2", "raw_roi_volume_ml": ".4"}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            pydicom.dcmwrite(folder / "1.2.3.4.dcm", ds, enforce_file_format=True)
            result = validate(row, folder)
            self.assertEqual(result["qc_flag"], "")
            self.assertAlmostEqual(result["contour_volume_ml"], .4)
            self.assertEqual(result["absolute_difference_pct"], 0)
            self.assertEqual(len(result["source_sha256"]), 64)
            wrong_tracking = dict(row, metadata_tracking_uid="2.25.999")
            self.assertEqual(validate(wrong_tracking, folder)["qc_flag"], "intended_roi_identity_changed")
            stale_volume = dict(row, raw_roi_volume_ml="4.0")
            self.assertEqual(validate(stale_volume, folder)["qc_flag"], "archive_comparator_changed")


if __name__ == "__main__":
    unittest.main()
