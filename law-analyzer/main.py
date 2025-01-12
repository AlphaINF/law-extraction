import json, docx, re, copy, os
from part_parser import parseParts


# 所有实现遵循以可读性换性能的原则，不作过度优化


def extractTitleAndContents(lines):
    begin_idx, end_idx, title_idx = -1, -1, -1
    title_pattern = re.compile(r"法|条例|解释|办法")
    title = ""

    for idx, line in enumerate(lines):
        if (begin_idx == -1):
            if (title_pattern.findall(line)):
                if len(title) == 0:
                    title = line
                    title_idx = idx
            elif (line == "目　　录"):
                begin_idx = idx + 1
            else:
                continue
        else:
            if (line == ""):
                end_idx = idx
                break
            else:
                continue

    if end_idx == -1:
        for idx, line in enumerate(lines):
            if line.strip().startswith('第一'):
                end_idx = idx - 1
                break

    return title, lines[end_idx + 1:]


def parseLaw(lines):
    title, contents = extractTitleAndContents(lines)
    parts = parseParts(contents)
    dic = {}
    output = []

    for part in parts:
        for subpart in part.subparts:
            for chapter in subpart.chapters:
                for section in chapter.sections:
                    for article in section.articles:
                        dic["id"] = article.id
                        dic["text"] = list(filter(lambda x: x != "", article.contents))
                        dic["chapter_id"] = list(filter(None, [part.id, subpart.id, chapter.id, section.id]))
                        dic["hierarchy"] = list(filter(None, [part.name, subpart.name, chapter.name, section.name]))
                        dic["law"] = title
                        output.append(copy.deepcopy(dic))

    return output


def process_document(doc_path):
    doc = docx.Document(doc_path)
    stripped_lines = list(map(lambda x: x.text.lstrip(), doc.paragraphs))
    return parseLaw(stripped_lines)

if __name__ == '__main__':
    assets_path = "./assets"
    output_path = "./output.txt"

    # 获取目录下所有的 .docx 文件
    docx_files = [f for f in os.listdir(assets_path) if f.endswith('.docx')]

    with open(output_path, "w", encoding="utf-8") as f:
        for docx_file in docx_files:
            doc_path = os.path.join(assets_path, docx_file)
            output = process_document(doc_path)

            # 将输出的 JSON 对象写入文件，以 JSONL 格式存储
            for item in output:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
