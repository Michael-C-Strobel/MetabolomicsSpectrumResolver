import json
import sys
sys.path.insert(0, '..')

import pytest
import werkzeug.datastructures

import parsing
import views

from usi_test_data import usis_to_test


def test_parse_usi():
    # ValueError will be thrown if invalid USI.
    for usi in usis_to_test:
        parsing.parse_usi(usi)
        if any(collection in usi for collection in
               ['MASSIVEKB', 'GNPS', 'MASSBANK', 'MS2LDA', 'MOTIFDB']):
            parsing.parse_usi(usi.replace('mzspec', 'mzdraft'))


def test_parse_usi_invalid():
    with pytest.raises(ValueError):
        parsing.parse_usi('this:is:an:invalid:usi')
    # Invalid preamble.
    # FIXME: Exception not thrown because of legacy parsing.
    # with pytest.raises(ValueError):
    #     parsing.parse_usi('not_mzspec:PXD000561:'
    #                       'Adult_Frontalcortex_bRP_Elite_85_f09:scan:17555')
    # Invalid collection.
    with pytest.raises(ValueError):
        parsing.parse_usi('mzspec:PXD000000000:'
                          'Adult_Frontalcortex_bRP_Elite_85_f09:scan:17555')
    with pytest.raises(ValueError):
        parsing.parse_usi('mzspec:RANDOM666:'
                          'Adult_Frontalcortex_bRP_Elite_85_f09:scan:17555')
    # Invalid index.
    # FIXME: Exception not thrown because of legacy parsing.
    # with pytest.raises(ValueError):
    #     parsing.parse_usi('mzspec:PXD000561:'
    #                       'Adult_Frontalcortex_bRP_Elite_85_f09:'
    #                       'not_scan:17555')
    # Missing index.
    with pytest.raises(ValueError):
        parsing.parse_usi('mzspec:PXD000561:'
                          'Adult_Frontalcortex_bRP_Elite_85_f09:scan:')


def test_parse_gnps_task():
    usi = ('mzspec:GNPS:TASK-c95481f0c53d42e78a61bf899e9f9adb-spectra/'
           'specs_ms.mgf:scan:1943')
    parsing.parse_usi(usi)
    # Invalid task pattern.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':TASK-', ':TASK-666'))
    # Invalid index flag.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':scan:', ':index:'))
    # Invalid file name.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace('specs_ms.mgf', 'nonexisting.mgf'))
    # Invalid scan number.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':1943', ':this_scan_does_not_exist'))


def test_parse_gnps_library():
    usi = 'mzspec:GNPS:GNPS-LIBRARY:accession:CCMSLIB00005436077'
    parsing.parse_usi(usi)
    # Invalid index flag.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':accession:', ':index:'))
    # Invalid accession.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':CCMSLIB00005436077',
                                      ':this_accession_does_not_exist'))


def test_parse_massbank():
    usi = 'mzspec:MASSBANK::accession:SM858102'
    parsing.parse_usi(usi)
    # Invalid index flag.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':accession:', ':index:'))
    # Invalid accession.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':SM858102',
                                      ':this_accession_does_not_exist'))


def test_parse_ms2lda():
    usi = 'mzspec:MS2LDA:TASK-190:accession:270684'
    parsing.parse_usi(usi)
    # Invalid task pattern.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':TASK-', ':TASK-bla'))
    # Invalid index flag.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':accession:', ':index:'))
    # Invalid experiment ID.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':TASK-190', ':TASK-666666666'))
    # Invalid document ID.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':270684',
                                      ':this_document_does_not_exist'))


def test_parse_msv_pxd():
    usi = 'mzspec:MSV000079514:Adult_Frontalcortex_bRP_Elite_85_f09:scan:17555'
    parsing.parse_usi(usi)
    # Invalid collection.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':MSV000079514:', ':MSV666666666:'))
    # Invalid file name.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace('Adult_Frontalcortex_bRP_Elite_85_f09',
                                      'this_filename_does_not_exist'))
    # Invalid index flag.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':scan:', ':index:'))
    # Invalid scan number.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':17555', ':this_scan_does_not_exist'))


