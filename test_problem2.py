"""
问题 2单元测试: BankAccount

说明：
使用 Python 的 unittest 框架补全下面的测试方法。
你的测试方法必须断言 BankAccount 对象上的多个属性
（例如 balance、status、transaction_history、summary）以验证状态一致性。

运行测试：
    python -m unittest test_problem2.py -v
"""
import unittest
from copy import deepcopy
from problem2 import BankAccount


class TestBankAccount(unittest.TestCase):

    def setUp(self):
        self.account_empty = BankAccount(
            "ACC001", "Alice", initial_balance=0.0, overdraft_limit=100.0
        )
        self.account_funded = BankAccount(
            "ACC002", "Bob", initial_balance=200.0, overdraft_limit=50.0
        )

#同时验证余额、状态、交易数量和摘要的一致性
    def assert_account_state(self, account, balance, status, count):
        self.assertAlmostEqual(account.balance, balance)
        self.assertEqual(account.status, status)
        self.assertEqual(len(account.transaction_history), count)
        self.assertDictEqual(account.get_summary(), {
            "account_id": account.account_id,
            "owner": account.owner,
            "balance": round(balance, 2),
            "status": status,
            "overdraft_limit": account.overdraft_limit,
            "transaction_count": count
        })
        if count:
            self.assertAlmostEqual(
                account.transaction_history[-1]["balance_after"], balance
            )
#验证空账户和有初始存款账户的初始属性
    def test_initial_state_multi_attributes(self):
        empty = self.account_empty
        self.assertEqual(empty.account_id, "ACC001")
        self.assertEqual(empty.owner, "Alice")
        self.assertEqual(empty.overdraft_limit, 100.0)
        self.assertEqual(empty.transaction_history, [])
        self.assert_account_state(empty, 0.0, "ACTIVE", 0)

        funded = self.account_funded
        self.assertEqual(funded.account_id, "ACC002")
        self.assertEqual(funded.owner, "Bob")
        self.assertEqual(funded.overdraft_limit, 50.0)
        self.assert_account_state(funded, 200.0, "ACTIVE", 1)
        self.assertDictEqual(funded.transaction_history[0], {
            "type": "INITIAL_DEPOSIT",
            "amount": 200.0,
            "fee": 0.0,
            "balance_after": 200.0,
            "description": "Initial account opening deposit"
        })

    def test_deposit_updates_multiple_attributes(self):
        """存入 150 元，验证余额、状态、交易记录及摘要。"""
        account = self.account_empty

        self.assertTrue(account.deposit(150.0))

        self.assert_account_state(account, 150.0, "ACTIVE", 1)
        self.assertDictEqual(account.transaction_history[-1], {
            "type": "DEPOSIT",
            "amount": 150.0,
            "fee": 0.0,
            "balance_after": 150.0,
            "description": "Deposit of $150.00"
        })
#取款 50 元并收取 2.50 元手续费
    def test_withdrawal_within_balance_multi_attributes(self):
        account = self.account_funded
        initial_transaction = deepcopy(account.transaction_history[0])

        self.assertTrue(account.withdraw(50.0, fee=2.50))

        self.assert_account_state(account, 147.50, "ACTIVE", 2)
        self.assertEqual(account.transaction_history[0], initial_transaction)
        self.assertDictEqual(account.transaction_history[-1], {
            "type": "WITHDRAWAL",
            "amount": 50.0,
            "fee": 2.50,
            "balance_after": 147.50,
            "description": "Withdrawal of $50.00 (Fee: $2.50)"
        })
#验证透支状态、恰好达到透支上限及超限拒绝
    def test_overdraft_withdrawal_and_status_transition(self):
        account = self.account_empty

        self.assertTrue(account.withdraw(50.0))
        self.assert_account_state(account, -50.0, "OVERDRAWN", 1)
        self.assertEqual(account.transaction_history[-1]["amount"], 50.0)
        self.assertEqual(account.transaction_history[-1]["fee"], 0.0)

        self.assertTrue(account.withdraw(50.0))
        self.assert_account_state(account, -100.0, "OVERDRAWN", 2)

        before = deepcopy(account.__dict__)
        with self.assertRaises(ValueError):
            account.withdraw(0.01)
        self.assertEqual(account.__dict__, before)
