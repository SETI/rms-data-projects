#!/usr/bin/env python
################################################################################
# unittester.py
################################################################################
import os
from pathlib import Path
import unittest

import pdstable, pdslogger
from pdslabelbot import PdsLabelBot

class Test_PdsLabelBot(unittest.TestCase):

    #===========================================================================
    def runTest(self):

        # Define paths
        test_data = Path(os.environ['OOPS_TEST_DATA_PATH']) / Path('pdslabelbot')
        templates = test_data / Path('templates')

        # Test logger
        PdsLabelBot.set_logger(pdslogger.EasyLogger())
    
        # Test supplemental index
        bot = PdsLabelBot(templates / Path('supplemental_index.lbl'),
                          test_data / Path('GO_0017_supplemental_index.tab'), 
                          table_type='SUPPLEMENTAL')
        bot.write(test_data / Path('GO_0017_supplemental_index.lbl'))

        table = pdstable.PdsTable(test_data / Path('GO_0017_supplemental_index.lbl'))
        self. assertIsInstance(table, pdstable.PdsTable)

        # Test sky geometry table
        bot = PdsLabelBot(templates / Path('sky_summary.lbl'), 
                          test_data / Path('GO_0017_sky_summary.tab'), 
                          table_type='SKY_GEOMETRY')
        bot.write(test_data / Path('GO_0017_sky_summary.lbl'))

        table = pdstable.PdsTable(test_data / Path('GO_0017_sky_summary.lbl'))
        self. assertIsInstance(table, pdstable.PdsTable)

        # Test body geometry table
        bot = PdsLabelBot(templates / Path('body_summary.lbl'),
                          test_data / Path('GO_0017_body_summary.tab'), 
                          table_type='BODY_GEOMETRY')
        bot.write(test_data / Path('GO_0017_body_summary.lbl'))

        table = pdstable.PdsTable(test_data / Path('GO_0017_body_summary.lbl'))
        self. assertIsInstance(table, pdstable.PdsTable)

        # Test ring geometry table
        bot = PdsLabelBot(templates / Path('ring_summary.lbl'),
                          test_data / Path('GO_0017_ring_summary.tab'), 
                          table_type='RING_GEOMETRY')
        bot.write(test_data / Path('GO_0017_ring_summary.lbl'))

        table = pdstable.PdsTable(test_data / Path('GO_0017_ring_summary.lbl'))
        self. assertIsInstance(table, pdstable.PdsTable)


#########################################
if __name__ == '__main__':
    unittest.main(verbosity=2)
################################################################################




