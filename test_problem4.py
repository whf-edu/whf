"""
问题 4 单元测试: MeetingRoom

说明：
使用 Python 的 unittest 框架补全下面的单元测试方法。
你的测试方法必须断言 MeetingRoom 对象上的多个属性
（例如 bookings 列表、total_hours_booked、free slots、utilization rate）
以验证会议室状态和冲突管理。

运行测试：
    python -m unittest test_problem4.py -v
"""
import unittest
from copy import deepcopy
from problem4 import MeetingRoom


class TestMeetingRoom(unittest.TestCase):

    def setUp(self):
        self.room = MeetingRoom("Conference-A", capacity=10)

    def test_initial_state_multi_attributes(self):
        self.assertEqual(self.room.room_id, "Conference-A")
        self.assertEqual(self.room.capacity, 10)
        self.assertEqual(self.room.bookings, [])
        self.assertEqual(self.room.total_hours_booked, 0)
        self.assertFalse(self.room.is_maintenance)
        self.assertEqual(self.room.get_free_slots(), [(8, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.0)

    def test_single_booking_multi_attributes(self):
        self.assertTrue(
            self.room.book("B01", "Team Meeting", 10, 12, 5)
        )

        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0], {
            "booking_id": "B01",
            "title": "Team Meeting",
            "start_time": 10,
            "end_time": 12,
            "attendees": 5
        })
        self.assertEqual(self.room.total_hours_booked, 2)
        self.assertEqual(self.room.get_utilization_rate(), 0.2)
        self.assertEqual(
            self.room.get_free_slots(),
            [(8, 10), (12, 18)]
        )

    def test_back_to_back_meetings_allowed(self):
        self.assertTrue(
            self.room.book("B01", "Morning Meeting", 9, 10, 5)
        )
        self.assertTrue(
            self.room.book("B02", "Second Meeting", 10, 12, 4)
        )

        self.assertEqual(
            [b["booking_id"] for b in self.room.bookings],
            ["B01", "B02"]
        )
        self.assertEqual(self.room.total_hours_booked, 3)
        self.assertEqual(self.room.get_free_slots(), [(8, 9), (12, 18)])
        self.assertEqual(self.room.get_utilization_rate(), 0.3)

    def test_overlapping_booking_rejected(self):
        self.room.book("B01", "Existing", 9, 11, 5)

        before = deepcopy(self.room.__dict__)

        with self.assertRaises(ValueError):
            self.room.book("B02", "Overlapping", 10, 12, 4)

        self.assertEqual(self.room.__dict__, before)

        with self.assertRaises(ValueError):
            self.room.book("B03", "Contained", 9, 12, 4)

        self.assertEqual(self.room.__dict__, before)

    def test_cancel_booking_updates_all_attributes(self):
        self.room.book("B01", "First", 9, 10, 4)
        self.room.book("B02", "Second", 12, 14, 6)

        self.assertEqual(self.room.total_hours_booked, 3)

        self.assertTrue(self.room.cancel("B01"))

        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B02")
        self.assertEqual(self.room.total_hours_booked, 2)
        self.assertEqual(
            self.room.get_free_slots(),
            [(8, 12), (14, 18)]
        )
        self.assertEqual(self.room.get_utilization_rate(), 0.2)

    def test_capacity_and_validation_exceptions(self):
        with self.assertRaises(ValueError):
            self.room.book("B01", "Too Large", 9, 10, 11)

        with self.assertRaises(ValueError):
            self.room.book("B02", "Invalid Time", 10, 10, 5)

        self.room.book("B03", "Valid Meeting", 10, 12, 5)

        with self.assertRaises(ValueError):
            self.room.book("B03", "Duplicate ID", 13, 14, 5)

        self.room.is_maintenance = True

        with self.assertRaises(RuntimeError):
            self.room.book("B04", "Maintenance", 13, 14, 5)

        self.room.is_maintenance = False

        with self.assertRaises(KeyError):
            self.room.cancel("UNKNOWN")

        with self.assertRaises(ValueError):
            self.room.get_free_slots(18, 8)

        with self.assertRaises(ValueError):
            self.room.get_utilization_rate(0)


if __name__ == "__main__":
    unittest.main()
