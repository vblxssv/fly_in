from typing import Dict, Any
import re


class Parser:
    @staticmethod
    def _parse_meta(meta_str: str) -> Dict[str, str]:
        if not meta_str:
            return {}

        meta_dict: Dict[str, str] = {}
        items = meta_str.strip().split()

        for item in items:
            if '=' not in item:
                raise ValueError(f"Error: meta item '{item}' must contain '='")
            key, value = item.split('=', 1)
            if not key or not value:
                raise ValueError(f"Error: invalid meta format in '{item}'")
            meta_dict[key] = value
        return meta_dict

    @classmethod
    def parse(cls, path: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {"hubs": [], "connections": []}
        meta_pattern = re.compile(r"\[(.*?)\]")

        with open(path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if ':' not in line:
                    raise ValueError(
                        f"Error in line {line_num}: missing ':' separator. "
                        f"Line content: '{line}'"
                    )

                meta_match = meta_pattern.search(line)
                meta_data = cls._parse_meta(
                    meta_match.group(1) if meta_match else ""
                )

                clean_line = meta_pattern.sub("", line).strip()
                key, _, val = clean_line.partition(':')
                key = key.strip()
                tokens = val.strip().split()

                if key in ['start_hub', 'end_hub', 'hub']:
                    if len(tokens) < 3:
                        raise ValueError(
                            f"Error: line {line_num} must contain a name "
                            "and coordinates (x, y)"
                        )
                    data['hubs'].append({
                        "type": key,
                        "name": tokens[0],
                        "coords": {"x": int(tokens[1]), "y": int(tokens[2])},
                        "meta": meta_data
                    })
                elif key == 'connection':
                    if '-' not in tokens[0]:
                        raise ValueError(
                            f"Error: invalid connection format '{tokens[0]}'. "
                            "Expected 'from-to'"
                        )
                    nodes = tokens[0].split('-')
                    data['connections'].append({
                        "from": nodes[0],
                        "to": nodes[1],
                        "meta": meta_data
                    })
                elif key == 'nb_drones':
                    if not tokens[0].isdigit():
                        raise ValueError(
                            f"Error: nb_drones must be a number, "
                            f"got '{tokens[0]}'"
                        )
                    data[key] = int(tokens[0])
                else:
                    raise ValueError(f"Error: unknown key '{key}'")

        start_hubs = [h for h in data['hubs'] if h['type'] == 'start_hub']
        end_hubs = [h for h in data['hubs'] if h['type'] == 'end_hub']

        if len(start_hubs) != 1:
            raise ValueError(
                f"Error: expected exactly one "
                f"start_hub, found {len(start_hubs)}"
            )
        if len(end_hubs) != 1:
            raise ValueError(
                f"Error: expected exactly one end_hub, found {len(end_hubs)}"
            )

        if 'nb_drones' not in data:
            raise ValueError("Error: missing required parameter 'nb_drones'")

        return data
