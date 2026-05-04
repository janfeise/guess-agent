# -*- coding: utf-8 -*-
"""更新测试文件以使用私有属性"""

# 读取 test_fsm.py
with open('tests/test_fsm.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有 self.fsm.state = 为 self.fsm._state = 
content = content.replace('self.fsm.state = ', 'self.fsm._state = ')

# 替换所有 self.fsm.round_count = 为 self.fsm._round_count = 
content = content.replace('self.fsm.round_count = ', 'self.fsm._round_count = ')

# 替换所有 self.fsm.max_rounds = 为 self.fsm._max_rounds = 
content = content.replace('self.fsm.max_rounds = ', 'self.fsm._max_rounds = ')

# 写回文件
with open('tests/test_fsm.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ test_fsm.py 已更新：state/round_count/max_rounds 赋值改为使用私有属性")

# 对 test_integration_examples.py 做同样的处理
with open('tests/test_integration_examples.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('fsm.state = ', 'fsm._state = ')
content = content.replace('fsm.round_count = ', 'fsm._round_count = ')
content = content.replace('fsm.max_rounds = ', 'fsm._max_rounds = ')

with open('tests/test_integration_examples.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ test_integration_examples.py 已更新：state/round_count/max_rounds 赋值改为使用私有属性")
