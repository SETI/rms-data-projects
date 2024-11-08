################################################################################
# GOSSI-specific metadata geometry unit tests
################################################################################
import unittest
import pdstable, pdsparser
import numpy as np

import metadata as meta
###import hosts.GO_0xxx.config

import unittester_support as unit

#SYSTEMS_TABLE = meta.convert_systems_table(config.SYSTEMS_TABLE, config.SCLK_BASES)

class Test_Geometry_GOSSI(unittest.TestCase):

    #===========================================================================
    # test geometry common fields
    def test_geometry_common(self):

        # Get labels to test
        files = unit.match(unit.METADATA, '*_summary.lbl')
        files = unit.exclude(files, 'templates/', 'old/', '__skip/')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file)

            # validate column values
            volume = file.split('/')[-1][0:7]
            self.assertFalse(np.any(np.where(table.column_values['VOLUME_ID'] != volume)))

    #===========================================================================
    # test geometry body fields
    def test_geometry_body(self):

        # Get labels to test
        files = unit.match(unit.METADATA, '*_summary.lbl')
        files = unit.exclude(files, 'templates/', 'old/', '__skip/', '.ring_', '_sky_')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file) 

            from IPython import embed; print('+++++++++++++'); embed()
#            system, secondaries = meta.get_system(SYSTEMS_TABLE, sclk, config.SCLK_BASES)

            target = table.column_values['TARGET_NAME']

            # validate value bounds
            test = table.column_values['MINIMUM_SUB_SOLAR_PLANETOCENTRIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MAXIMUM_SUB_SOLAR_PLANETOCENTRIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MINIMUM_SUB_SOLAR_PLANETOGRAPHIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MAXIMUM_SUB_SOLAR_PLANETOGRAPHIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))

            test = table.column_values['MINIMUM_SUB_OBSERVER_PLANETOCENTRIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MAXIMUM_SUB_OBSERVER_PLANETOCENTRIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MINIMUM_SUB_OBSERVER_PLANETOGRAPHIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MAXIMUM_SUB_OBSERVER_PLANETOGRAPHIC_LATITUDE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))

    #===========================================================================
    # test geometry ring fields
    def test_geometry_ring(self):

        # Get labels to test
        files = unit.match(unit.METADATA, '*ring_summary.lbl')
        files = unit.exclude(files, 'templates/', 'old/', '__skip/')

        # Test labels
        print()
        for file in files:
            print('Reading', file)
            table = pdstable.PdsTable(file)

            # validate value bounds
            test = table.column_values['MINIMUM_NORTH_BASED_INCIDENCE_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 55)))
            test = table.column_values['MINIMUM_NORTH_BASED_INCIDENCE_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 55)))
            test = table.column_values['MAXIMUM_NORTH_BASED_INCIDENCE_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MINIMUM_RING_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MAXIMUM_RING_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MINIMUM_NORTH_BASED_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 60)))
            test = table.column_values['MAXIMUM_NORTH_BASED_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 60)))
            test = table.column_values['MINIMUM_SOLAR_RING_ELEVATION']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MAXIMUM_SOLAR_RING_ELEVATION']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MINIMUM_OBSERVER_RING_ELEVATION']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MAXIMUM_OBSERVER_RING_ELEVATION']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MINIMUM_RING_CENTER_INCIDENCE_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MAXIMUM_RING_CENTER_INCIDENCE_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MINIMUM_RING_CENTER_NORTH_BASED_INCIDENCE_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 55)))
            test = table.column_values['MAXIMUM_RING_CENTER_NORTH_BASED_INCIDENCE_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 55)))
            test = table.column_values['MINIMUM_RING_CENTER_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MAXIMUM_RING_CENTER_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MINIMUM_RING_CENTER_NORTH_BASED_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 60)))
            test = table.column_values['MAXIMUM_RING_CENTER_NORTH_BASED_EMISSION_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) < 60)))
            test = table.column_values['MINIMUM_SOLAR_RING_OPENING_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MAXIMUM_SOLAR_RING_OPENING_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 35)))
            test = table.column_values['MINIMUM_OBSERVER_RING_OPENING_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))
            test = table.column_values['MAXIMUM_OBSERVER_RING_OPENING_ANGLE']
            self.assertFalse(np.any(np.where(np.abs(test) > 30)))

#########################################
if __name__ == '__main__':
    unittest.main(verbosity=2)
################################################################################