def test_parse_motifdb():
    usi = 'mzspec:MOTIFDB::accession:171163'
    parsing.parse_usi(usi)
    # Invalid index flag.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':accession:', ':index:'))
    # Invalid index.
    with pytest.raises(ValueError):
        parsing.parse_usi(usi.replace(':171163', ':this_index_does_not_exist'))


def _get_plotting_args(**kwargs):
    plotting_args = views.default_plotting_args.copy()
    plotting_args['max_intensity'] = plotting_args['max_intensity_unlabeled']
    del plotting_args['annotate_peaks']
    for key, value in kwargs.items():
        plotting_args[key] = value
    return werkzeug.datastructures.ImmutableMultiDict(plotting_args)


def test_get_plotting_args_invalid_figsize():
    plotting_args = views._get_plotting_args(_get_plotting_args(width=-1))
    assert plotting_args['width'] == views.default_plotting_args['width']
    plotting_args = views._get_plotting_args(_get_plotting_args(height=-1))
    assert plotting_args['height'] == views.default_plotting_args['height']
    plotting_args = views._get_plotting_args(_get_plotting_args(width=-1),
                                             mirror=True)
    assert plotting_args['width'] == views.default_plotting_args['width']
    plotting_args = views._get_plotting_args(_get_plotting_args(height=-1),
                                             mirror=True)
    assert plotting_args['height'] == views.default_plotting_args['height']


def test_get_plotting_args_unspecified_mz_range():
    plotting_args = views._get_plotting_args(_get_plotting_args())
    assert plotting_args['mz_min'] is None
    plotting_args = views._get_plotting_args(_get_plotting_args())
    assert plotting_args['mz_max'] is None
    plotting_args = views._get_plotting_args(_get_plotting_args(), mirror=True)
    assert plotting_args['mz_min'] is None
    plotting_args = views._get_plotting_args(_get_plotting_args(), mirror=True)
    assert plotting_args['mz_max'] is None


def test_get_plotting_args_invalid_mz_range():
    plotting_args = views._get_plotting_args(_get_plotting_args(mz_min=-100))
    assert plotting_args['mz_min'] is None
    plotting_args = views._get_plotting_args(_get_plotting_args(mz_max=-100))
    assert plotting_args['mz_max'] is None
    plotting_args = views._get_plotting_args(_get_plotting_args(mz_min=-100),
                                             mirror=True)
    assert plotting_args['mz_min'] is None
    plotting_args = views._get_plotting_args(_get_plotting_args(mz_max=-100),
                                             mirror=True)
    assert plotting_args['mz_max'] is None


def test_get_plotting_args_invalid_max_intensity():
    plotting_args = views._get_plotting_args(_get_plotting_args(
        max_intensity=-1))
    assert (plotting_args['max_intensity']
            == views.default_plotting_args['max_intensity_labeled'])
    plotting_args = views._get_plotting_args(_get_plotting_args(
        max_intensity=-1), mirror=True)
    assert (plotting_args['max_intensity']
            == views.default_plotting_args['max_intensity_mirror_labeled'])


def test_get_plotting_args_invalid_annotate_precision():
    plotting_args = views._get_plotting_args(_get_plotting_args(
        annotate_precision=-1))
    assert (plotting_args['annotate_precision']
            == views.default_plotting_args['annotate_precision'])
    plotting_args = views._get_plotting_args(_get_plotting_args(
        annotate_precision=-1), mirror=True)
    assert (plotting_args['annotate_precision']
            == views.default_plotting_args['annotate_precision'])


