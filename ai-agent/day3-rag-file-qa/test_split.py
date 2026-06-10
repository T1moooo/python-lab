def split_by_sentence(text: str, min_length: int = 50) -> list[str]:
    text = text.replace("?", "?|").replace("!", "!|").replace(".", ".|")
    sentences = [s.strip() for s in text.split("|") if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) < min_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# 测试
test_text = "Python is great. It was created by Guido. Python 2.0 was released in 2000. Python 3.0 came later in 2008. It is very popular."

result = split_by_sentence(test_text, min_length=50)

print(f"输入文本: {test_text}\n")
print(f"分块结果（共 {len(result)} 块）:")
for i, chunk in enumerate(result):
    print(f"  块{i+1} ({len(chunk)}字符): {chunk}")
