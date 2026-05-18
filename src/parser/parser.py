from typing import List, Any
import re


class Parser:
    @staticmethod
    def parse(path: str) -> List[List[Any]]:
        lines_tokens: List[List[Any]] = []

        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                brackets_match = re.search(r"\[(.*?)\]", line)
                base_line = re.sub(r"\[.*?\]", "", line).strip()
                tokens: List[Any] = base_line.split()

                if brackets_match:
                    inside_brackets = brackets_match.group(1)
                    brackets_tokens = inside_brackets.split()
                    tokens.append(brackets_tokens)
                else:
                    tokens.append([])
                lines_tokens.append(tokens)
        return lines_tokens
