# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""Tests for the ``EpwParser``."""
from aiida import orm
import pytest


@pytest.mark.parametrize('test_name', (
    'default',
    'isotropic_eliashberg',
    'bands',
    'bands2',
))
def test_epw(fixture_localhost, generate_calc_job_node, generate_parser, data_regression, test_name):
    """Test ``OpenGridParser`` on the results of a simple ``open_grid.x`` calculation."""
    entry_point_calc_job = 'quantumespresso.epw'
    entry_point_parser = 'quantumespresso.epw'

    node = generate_calc_job_node(entry_point_calc_job, fixture_localhost, test_name)
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False)

    assert calcfunction.is_finished, calcfunction.exception
    assert calcfunction.is_finished_ok, calcfunction.exit_message

    data_regression_dict = {
        'output_parameters': results['output_parameters'].get_dict(),
    }
    if 'max_eigenvalue' in results:
        data_regression_dict['max_eigenvalue'] = results['max_eigenvalue'].get_array('max_eigenvalue').tolist()
    if 'a2f' in results:
        data_regression_dict['a2f'] = results['a2f'].get_array('a2f').tolist()
        data_regression_dict['lambda'] = results['a2f'].get_array('lambda').tolist()
        data_regression_dict['degaussq'] = results['a2f'].get_array('degaussq').tolist()
    if 'el_band_structure' in results:
        data_regression_dict['kpoints'] = results['el_band_structure'].get_kpoints().tolist()
        data_regression_dict['el_band_structure'] = results['el_band_structure'].get_bands().tolist()
    if 'ph_band_structure' in results:
        data_regression_dict['qpoints'] = results['ph_band_structure'].get_kpoints().tolist()
        data_regression_dict['ph_band_structure'] = results['ph_band_structure'].get_bands().tolist()

    data_regression.check(data_regression_dict)


def test_epw_failed_broyden_factor(fixture_localhost, generate_calc_job_node, generate_parser, data_regression):
    """Test a `epw.x` that failed due to ...."""
    name = 'failed_broyden_factor'
    entry_point_calc_job = 'quantumespresso.epw'
    entry_point_parser = 'quantumespresso.epw'

    node = generate_calc_job_node(entry_point_calc_job, fixture_localhost, name)
    parser = generate_parser(entry_point_parser)
    results, calcfunction = parser.parse_from_node(node, store_provenance=False)
    expected_exit_status = node.process_class.exit_codes.ERROR_OUTPUT_STDOUT_INCOMPLETE.status

    assert calcfunction.is_failed
    assert calcfunction.exit_status == expected_exit_status
    assert orm.Log.collection.get_logs_for(node)
    data_regression.check({
        'output_parameters': results['output_parameters'].get_dict(),
    })
