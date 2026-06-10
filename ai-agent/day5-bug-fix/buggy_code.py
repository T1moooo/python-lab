import sys

# Ensure the standard output can handle Unicode characters
# Removed reconfigure to avoid potential issues on unsupported environments

def calculate_average(numbers):
    """计算数字列表的平均值"""
    if not numbers:
        return 0
    # Filter out None and non-numeric values
    filtered = [n for n in numbers if isinstance(n, (int, float)) and n is not None]
    if not filtered:
        return 0
    total = sum(filtered)
    return total / len(filtered)


def find_max(numbers):
    """找到最大值"""
    if not numbers:
        raise ValueError("Empty list has no maximum")
    # Filter out None and non-numeric values
    filtered = [n for n in numbers if isinstance(n, (int, float)) and n is not None]
    if not filtered:
        raise ValueError("List contains only None values")
    max_num = filtered[0]
    for num in filtered[1:]:
        if num > max_num:
            max_num = num
    return max_num


def reverse_string(text):
    """反转字符串"""
    if text is None:
        return ''
    return str(text)[::-1]


def count_vowels(text):
    """统计元音字母数量"""
    if not text:
        return 0
    vowels = "aeiouAEIOU"
    count = 0
    for char in str(text):
        if char in vowels:
            count += 1
    return count


def is_palindrome(text):
    """判断是否是回文"""
    if not text:
        return True
    cleaned = ''.join(ch.lower() for ch in str(text) if not ch.isspace())
    reversed_text = reverse_string(cleaned)
    return cleaned == reversed_text