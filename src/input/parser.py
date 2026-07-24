from .line import Line

from typing import List, Dict, Tuple


class Parser:
    @staticmethod
    def _split_meta(line_number: int, line: str) -> Tuple[str, str | None]:
        brackets: Tuple[int, int] = (line.count("["), line.count("]"))

        if brackets[0] > 1 or brackets[1] > 1:  # [[]]
            raise ValueError(f"Line {line_number}: Too many square brackets")
        if brackets[0] == 1 and brackets[1] == 0:  # [
            raise ValueError(f"Line {line_number}:"
                             f"There is no close square bracket")
        if brackets[0] == 0 and brackets[1] == 1:  # ]
            raise ValueError(f"Line {line_number}:"
                             f"There is no open square bracket")
        if brackets[0] == 1 and brackets[1] == 1:
            if not line.rstrip().endswith("]"):
                raise ValueError(
                    f"Line {line_number}: Meta"
                    f" section must be the last element"
                )
        if brackets[0] == 0 and brackets[1] == 0:  # There is no meta
            return (line, None)
        start = line.index("[")
        return (
            line[:start].strip(),
            line[start:].strip()
        )

    @staticmethod
    def _parse_meta(line_number: int, line: str | None) -> Dict[str, str]:
        meta_dic: Dict[str, str] = {}
        if not line:
            return meta_dic
        for pair in line[1: -1].split():
            if pair.count("=") != 1:
                raise ValueError(
                    f"Line {line_number}: amount of '=' is not 1")
            key, value = pair.split("=", 1)
            meta_dic[key] = value
        return meta_dic

    @staticmethod
    def parse(path: str) -> List[Line]:
        lines: List[Line] = []

        with open(path, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = Parser._split_meta(line_number, line)
                meta_dict: Dict[str, str] = Parser._parse_meta(
                    line_number, parts[1])
                lines.append(Line(line_number=line_number,
                                  arguments=parts[0].split(),
                                  meta=meta_dict))
        return lines
