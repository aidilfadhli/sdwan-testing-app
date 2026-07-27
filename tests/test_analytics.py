import unittest
from db import get_conn
from analytics import get_analytics_data


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        conn = get_conn()
        conn.close()

    def test_analytics_data_empty(self):
        data = get_analytics_data()
        self.assertIn("summary", data)
        self.assertIn("throughput", data)
        self.assertIn("top_failed_items", data)
        self.assertIn("vendor_distribution", data)
        self.assertIsInstance(data["summary"]["total"], int)

    def test_analytics_with_mock_reports(self):
        conn = get_conn()
        conn.execute(
            "INSERT INTO reports (serial_number, vendor, type_device, status, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("TESTSN001", "fortinet", "FGT-40F", "PASS"),
        )
        conn.execute(
            "INSERT INTO reports (serial_number, vendor, type_device, status, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            ("TESTSN002", "cisco", "ISR1100", "FAIL"),
        )
        conn.commit()
        conn.close()

        try:
            data = get_analytics_data()
            self.assertGreaterEqual(data["summary"]["total"], 2)
            self.assertGreaterEqual(data["summary"]["pass"], 1)
            self.assertGreaterEqual(data["summary"]["fail"], 1)

            cisco_data = get_analytics_data(vendor="cisco")
            self.assertGreaterEqual(cisco_data["summary"]["total"], 1)
        finally:
            conn = get_conn()
            conn.execute("DELETE FROM reports WHERE serial_number IN ('TESTSN001', 'TESTSN002')")
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()
