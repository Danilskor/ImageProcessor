import dataclasses

import numpy as np

from src.base import InvalidLUTFileError, InvalidLUTSizeError


@dataclasses.dataclass
class CubeData:
    title: str
    lut_size: int
    domain_min: tuple[float, float, float]
    domain_max: tuple[float, float, float]
    # Shape: (lut_size, lut_size, lut_size, 3), float32, values in [0, 1]
    # Axes: [B_index, G_index, R_index, channel]
    table: np.ndarray


class CubeFileParser:
    @staticmethod
    def parse(path: str) -> CubeData:
        title = ""
        lut_size: int | None = None
        domain_min = (0.0, 0.0, 0.0)
        domain_max = (1.0, 1.0, 1.0)
        entries: list[list[float]] = []

        try:
            with open(path, "r") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if line.upper().startswith("TITLE"):
                        title = line.split(None, 1)[1].strip().strip('"')
                    elif line.upper().startswith("LUT_3D_SIZE"):
                        lut_size = int(line.split()[1])
                        if not (2 <= lut_size <= 256):
                            raise InvalidLUTSizeError(
                                f"LUT_3D_SIZE {lut_size} is outside valid range [2, 256]"
                            )
                    elif line.upper().startswith("DOMAIN_MIN"):
                        parts = line.split()
                        domain_min = (float(parts[1]), float(parts[2]), float(parts[3]))
                    elif line.upper().startswith("DOMAIN_MAX"):
                        parts = line.split()
                        domain_max = (float(parts[1]), float(parts[2]), float(parts[3]))
                    elif line.upper().startswith("LUT_1D_SIZE"):
                        raise InvalidLUTFileError("1D LUT files are not supported by this parser")
                    else:
                        parts = line.split()
                        if len(parts) == 3:
                            try:
                                entries.append([float(p) for p in parts])
                            except ValueError:
                                pass  # skip unrecognised keyword lines
        except OSError as e:
            raise InvalidLUTFileError(f"Cannot open LUT file: {e}") from e

        if lut_size is None:
            raise InvalidLUTFileError("LUT_3D_SIZE not found in .cube file")

        expected = lut_size ** 3
        if len(entries) != expected:
            raise InvalidLUTFileError(
                f"Expected {expected} entries for LUT size {lut_size}, got {len(entries)}"
            )

        # .cube iterates R fastest, B slowest → reshape gives [B, G, R, channel]
        table = np.array(entries, dtype=np.float32).reshape(lut_size, lut_size, lut_size, 3)

        return CubeData(
            title=title,
            lut_size=lut_size,
            domain_min=domain_min,
            domain_max=domain_max,
            table=table,
        )
