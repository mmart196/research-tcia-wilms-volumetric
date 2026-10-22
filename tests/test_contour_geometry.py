"""Analytic geometry checks; these synthetic shapes are not study observations."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from pydicom.dataset import Dataset

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from volumes import laterality, roi_volume_ml, source_class


def contour(xy, z, kind="CLOSED_PLANAR", transform=None, reverse=False):
    points = np.column_stack((np.asarray(xy, dtype=float), np.full(len(xy), z)))
    if reverse:
        points = points[::-1]
    if transform is not None:
        points = points @ transform.T + np.array([110.0, -35.0, 52.0])
    return SimpleNamespace(ContourGeometricType=kind, ContourData=points.ravel(),
                           NumberOfContourPoints=len(points))


def square(x, y, size):
    return [(x, y), (x + size, y), (x + size, y + size), (x, y + size)]


class ContourGeometryTests(unittest.TestCase):
    def assert_volume(self, contours, expected, planes):
        value, n, flag = roi_volume_ml(contours)
        self.assertEqual(flag, "")
        self.assertEqual(n, planes)
        self.assertAlmostEqual(value, expected, places=10)

    def test_regular_prism_with_explicit_end_slabs(self):
        # 100 mm² × 6 mm, with centre planes 0/2/4 and boundaries -1/5.
        self.assert_volume([contour(square(0, 0, 10), z) for z in [0, 2, 4]], .6, 3)

    def test_multiple_disjoint_contours_count_as_one_plane(self):
        # Each of two planes has separate 100 and 25 mm² components.
        cs = [contour(shape, z) for z in [0, 2]
              for shape in [square(0, 0, 10), square(20, 0, 5)]]
        self.assert_volume(cs, .5, 2)

    def test_winding_order_oblique_orientation_and_translation_do_not_change_volume(self):
        angle = np.pi / 5
        rx = np.array([[1, 0, 0], [0, np.cos(angle), -np.sin(angle)],
                       [0, np.sin(angle), np.cos(angle)]])
        ry = np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0],
                       [-np.sin(angle), 0, np.cos(angle)]])
        cs = [contour(square(0, 0, 10), z, transform=ry @ rx, reverse=i % 2 == 0)
              for i, z in enumerate([4, 0, 2])]
        self.assert_volume(cs, .6, 3)

    def test_xor_outer_hole_and_island(self):
        # Per plane: 100 - 36 + 4 = 68 mm², irrespective of winding.
        cs = [contour(shape, z, "CLOSEDPLANAR_XOR", reverse=i % 2 == 0)
              for z in [0, 2, 4]
              for i, shape in enumerate([square(0, 0, 10), square(2, 2, 6), square(4, 4, 2)])]
        self.assert_volume(cs, .408, 3)

    def test_xor_overlapping_components_exclude_shared_area(self):
        # Two 100 mm² squares overlap by 50 mm²: XOR area is 100 mm².
        cs = [contour(shape, z, "CLOSEDPLANAR_XOR") for z in [0, 2]
              for shape in [square(0, 0, 10), square(5, 0, 10)]]
        self.assert_volume(cs, .4, 2)

    def test_closed_planar_nesting_is_not_silently_added_or_subtracted(self):
        cs = [contour(shape, z) for z in [0, 2]
              for shape in [square(0, 0, 10), square(2, 2, 6)]]
        self.assertEqual(roi_volume_ml(cs), (None, 2, "overlapping_or_nested_closed_planar"))

    def test_duplicate_closed_contours_are_rejected(self):
        cs = [contour(square(0, 0, 10), z) for z in [0, 0, 2]]
        self.assertEqual(roi_volume_ml(cs), (None, 2, "overlapping_or_nested_closed_planar"))

    def test_mixed_xor_types_are_rejected_for_the_whole_roi(self):
        cs = [contour(square(0, 0, 10), 0, "CLOSEDPLANAR_XOR"),
              contour(square(0, 0, 10), 2)]
        self.assertEqual(roi_volume_ml(cs)[2], "mixed_xor_contour_types")

    def test_irregular_spacing_is_not_filled_with_an_invented_median_slab(self):
        cs = [contour(square(0, 0, 10), z) for z in [0, 2, 7]]
        self.assertEqual(roi_volume_ml(cs), (None, 3, "irregular_plane_spacing"))

    def test_parallelism_and_planarity_are_checked(self):
        horizontal = contour(square(0, 0, 10), 0)
        vertical = contour(square(0, 0, 10), 2,
                           transform=np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]))
        self.assertEqual(roi_volume_ml([horizontal, vertical])[2], "nonparallel_contour_planes")
        warped = contour(square(0, 0, 10), 2)
        warped.ContourData[-1] += 1
        self.assertEqual(roi_volume_ml([horizontal, warped])[2], "nonplanar_contour")

    def test_single_plane_with_multiple_islands_has_no_inferred_thickness(self):
        cs = [contour(square(x, 0, 5), 0) for x in [0, 10, 20]]
        self.assertEqual(roi_volume_ml(cs), (None, 1, "single_slice"))

    def test_concave_simple_polygon_area(self):
        shape = [(0, 0), (10, 0), (10, 5), (5, 5), (5, 10), (0, 10)]
        self.assert_volume([contour(shape, z) for z in [0, 2]], .3, 2)

    def test_bad_points_or_unsupported_contours_do_not_produce_partial_volumes(self):
        good = contour(square(0, 0, 10), 0)
        bad = contour(square(0, 0, 10), 2)
        bad.ContourData[0] = np.nan
        self.assertEqual(roi_volume_ml([good, bad])[2], "invalid_contour_points")
        bad = contour(square(0, 0, 10), 2, "OPEN_PLANAR")
        self.assertEqual(roi_volume_ml([good, bad])[2], "unsupported_contour_type")
        bad = contour(square(0, 0, 10), 2)
        bad.NumberOfContourPoints = 3
        self.assertEqual(roi_volume_ml([good, bad])[2], "contour_point_count_mismatch")


class SourceMetadataTests(unittest.TestCase):
    def test_standalone_laterality_tokens_and_unrelated_words(self):
        for label in ["L KIDNEY - 1", "LT-KIDNEY", "left kidney"]:
            self.assertEqual(laterality(label), "left")
        for label in ["R KIDNEY - 1", "RT-KIDNEY", "right kidney"]:
            self.assertEqual(laterality(label), "right")
        for label in ["LIVER", "RIGHTEOUS", "BRIGHT", "LTKIDNEY", "RL KIDNEY",
                      "L/R KIDNEYS", "LEFT AND RIGHT KIDNEY"]:
            self.assertEqual(laterality(label), "unknown")

    @staticmethod
    def referenced_object(series_uids, contour_uids=()):
        def image(uid):
            result = Dataset()
            result.ReferencedSOPClassUID = uid
            return result
        result, frame, study, series = (Dataset() for _ in range(4))
        series.ContourImageSequence = [image(uid) for uid in series_uids]
        study.RTReferencedSeriesSequence = [series]
        frame.RTReferencedStudySequence = [study]
        result.ReferencedFrameOfReferenceSequence = [frame]
        roi, contour = Dataset(), Dataset()
        contour.ContourImageSequence = [image(uid) for uid in contour_uids]
        roi.ContourSequence = [contour]
        result.ROIContourSequence = [roi]
        return result

    def test_conflicting_later_references_are_not_ignored(self):
        ct, mr = "1.2.840.10008.5.1.4.1.1.2", "1.2.840.10008.5.1.4.1.1.4"
        self.assertEqual(source_class(self.referenced_object([ct, ct])), "CT")
        self.assertEqual(source_class(self.referenced_object([ct, mr])), "mixed")
        self.assertEqual(source_class(self.referenced_object([ct], [mr])), "mixed")
        self.assertEqual(source_class(self.referenced_object([], [mr])), "MR")
        self.assertEqual(source_class(self.referenced_object(["1.2.3.4"])), "unknown")
        self.assertEqual(source_class(Dataset()), "unknown")


if __name__ == "__main__":
    unittest.main()
