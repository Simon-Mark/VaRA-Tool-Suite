"""Test case study."""
import typing as tp
import unittest
import unittest.mock as mock
from pathlib import Path
from tempfile import NamedTemporaryFile

import varats.paper_mgmt.case_study as MCS
from tests.test_helper_config import ConfigurationTestImpl
from tests.test_utils import run_in_test_environment, TestInputs
from varats.base.sampling_method import UniformSamplingMethod
from varats.data.reports.commit_report import CommitReport as CR
from varats.mapping.commit_map import CommitMap
from varats.paper_mgmt.paper_config import get_paper_config, load_paper_config
from varats.report.report import FileStatusExtension, ReportFilename
from varats.utils.settings import vara_cfg


class TestCaseStudyRevisionLookupFunctions(unittest.TestCase):
    """Test if revision look up functions find the correct revisions."""

    @run_in_test_environment(TestInputs.PAPER_CONFIGS, TestInputs.RESULT_FILES)
    def test_get_failed_revisions(self):
        """Check if we can correctly find all failed revisions of a case
        study."""
        vara_cfg()['paper_config']['current_config'] = "test_revision_lookup"
        load_paper_config()

        failed_revs = MCS.failed_revisions_for_case_study(
            get_paper_config().get_case_studies('brotli')[0], CR
        )

        self.assertEqual(len(failed_revs), 1)
        self.assertTrue(
            'aaa4424d9bdeb10f8af5cb4599a0fc2bbaac5553' in failed_revs
        )

    @run_in_test_environment(TestInputs.PAPER_CONFIGS, TestInputs.RESULT_FILES)
    def test_get_processed_revisions(self):
        """Check if we can correctly find all processed revisions of a case
        study."""
        vara_cfg()['paper_config']['current_config'] = "test_revision_lookup"
        load_paper_config()

        process_revs = MCS.processed_revisions_for_case_study(
            get_paper_config().get_case_studies('brotli')[0], CR
        )

        self.assertEqual(len(process_revs), 1)
        self.assertTrue(
            '21ac39f7c8ca61c855be0bc38900abe7b5a0f67f' in process_revs
        )

    @run_in_test_environment(TestInputs.PAPER_CONFIGS)
    def test_get_revisions_status_for_case_study_to_high_stage(self):
        """Check if we correctly handle look ups where the stage selected is
        larger than the biggest one in the case study."""
        vara_cfg()['paper_config']['current_config'] = "test_revision_lookup"
        load_paper_config()

        self.assertListEqual(
            MCS.get_revisions_status_for_case_study(
                get_paper_config().get_case_studies('brotli')[0], CR, 9001
            ), []
        )

    @run_in_test_environment(TestInputs.PAPER_CONFIGS)
    def test_get_revision_not_in_case_study(self):
        """Check if we correctly handle the lookup of a revision that is not in
        the case study."""
        vara_cfg()['paper_config']['current_config'] = "test_revision_lookup"
        load_paper_config()

        self.assertRaises(
            ValueError, MCS.get_revision_status_for_case_study,
            get_paper_config().get_case_studies('brotli')[0], '0000000000', CR
        )

    @run_in_test_environment(TestInputs.PAPER_CONFIGS, TestInputs.RESULT_FILES)
    def test_get_revisions_in_case_study(self):
        """Check if we correctly handle the lookup of a revision that is in a
        case study."""
        vara_cfg()['paper_config']['current_config'] = "test_revision_lookup"
        load_paper_config()

        self.assertEqual(
            MCS.get_revision_status_for_case_study(
                get_paper_config().get_case_studies('brotli')[0], '21ac39f7c8',
                CR
            ), FileStatusExtension.Success
        )

    @run_in_test_environment(TestInputs.PAPER_CONFIGS, TestInputs.RESULT_FILES)
    def test_get_newest_result_files_for_case_study(self):
        """Check that when we have two files, the newes one get's selected."""
        vara_cfg()['paper_config']['current_config'] = "test_revision_lookup"
        load_paper_config()

        newest_res_files = MCS.get_newest_result_files_for_case_study(
            get_paper_config().get_case_studies('brotli')[0],
            Path(vara_cfg()['result_dir'].value), CR
        )

        # remove unnecessary files
        newest_res_files = list(
            filter(
                lambda res_file: res_file.commit_hash.startswith('21ac39f7'),
                map(
                    lambda res_file: ReportFilename(res_file), newest_res_files
                )
            )
        )

        self.assertTrue(newest_res_files[0].uuid.endswith('42'))

    @run_in_test_environment(TestInputs.PAPER_CONFIGS)
    def test_get_newest_result_files_for_case_study_with_empty_res_dir(self):
        """Check that we correctly handle the edge case where no result dir
        exists."""
        vara_cfg()['paper_config']['current_config'] = "test_revision_lookup"
        load_paper_config()

        self.assertListEqual(
            MCS.get_newest_result_files_for_case_study(
                get_paper_config().get_case_studies('brotli')[0],
                Path(vara_cfg()['result_dir'].value), CR
            ), []
        )

    def test_get_case_study_file_name_filter_empty(self):
        """Check that we correctly handle  case study filter generation even if
        no case study was provided."""

        cs_filter = MCS.get_case_study_file_name_filter(None)

        self.assertFalse(cs_filter('foo/bar'))