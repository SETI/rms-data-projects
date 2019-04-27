import unittest

from HistoryLabels import *
from LabelItem import LabelItem
from Value import StringValue
from VicarSyntaxTests import VicarSyntaxTests
from test_LabelItem import mk_sqr_label_items


def _mk_label_task():
    return Task.create('LABEL', 'RGD059', 'Thu Sep 24 17:32:54 1992')


class TestTask(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            Task(None)
        with self.assertRaises(Exception):
            Task([None, None, None])
        with self.assertRaises(Exception):
            Task([1, 2, 3])
        with self.assertRaises(Exception):
            # missing TASK
            Task([
                LabelItem.create('USER', StringValue.from_raw_string('bar')),
                LabelItem.create('DAT_TIM',
                                 StringValue.from_raw_string('baz')),
                LabelItem.create('SOMETHING_ELSE',
                                 StringValue.from_raw_string('baz'))
            ])
        with self.assertRaises(Exception):
            # missing USER
            Task([
                LabelItem.create('TASK', StringValue.from_raw_string('foo')),
                LabelItem.create('DAT_TIM',
                                 StringValue.from_raw_string('baz')),
                LabelItem.create('SOMETHING_ELSE',
                                 StringValue.from_raw_string('baz'))
            ])
        with self.assertRaises(Exception):
            # missing DAT_TIM
            Task([
                LabelItem.create('TASK', StringValue.from_raw_string('foo')),
                LabelItem.create('USER', StringValue.from_raw_string('bar')),
                LabelItem.create('SOMETHING_ELSE',
                                 StringValue.from_raw_string('baz'))
            ])

        with self.assertRaises(Exception):
            # out of order
            Task([
                LabelItem.create('TASK', StringValue.from_raw_string('foo')),
                LabelItem.create('DAT_TIM',
                                 StringValue.from_raw_string('baz')),
                LabelItem.create('USER', StringValue.from_raw_string('bar')),
            ])

        # verify that this does not raise
        _mk_label_task()

    def test_create(self):
        # make a task; verify its values
        task = Task.create('CLEAN_UP', 'JacquesCustodian', 'dat_tim goes here')
        self.assertEqual(
            map(escape_byte_string,
                ['CLEAN_UP', 'JacquesCustodian', 'dat_tim goes here']),
            [label_item.value.value_byte_string
             for label_item in task.history_label_items])

        # make a task with an additional LabelItem; verify its values
        task = Task.create(
            'CLEAN_UP', 'JacquesCustodian', 'dat_tim goes here',
            LabelItem.create('REMINDER',
                             StringValue.from_raw_string('Recycle!')))

        self.assertEqual(
            [LabelItem.create('REMINDER',
                              StringValue.from_raw_string('Recycle!'))],
            task.history_label_items[3:])

    def test_create_migration_task(self):
        dat_tim = 'dat_tim goes here'

        # Create a simple task and check that the task contains the right
        # LabelItems
        task = Task.create_migration_task(dat_tim)
        expected_strs = [MIGRATION_TASK_NAME, MIGRATION_USER_NAME, dat_tim]
        self.assertEqual(map(escape_byte_string, expected_strs),
                         [label_item.value.value_byte_string
                          for label_item in
                          task.history_label_items[:3]])
        self.assertEqual([], task.history_label_items[3:])

        # Create a complicated task and check that the task contains the right
        # LabelItems
        extra_label_items = mk_sqr_label_items()
        task = Task.create_migration_task(dat_tim, *extra_label_items)

        self.assertEqual(extra_label_items,
                         task.history_label_items[3:])

    def test_is_migration_task(self):
        # Not a migration task, but a conversion task, whatever that is.
        self.assertFalse(Task.create('PDS4 conversion',
                                     MIGRATION_USER_NAME,
                                     'dat_tim goes here').is_migration_task())

        # Looks like a migration task of ours, but the wrong user
        self.assertFalse(Task.create(MIGRATION_TASK_NAME,
                                     'some other guy',
                                     'dat_tim goes here').is_migration_task())

        # A true migration task
        self.assertTrue(Task.create_migration_task(
            'dat_tim goes here').is_migration_task())

    def args_for_test(self):
        return [_mk_label_task(),
                Task.create('CHORE', 'ChoreDoer', 'dat_tim'),
                Task.create('CALC_SQRS', 'SquarePants', 'dat_tim',
                            *mk_sqr_label_items()),
                Task.create_migration_task('dat_tim'),
                Task.create_migration_task('dat_tim', *mk_sqr_label_items())
                ]


class TestHistoryLabels(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            HistoryLabels(None)
        with self.assertRaises(Exception):
            HistoryLabels([None, None, None])
        with self.assertRaises(Exception):
            HistoryLabels([1, 2, 3])

        # verify that these do not raise
        HistoryLabels([])
        HistoryLabels([Task.create_migration_task('dat_tim')])

    def args_for_test(self):
        return [HistoryLabels([]),
                HistoryLabels([Task.create_migration_task('dat_tim')])]

    def test_has_migration_task(self):
        self.assertFalse(HistoryLabels([]).has_migration_task())
        self.assertTrue(HistoryLabels(
            [Task.create_migration_task('dat_tim')]).has_migration_task())
