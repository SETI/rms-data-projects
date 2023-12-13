################################################################################
# Metadata unit tests
################################################################################

import unittest
import pdstable
import glob
import numpy as np

class Test_MakeLabel(unittest.TestCase):

    #===========================================================================
    def bounds_test(self, table, key, min=0, max=360):
        val = table.column_values[key][0]
        if val == -999.:
            return
        self.assertGreaterEqual(val, min)
        self.assertLessEqual(val, max)

### need to test index file outputs
### need to test metadata code
### need to test index code

    #===========================================================================
    # test geom files
    def runTest(self):

#        files = glob.glob('GO_00*/*[moon,jupiter]_summary*.lbl')
        files = glob.glob('hosts/*/*/*_summary.lbl')
        from IPython import embed; print('+++++++++++++'); embed()
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
            self.bounds_test(table, 'MAXIMUM_INCIDENCE_ANGLE')
            self.bounds_test(table, 'MINIMUM_EMISSION_ANGLE')
            self.bounds_test(table, 'MAXIMUM_EMISSION_ANGLE')
            self.bounds_test(table, 'MINIMUM_SUB_SOLAR_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SUB_SOLAR_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_SUB_OBSERVER_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SUB_OBSERVER_PLANETOCENTRIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_SUB_OBSERVER_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MAXIMUM_SUB_OBSERVER_PLANETOGRAPHIC_LATITUDE', min=-90, max=90)
            self.bounds_test(table, 'MINIMUM_SUB_SOLAR_IAU_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_SUB_SOLAR_IAU_LONGITUDE')
            self.bounds_test(table, 'MINIMIM_SUB_OBSERVER_IAU_LONGITUDE')
            self.bounds_test(table, 'MAXIMUM_SUB_OBSERVER_IAU_LONGITUDE')
            self.bounds_test(table, 'MINIMUM_CENTER_PHASE_ANGLE', min=0, max=180)
            self.bounds_test(table, 'MAXIMUM_CENTER_PHASE_ANGLE', min=0, max=180)

#########################################
if __name__ == '__main__':
    unittest.main(verbosity=2)
################################################################################




