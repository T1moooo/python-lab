# 测试文件：用于验证 buggy_code.py 的修复情况

from buggy_code import calculate_average, find_max, reverse_string, count_vowels, is_palindrome


def test_calculate_average():
    """测试 calculate_average"""
    # 测试正常情况
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0, "平均值计算错误"

    # 测试空列表（这是 bug）
    result = calculate_average([])
    if result == 0:
        print("  [PASS] 空列表返回 0")
    else:
        print(f"  [FAIL] 空列表返回值错误: 期望 0, 实际 {result}")


def test_find_max():
    """测试 find_max"""
    # 测试正数
    assert find_max([1, 5, 3, 9, 2]) == 9, "最大值应该是 9"

    # 测试负数（这是 bug）
    result = find_max([-5, -3, -1, -10])
    if result == -1:
        print("  [PASS] 负数最大值正确")
    else:
        print(f"  [FAIL] 负数最大值错误: 期望 -1, 实际 {result}")


def test_reverse_string():
    """测试 reverse_string"""
    # 测试正常字符串
    result = reverse_string("hello")
    if result == "olleh":
        print("  [PASS] 字符串反转正确")
    else:
        print(f"  [FAIL] 字符串反转错误: 期望 'olleh', 实际 '{result}'")


def test_count_vowels():
    """测试 count_vowels"""
    # 测试小写
    assert count_vowels("hello") == 2, "hello 有 2 个元音"

    # 测试大写（这是 bug）
    result = count_vowels("Hello World")
    if result == 3:
        print("  [PASS] 大写元音统计正确")
    else:
        print(f"  [FAIL] 大写元音统计错误: 期望 3, 实际 {result}")


def test_is_palindrome():
    """测试 is_palindrome"""
    # 测试普通回文
    assert is_palindrome("racecar") == True, "racecar 是回文"

    # 测试带空格和大小写的回文（这是 bug）
    result = is_palindrome("A man a plan a canal Panama")
    if result == True:
        print("  [PASS] 复杂回文判断正确")
    else:
        print(f"  [FAIL] 复杂回文判断错误: 期望 True, 实际 {result}")


if __name__ == "__main__":
    print("运行测试...\n")

    print("测试 calculate_average:")
    test_calculate_average()

    print("\n测试 find_max:")
    test_find_max()

    print("\n测试 reverse_string:")
    test_reverse_string()

    print("\n测试 count_vowels:")
    test_count_vowels()

    print("\n测试 is_palindrome:")
    test_is_palindrome()

    print("\n测试完成!")
