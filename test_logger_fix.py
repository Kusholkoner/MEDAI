import sys
sys.path.insert(0, r'c:\Users\User\Desktop\MEDAI')

from main import logger

# Test that the warning method exists and works
print("Testing EventsLogger.warning method...")

# Test 1: Check method exists
assert hasattr(logger, 'warning'), "EventsLogger should have a 'warning' method"
print("✓ warning method exists")

# Test 2: Call the warning method
logger.warning("Test warning message", test_param="test_value")
print("✓ warning method can be called")

# Test 3: Verify it was logged
logs = logger.dump()
warning_logs = [log for log in logs['logs'] if log['level'] == 'WARNING']
assert len(warning_logs) > 0, "Warning should be logged"
print("✓ warning message was logged correctly")

print("\nAll tests passed! ✅")
print(f"Last warning log: {warning_logs[-1]}")
