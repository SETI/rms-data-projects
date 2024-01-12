################################################################################
# Metadata unit tests
################################################################################
import unittest
import pdstable
import glob
import fnmatch
import os
import numpy as np

METADATA = './'

class Test_MakeLabel(unittest.TestCase):

    #===========================================================================
    def bounds_test(self, table, key, min=0, max=360):
        val = table.column_values[key][0]
        if val == -999.:
            return
        self.assertGreaterEqual(val, min)
        self.assertLessEqual(val, max)

    #===========================================================================
    # get summary filenames  ### LIB
    def match(self, dir, pattern):
        all_files = []
        for root, dirs, files in os.walk(dir):
            all_files += glob.glob(os.path.join(root, pattern))
        return(all_files)

    #===========================================================================
    # exclude test files  ### LIB
    def ___exclude(self, files, *patterns):
        result = []
        for pattern in patterns:
            for i in range(len(files)):
                if files[i].find(pattern) == -1:
                    result += [files[i]]
        return(result)

    #===========================================================================
    # exclude test files  ### LIB
    def exclude(self, files, *patterns):
        result = []
        for i in range(len(files)):
            keep = True
            for pattern in patterns:
                if files[i].find(pattern) != -1:
                    keep = False
            if(keep):
                result += [files[i]]
        return(result)

    #===========================================================================
    # test index common fields
    def test_index_common(self):
        pass

    #===========================================================================
    # test geometry common fields
    def test_geometry_common(self):

        # Get labels to test
        files = self.match(METADATA, '*_summary.lbl')
        files = self.exclude(files, 'templates/', 'old/')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file)

            # verify # rows, columns          
            self.assertEqual(table.info.rows, len(table.column_values['OPUS_ID']))
            self.assertEqual(table.info.columns, len(table.keys))
            
            # validate column values
            self.assertIsInstance(table.column_values['VOLUME_ID'][0], np.str_)
            self.assertIsInstance(table.column_values['FILE_SPECIFICATION_NAME'][0], np.str_)
            self.assertIsInstance(table.column_values['OPUS_ID'][0], np.str_)

    #===========================================================================
    # test geometry body fields
    def test_geometry_body(self):

        # Get labels to test
        files = self.match(METADATA, '*_summary.lbl')
        files = self.exclude(files, 'templates/', 'old/', '_ring_')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file)
            
            # validate column values
            self.assertIsInstance(table.column_values['TARGET_NAME'][0], np.str_)

            # validate bounded values
            self.bounds_test(table, 'MINIMUM_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_IAU_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_IAU_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_LOCAL_HOUR_ANGLE')
            self.bounds_test(table, 'MAXIMUM_LOCAL_HOUR_ANGLE')
            self.bounds_test(table, 'MINIMUM_LONGITUDE_WRT_OBSERVER', min=-180, max=180)
            self.bounds_test(table, 'MAXIMUM_LONGITUDE_WRT_OBSERVER', min=-180, max=180)
            self.bounds_test(table, 'MINIMUM_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_SUB_SOLAR_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SUB_SOLAR_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_SUB_SOLAR_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SUB_SOLAR_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_SUB_OBSERVER_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SUB_OBSERVER_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_SUB_OBSERVER_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SUB_OBSERVER_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_SUB_SOLAR_IAU_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_SUB_SOLAR_IAU_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_SUB_OBSERVER_IAU_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_SUB_OBSERVER_IAU_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_CENTER_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_CENTER_PHASE_ANGLE', min=0, max=180)


    #===========================================================================
    # test geometry ring fields
    def test_geometry_ring(self):

        # Get labels to test
        files = self.match(METADATA, '*ring_summary.lbl')
        files = self.exclude(files, 'templates/', 'old/')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file)

            # validate bounded values
            self.bounds_test(table, 'MINIMUM_RIGHT_ASCENSION')
            self.bounds_test(table, 'MAXIMUM_RIGHT_ASCENSION')
            self.bounds_test(table, 'MINIMUM_DECLINATION', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_DECLINATION', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_RING_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_RING_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_SOLAR_HOUR_ANGLE')
            self.bounds_test(table, 'MAXIMUM_SOLAR_HOUR_ANGLE')
            self.bounds_test(table, 'MINIMUM_RING_LONGITUDE_WRT_OBSERVER', min=-180, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_LONGITUDE_WRT_OBSERVER', min=-180, max=180)
            self.bounds_test(table, 'MINIMUM_RING_AZIMUTH')
            self.bounds_test(table, 'MAXIMUM_RING_AZIMUTH')
            self.bounds_test(table, 'MINIMUM_RING_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_RING_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_NORTH_BASED_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_NORTH_BASED_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_RING_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_NORTH_BASED_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_NORTH_BASED_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_SOLAR_RING_ELEVATION', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SOLAR_RING_ELEVATION', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_OBSERVER_RING_ELEVATION', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_OBSERVER_RING_ELEVATION', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_EDGE_ON_RING_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_EDGE_ON_RING_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_EDGE_ON_SOLAR_HOUR_ANGLE')
            self.bounds_test(table, 'MAXIMUM_EDGE_ON_SOLAR_HOUR_ANGLE')
            self.bounds_test(table, 'MINIMUM_SUB_SOLAR_RING_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_SUB_SOLAR_RING_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_SUB_OBSERVER_RING_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_SUB_OBSERVER_RING_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_RING_CENTER_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_CENTER_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_RING_CENTER_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_CENTER_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_RING_CENTER_NORTH_BASED_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_CENTER_NORTH_BASED_INCIDENCE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_RING_CENTER_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_CENTER_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_RING_CENTER_NORTH_BASED_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_RING_CENTER_NORTH_BASED_EMISSION_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MINIMUM_SOLAR_RING_OPENING_ANGLE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SOLAR_RING_OPENING_ANGLE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_OBSERVER_RING_OPENING_ANGLE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_OBSERVER_RING_OPENING_ANGLE', min=-90, max=90)

#########################################
if __name__ == '__main__':
    unittest.main(verbosity=2)
################################################################################