def test_get_plotting_args_invalid_fragment_mz_tolerance():
    plotting_args = views._get_plotting_args(_get_plotting_args(
        fragment_mz_tolerance=-1))
    assert (plotting_args['fragment_mz_tolerance']
            == views.default_plotting_args['fragment_mz_tolerance'])
    plotting_args = views._get_plotting_args(_get_plotting_args(
        fragment_mz_tolerance=-1), mirror=True)
    assert (plotting_args['fragment_mz_tolerance']
            == views.default_plotting_args['fragment_mz_tolerance'])


def test_prepare_spectrum():
    usi = 'mzspec:MOTIFDB::accession:171163'
    spectrum, _ = parsing.parse_usi(usi)
    spectrum_processed = views._prepare_spectrum(
        spectrum, **views._get_plotting_args(_get_plotting_args(
            mz_min=400, mz_max=700, annotate_peaks=json.dumps([[]]))))
    assert spectrum is not spectrum_processed
    assert len(spectrum.mz) == 49
    assert len(spectrum_processed.mz) == 5
    assert spectrum_processed.intensity.max() == 1
    assert len(spectrum_processed.mz) == len(spectrum_processed.annotation)
    assert all([annotation is None
                for annotation in spectrum_processed.annotation])


def test_prepare_spectrum_annotate_peaks_default():
    usi = 'mzspec:MOTIFDB::accession:171163'
    spectrum, _ = parsing.parse_usi(usi)
    spectrum_processed = views._prepare_spectrum(
        spectrum, **views._get_plotting_args(_get_plotting_args()))
    assert not all([annotation is None
                    for annotation in spectrum_processed.annotation])


def test_prepare_spectrum_annotate_peaks_specified():
    usi = 'mzspec:MOTIFDB::accession:171163'
    spectrum, _ = parsing.parse_usi(usi)
    spectrum_processed = views._prepare_spectrum(
        spectrum, **views._get_plotting_args(_get_plotting_args(
            mz_min=400, mz_max=700,
            annotate_peaks=json.dumps([[477.2525, 654.3575]]))))
    assert sum([annotation is not None
                for annotation in spectrum_processed.annotation]) == 2
    assert spectrum_processed.annotation[0] is None
    assert spectrum_processed.annotation[1] is not None
    assert spectrum_processed.annotation[2] is None
    assert spectrum_processed.annotation[3] is None
    assert spectrum_processed.annotation[4] is not None


def test_prepare_spectrum_annotate_peaks_specified_invalid():
    usi = 'mzspec:MOTIFDB::accession:171163'
    spectrum, _ = parsing.parse_usi(usi)
    spectrum_processed = views._prepare_spectrum(
        spectrum, **views._get_plotting_args(_get_plotting_args(
            annotate_peaks=json.dumps([[1477.2525, 1654.3575]]))))
    assert all([annotation is None
                for annotation in spectrum_processed.annotation])


def test_prepare_mirror_spectra():
    usi1 = 'mzspec:MOTIFDB::accession:171163'
    usi2 = 'mzspec:MOTIFDB::accession:171164'
    spectrum1, _ = parsing.parse_usi(usi1)
    spectrum2, _ = parsing.parse_usi(usi2)
    spectrum1_processed, spectrum2_processed = views._prepare_mirror_spectra(
        spectrum1, spectrum2, views._get_plotting_args(_get_plotting_args(
            mz_min=400, mz_max=700, annotate_peaks=json.dumps([[], []])),
            mirror=True))
    assert spectrum1 is not spectrum1_processed
    assert spectrum2 is not spectrum2_processed
    assert len(spectrum1.mz) == 49
    assert len(spectrum2.mz) == 28
    assert len(spectrum1_processed.mz) == 5
    assert len(spectrum2_processed.mz) == 9
    assert spectrum1_processed.intensity.max() == 1
    assert spectrum2_processed.intensity.max() == 1
    assert len(spectrum1_processed.mz) == len(spectrum1_processed.annotation)
    assert len(spectrum2_processed.mz) == len(spectrum2_processed.annotation)
    assert all([annotation is None
                for annotation in spectrum1_processed.annotation])
    assert all([annotation is None
                for annotation in spectrum2_processed.annotation])
