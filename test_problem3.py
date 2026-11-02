"""
问题 3 单元测试: Order

说明：
使用 Python 的 unittest 框架补全下面的单元测试方法。
你的测试方法必须断言 Order 对象上的多个属性
（例如 subtotal、discount_amount、tax_amount、shipping_fee、final_total、status）
以验证在各种条件下的状态一致性。

运行测试：
    python -m unittest test_problem3.py -v
"""
import unittest
from problem3 import Order


class TestOrder(unittest.TestCase):

    def setUp(self):
        self.regular_order = Order("ORD100", customer_tier="regular")
        self.silver_order = Order("ORD200", customer_tier="silver")
        self.gold_order = Order("ORD300", customer_tier="gold")

    def test_initial_state(self):
        order = self.regular_order

        self.assertEqual(order.order_id, "ORD100")
        self.assertEqual(order.customer_tier, "regular")
        self.assertEqual(order.items, {})
        self.assertEqual(order.status, "PENDING")
        self.assertIsNone(order.applied_coupon)
        self.assertEqual(order.subtotal, 0.0)
        self.assertEqual(order.discount_amount, 0.0)
        self.assertEqual(order.tax_amount, 0.0)
        self.assertEqual(order.shipping_fee, 0.0)
        self.assertEqual(order.final_total, 0.0)

    def test_add_items_and_recalculate_totals(self):
        order = self.regular_order

        order.add_item("Laptop", 40.0, quantity=1, category="electronics")
        order.add_item("Apple", 10.0, quantity=1, category="grocery")

        self.assertEqual(order.items["Laptop"]["quantity"], 1)
        self.assertEqual(order.items["Apple"]["quantity"], 1)
        self.assertEqual(order.subtotal, 50.0)
        self.assertEqual(order.discount_amount, 0.0)
        self.assertEqual(order.tax_amount, 3.20)
        self.assertEqual(order.shipping_fee, 0.0)
        self.assertEqual(order.final_total, 53.20)
        self.assertEqual(order.status, "PENDING")

    def test_membership_and_coupon_discount(self):
        order = self.silver_order
        order.add_item("Monitor", 100.0, category="electronics")
        order.apply_coupon("SAVE10")

        # 100 - 5%会员折扣 - 10%优惠券折扣
        self.assertEqual(order.subtotal, 100.0)
        self.assertEqual(order.discount_amount, 14.50)
        self.assertEqual(order.tax_amount, 6.84)
        self.assertEqual(order.shipping_fee, 0.0)
        self.assertEqual(order.final_total, 92.34)
        self.assertEqual(order.applied_coupon, "SAVE10")

    def test_flat_coupon_and_shipping(self):
        order = self.gold_order
        order.add_item("Headphones", 40.0, category="electronics")
        order.apply_coupon("FLAT15")

        # 40 - 10%会员折扣 - 15元优惠券 + 税费 + 运费
        self.assertEqual(order.subtotal, 40.0)
        self.assertEqual(order.discount_amount, 19.0)
        self.assertEqual(order.tax_amount, 1.68)
        self.assertEqual(order.shipping_fee, 5.99)
        self.assertEqual(order.final_total, 28.67)

    def test_add_and_remove_items(self):
        order = self.regular_order
        order.add_item("Keyboard", 25.0, quantity=2)
        order.add_item("Keyboard", 25.0, quantity=1)

        self.assertEqual(order.items["Keyboard"]["quantity"], 3)
        self.assertEqual(order.subtotal, 75.0)

        order.remove_item("Keyboard", quantity=1)
        self.assertEqual(order.items["Keyboard"]["quantity"], 2)
        self.assertEqual(order.subtotal, 50.0)

        order.remove_item("Keyboard")
        self.assertNotIn("Keyboard", order.items)
        self.assertEqual(order.subtotal, 0.0)
        self.assertEqual(order.final_total, 0.0)
        self.assertEqual(order.shipping_fee, 0.0)

    def test_checkout_and_cancel_state_transitions(self):
        order = self.regular_order

        with self.assertRaises(ValueError):
            order.checkout()

        order.add_item("Book", 20.0)
        self.assertTrue(order.checkout())
        self.assertEqual(order.status, "PAID")

        with self.assertRaises(RuntimeError):
            order.add_item("Pen", 2.0)

        with self.assertRaises(RuntimeError):
            order.apply_coupon("SAVE10")

        with self.assertRaises(RuntimeError):
            order.cancel()

    def test_cancel_pending_order(self):
        order = self.regular_order
        order.add_item("Book", 20.0)

        self.assertTrue(order.cancel())
        self.assertEqual(order.status, "CANCELLED")

        with self.assertRaises(RuntimeError):
            order.add_item("Pen", 2.0)

        with self.assertRaises(RuntimeError):
            order.apply_coupon("FLAT15")

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Order("ORD400", customer_tier="platinum")

        order = self.regular_order

        with self.assertRaises(ValueError):
            order.add_item("Invalid", 0.0)

        with self.assertRaises(ValueError):
            order.add_item("Invalid", 10.0, quantity=0)

        with self.assertRaises(ValueError):
            order.apply_coupon("INVALID")

        with self.assertRaises(KeyError):
            order.remove_item("Missing")

        order.add_item("Book", 20.0)

        with self.assertRaises(ValueError):
            order.remove_item("Book", quantity=0)


if __name__ == "__main__":
    unittest.main()
