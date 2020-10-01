import os,sys
from xmltemplate import XmlTemplate

TEMPLATE = XmlTemplate('wavelength-bins_template.xml')

DATES = {
    'wavelength-bins-1999-6000.tab': ('1999-08-08T09:28:22', '2000-05-08T07:55:52'),
    'wavelength-bins-2000-3500.tab': ('2000-05-08T07:55:52', '2000-09-11T08:10:55'),
    'wavelength-bins-2000-6950.tab': ('2000-09-11T08:10:55', '2000-11-13T12:41:25'),
    'wavelength-bins-2000-8680.tab': ('2000-11-13T12:41:25', '2000-11-17T04:20:59'),
    'wavelength-bins-2000-8780.tab': ('2000-11-17T04:20:59', '2000-11-19T08:56:44'),
    'wavelength-bins-2000-8840.tab': ('2000-11-19T08:56:44', '2000-11-23T00:36:18'),
    'wavelength-bins-2000-8940.tab': ('2000-11-23T00:36:18', '2000-11-26T07:29:54'),
    'wavelength-bins-2000-9030.tab': ('2000-11-26T07:29:54', '2000-11-29T05:37:33'),
    'wavelength-bins-2000-9110.tab': ('2000-11-29T05:37:33', '2000-12-01T18:59:15'),
    'wavelength-bins-2000-9180.tab': ('2000-12-01T18:59:15', '2000-12-04T08:20:57'),
    'wavelength-bins-2000-9250.tab': ('2000-12-04T08:20:57', '2000-12-06T12:56:41'),
    'wavelength-bins-2000-9310.tab': ('2000-12-06T12:56:41', '2000-12-08T08:46:28'),
    'wavelength-bins-2000-9360.tab': ('2000-12-08T08:46:28', '2000-12-10T13:22:13'),
    'wavelength-bins-2000-9420.tab': ('2000-12-10T13:22:13', '2000-12-12T09:12:00'),
    'wavelength-bins-2000-9470.tab': ('2000-12-12T09:12:00', '2000-12-14T05:01:47'),
    'wavelength-bins-2000-9520.tab': ('2000-12-14T05:01:47', '2000-12-15T16:05:36'),
    'wavelength-bins-2000-9560.tab': ('2000-12-15T16:05:36', '2000-12-17T11:55:23'),
    'wavelength-bins-2000-9610.tab': ('2000-12-17T11:55:23', '2001-02-13T13:42:30'),
    'wavelength-bins-2001-1200.tab': ('2001-02-13T13:42:30', '2001-07-02T08:46:02'),
    'wavelength-bins-2001-5000.tab': ('2001-07-02T08:46:02', '2001-12-31T23:44:22'),
    'wavelength-bins-2002-0000.tab': ('2001-12-31T23:44:22', '2004-12-31T17:34:22'),
    'wavelength-bins-2005-0000.tab': ('2004-12-31T17:34:22', '2005-07-02T08:32:42'),
    'wavelength-bins-2005-5000.tab': ('2005-07-02T08:32:42', '2005-12-31T23:31:02'),
    'wavelength-bins-2006-0000.tab': ('2005-12-31T23:31:02', '2006-07-02T14:29:21'),
    'wavelength-bins-2006-5000.tab': ('2006-07-02T14:29:21', '2007-01-01T05:27:41'),
    'wavelength-bins-2007-0000.tab': ('2007-01-01T05:27:41', '2007-07-02T20:26:01'),
    'wavelength-bins-2007-5000.tab': ('2007-07-02T20:26:01', '2008-01-01T11:24:21'),
    'wavelength-bins-2008-0000.tab': ('2008-01-01T11:24:21', '2008-07-02T02:22:41'),
    'wavelength-bins-2008-5000.tab': ('2008-07-02T02:22:41', '2008-12-31T17:21:01'),
    'wavelength-bins-2009-0000.tab': ('2008-12-31T17:21:01', '2009-07-02T08:19:20'),
    'wavelength-bins-2009-5000.tab': ('2009-07-02T08:19:20', '2011-07-02T20:12:40'),
    'wavelength-bins-2011-5000.tab': ('2011-07-02T20:12:40', '2012-01-01T11:11:00'),
    'wavelength-bins-2012-0000.tab': ('2012-01-01T11:11:00', '2012-07-02T02:09:19'),
    'wavelength-bins-2012-5000.tab': ('2012-07-02T02:09:19', '2012-12-31T17:07:39'),
    'wavelength-bins-2013-0000.tab': ('2012-12-31T17:07:39', '2013-07-02T08:05:59'),
    'wavelength-bins-2013-5000.tab': ('2013-07-02T08:05:59', '2013-12-31T23:04:19'),
    'wavelength-bins-2014-0000.tab': ('2013-12-31T23:04:19', '2014-04-20T12:51:19'),
    'wavelength-bins-2014-3000.tab': ('2014-04-20T12:51:19', '2014-07-02T14:02:39'),
    'wavelength-bins-2014-5000.tab': ('2014-07-02T14:02:39', '2015-07-02T19:59:18'),
    'wavelength-bins-2015-5000.tab': ('2015-07-02T19:59:18', '2016-01-01T10:57:38'),
    'wavelength-bins-2016-0000.tab': ('2016-01-01T10:57:38', '2016-07-02T01:55:58'),
    'wavelength-bins-2016-5000.tab': ('2016-07-02T01:55:58', '2016-12-31T16:54:18'),
    'wavelength-bins-2017-0000.tab': ('2016-12-31T16:54:18', '2017-07-02T07:52:37'),
    'wavelength-bins-2017-5000.tab': ('2017-07-02T07:52:37', '2017-09-14T20:00:00'),
}


TABLES = [
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-1999-6000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-3500.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-6950.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-8680.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-8780.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-8840.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-8940.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9030.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9110.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9180.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9250.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9310.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9360.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9420.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9470.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9520.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9560.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2000-9610.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2001-1200.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2001-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_cruise/calibration/wavelength-bins/wavelength-bins-2002-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2002-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2005-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2006-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2006-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2007-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2007-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2008-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2008-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2009-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2009-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2011-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2012-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2012-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2013-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2013-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2014-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2014-3000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2014-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2015-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2016-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2016-5000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2017-0000.tab',
    '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/calibration/wavelength-bins/wavelength-bins-2017-5000.tab',
]

for datafile in TABLES:

    lookup = {}
    lookup['datafile'] = datafile
    lookup['DATES'] = DATES

    # Write the label
    labelfile = datafile[:-4] + '.xml'
    TEMPLATE.write(lookup, labelfile)

################################################################################