#验证部分偿还、恰好归零和恢复正余额
    def test_deposit_recovering_from_overdrawn_status(self):
        account = self.account_empty
        account.withdraw(50.0)

        self.assertTrue(account.deposit(20.0))
        self.assert_account_state(account, -30.0, "OVERDRAWN", 2)

        self.assertTrue(account.deposit(30.0))
        self.assert_account_state(account, 0.0, "ACTIVE", 3)

        self.assertTrue(account.deposit(10.0))
        self.assert_account_state(account, 10.0, "ACTIVE", 4)
        self.assertEqual(
            [record["type"] for record in account.transaction_history],
            ["WITHDRAWAL", "DEPOSIT", "DEPOSIT", "DEPOSIT"]
        )
#转账 50 元，发送方承担 5 元手续费
    def test_transfer_between_accounts_multi_attributes(self):
        sender = self.account_funded
        recipient = self.account_empty

        self.assertTrue(
            sender.transfer_to(recipient, 50.0, transfer_fee=5.0)
        )

        self.assert_account_state(sender, 145.0, "ACTIVE", 2)
        self.assert_account_state(recipient, 50.0, "ACTIVE", 1)

        withdrawal = sender.transaction_history[-1]
        self.assertEqual(withdrawal["type"], "WITHDRAWAL")
        self.assertEqual(withdrawal["amount"], 50.0)
        self.assertEqual(withdrawal["fee"], 5.0)

        deposit = recipient.transaction_history[-1]
        self.assertEqual(deposit["type"], "DEPOSIT")
        self.assertEqual(deposit["amount"], 50.0)
        self.assertEqual(deposit["fee"], 0.0)

        # 两个账户的总余额只减少手续费
        self.assertAlmostEqual(sender.balance + recipient.balance, 195.0)
#冻结后禁止存取款及双向转账，解冻后恢复正确状态
    def test_frozen_account_restrictions(self):
        account = self.account_funded
        other = self.account_empty
        account.freeze()
        self.assert_account_state(account, 200.0, "FROZEN", 1)

        operations = [
            lambda: account.deposit(10.0),
            lambda: account.withdraw(10.0),
            lambda: account.transfer_to(other, 10.0),
            lambda: other.transfer_to(account, 10.0)
        ]

        for index, operation in enumerate(operations):
            with self.subTest(operation=index):
                before_account = deepcopy(account.__dict__)
                before_other = deepcopy(other.__dict__)
                with self.assertRaises(RuntimeError):
                    operation()
                self.assertEqual(account.__dict__, before_account)
                self.assertEqual(other.__dict__, before_other)

        account.unfreeze()
        self.assert_account_state(account, 200.0, "ACTIVE", 1)

        other.withdraw(20.0)
        other.freeze()
        self.assert_account_state(other, -20.0, "FROZEN", 1)
        other.unfreeze()
        self.assert_account_state(other, -20.0, "OVERDRAWN", 1)
#验证非法参数被拒绝，且失败操作不改变账户数据
    def test_invalid_operations_raise_exceptions(self):
        with self.assertRaises(ValueError):
            BankAccount("BAD1", "Alice", initial_balance=-1.0)
        with self.assertRaises(ValueError):
            BankAccount("BAD2", "Alice", overdraft_limit=-1.0)

        account = self.account_funded
        target = self.account_empty

        cases = [
            (ValueError, lambda: account.deposit(0)),
            (ValueError, lambda: account.deposit(-10)),
            (ValueError, lambda: account.withdraw(0)),
            (ValueError, lambda: account.withdraw(-10)),
            (ValueError, lambda: account.withdraw(10, fee=-1)),
            # 可用额度为 250；手续费也必须计入。
            (ValueError, lambda: account.withdraw(250, fee=0.01)),
            (ValueError, lambda: account.transfer_to(target, 0)),
            (ValueError, lambda: account.transfer_to(target, -10)),
            (ValueError, lambda: account.transfer_to(
                target, 10, transfer_fee=-1
            )),
            (ValueError, lambda: account.transfer_to(target, 251)),
            (TypeError, lambda: account.transfer_to("not an account", 10))
        ]

        for index, (exception, operation) in enumerate(cases):
            with self.subTest(case=index):
                before_account = deepcopy(account.__dict__)
                before_target = deepcopy(target.__dict__)
                with self.assertRaises(exception):
                    operation()
                self.assertEqual(account.__dict__, before_account)
                self.assertEqual(target.__dict__, before_target)


if __name__ == "__main__":
    unittest.main()
