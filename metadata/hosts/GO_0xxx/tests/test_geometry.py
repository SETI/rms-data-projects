################################################################################
# GOSSI-specific metadata geometry unit tests
################################################################################
import unittest

import pdstable, pdsparser
import numpy as np

#import metadata as meta
###import hosts.GO_0xxx.config
import metadata.unittester_support as unit

#SYSTEMS_TABLE = meta.convert_systems_table(config.SYSTEMS_TABLE, config.SCLK_BASES)

class Test_Geometry_GOSSI(unittest.TestCase):

    #===========================================================================
    def bounds_test(self, file, table, key, min=0, max=360, minmax=True):

        if minmax:
            self.bounds_test(file, table, 'MINIMUM_' + key, minmax=False, min=min, max=max)
            self.bounds_test(file, table, 'MAXIMUM_' + key, minmax=False, min=min, max=max)
            return
            
        nullvals = table.info.column_info_dict[key].invalid_values.copy()
        nullval = nullvals.pop()

#        from IPython import embed; print('+++++++++++++'); embed()
        test = table.column_values[key]
        self.assertFalse(np.any(np.where(
            np.logical_and(np.logical_or(test<min, test>max), test != nullval))), (key, file))

    #===========================================================================
    # test geometry common fields
    def test_geometry_common(self):

        # Get labels to test
        files = unit.match(unit.METADATA, '*_summary.lbl')
        files = unit.exclude(files, 'templates/', 'old/', '__skip/', 'GO_0999/')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file)

            # validate column values
            volume = file.split('/')[-1][0:7]
            self.assertFalse(np.any(np.where(table.column_values['VOLUME_ID'] != volume)) == np.True_, file)

    #===========================================================================
    # test geometry body fields
    def test_geometry_body(self):

        # Get labels to test
        files = unit.match(unit.METADATA, '*_summary.lbl')
        files = unit.exclude(files, 'templates/', 'old/', '__skip/', '_ring_', '_sky_', 'GO_0999/')

        # Test labels, 'GO_0999/
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file) 

#            system, secondaries = meta.get_system(SYSTEMS_TABLE, sclk, config.SCLK_BASES)

            target = table.column_values['TARGET_NAME']

            # validate value bounds
# These bounds only apply to the Jupiter orbits....
#            self.bounds_test(file, table, 'SUB_SOLAR_PLANETOCENTRIC_LATITUDE', min=-30, max=30)
#            self.bounds_test(file, table, 'SUB_SOLAR_PLANETOGRAPHIC_LATITUDE', min=-30, max=30)
#            self.bounds_test(file, table, 'SUB_OBSERVER_PLANETOCENTRIC_LATITUDE', min=-35, max=35)
#            self.bounds_test(file, table, 'SUB_OBSERVER_PLANETOGRAPHIC_LATITUDE', min=-35, max=35)

    #===========================================================================
    # test geometry ring fields
    def test_geometry_ring(self):

        # Get labels to test
        files = unit.match(unit.METADATA, '*ring_summary.lbl')
        files = unit.exclude(files, 'templates/', 'old/', '__skip/', '_body_', '_sky_', 'GO_0999/')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file)

            # validate value bounds
            self.bounds_test(file, table, 'NORTH_BASED_INCIDENCE_ANGLE', min=35, max=145)
            self.bounds_test(file, table, 'SOLAR_RING_ELEVATION', min=-35, max=35)
            self.bounds_test(file, table, 'RING_CENTER_INCIDENCE_ANGLE', min=60, max=90)
            self.bounds_test(file, table, 'RING_CENTER_NORTH_BASED_INCIDENCE_ANGLE', min=35, max=145)

            #################### Slightly exceeds 90 deg in GO_0022
#            self.bounds_test(file, table, 'RING_CENTER_EMISSION_ANGLE', min=-30, max=30)

            self.bounds_test(file, table, 'RING_CENTER_NORTH_BASED_EMISSION_ANGLE', min=35, max=145)
            self.bounds_test(file, table, 'SOLAR_RING_OPENING_ANGLE', min=-35, max=35)
            self.bounds_test(file, table, 'OBSERVER_RING_OPENING_ANGLE', min=-30, max=30)

#########################################
if __name__ == '__main__':
    unittest.main(verbosity=2)
################################################################################




