import unittest
from db import get_conn
from analytics import (
    get_analytics_data,
    get_device_health_history,
    get_component_failure_breakdown,
    get_technician_consistency,
)


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
        self.assertIn("component_breakdown", data)
        self.assertIn("technician_consistency", data)
        self.assertIn("shift_progress", data)
        self.assertIsInstance(data["summary"]["total"], int)

    def test_analytics_with_mock_reports(self):
        conn = get_conn()
        conn.execute(
            "INSERT INTO reports (serial_number, vendor, type_device, status, duration_seconds, petugas, created_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
            ("TESTSN001", "fortinet", "FGT-40F", "PASS", 300, "Budi"),
        )
        conn.execute(
            "INSERT INTO reports (serial_number, vendor, type_device, status, hasil6, ket6, duration_seconds, petugas, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            ("TESTSN002", "cisco", "ISR1100", "FAIL", "NOT OK", "Port Down", 5000, "Budi"),
        )
        conn.execute(
            "INSERT INTO reports (serial_number, vendor, type_device, status, hasil6, ket6, version, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            ("TESTSN002\r\n", "cisco", "ISR1100", "FAIL", "NOT OK", "Optic Failure", 2),
        )
        conn.commit()
        conn.close()

        try:
            data = get_analytics_data()
            self.assertGreaterEqual(data["summary"]["total"], 3)
            self.assertGreaterEqual(data["summary"]["pass"], 1)
            self.assertGreaterEqual(data["summary"]["fail"], 2)

            cisco_data = get_analytics_data(vendor="cisco")
            self.assertGreaterEqual(cisco_data["summary"]["total"], 2)

            # Test officer and model defect stats
            self.assertIn("officer_stats", data)
            self.assertIn("model_stats", data)
            self.assertIn("component_breakdown", data)
            self.assertIn("technician_consistency", data)

            # Test device health history with control characters & chronic defect flag
            health = get_device_health_history("TESTSN002\t\n")
            self.assertEqual(health["serial_number"], "TESTSN002")
            self.assertTrue(health["has_history"])
            self.assertTrue(health["is_chronic_defect"])
            self.assertEqual(health["total_attempts"], 2)
            self.assertEqual(len(health["history"]), 2)

            # Test technician consistency duration outlier clamping (> 1800s ignored in avg)
            conn = get_conn()
            tech_stats = get_technician_consistency(conn)
            conn.close()
            budi_stat = next((t for t in tech_stats if t["officer"] == "Budi"), None)
            self.assertIsNotNone(budi_stat)
            self.assertEqual(budi_stat["avg_duration_minutes"], 5.0) # 300s / 60 = 5.0 mins, 5000s ignored as outlier

        finally:
            conn = get_conn()
            conn.execute("DELETE FROM reports WHERE serial_number LIKE 'TESTSN00%'")
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()

