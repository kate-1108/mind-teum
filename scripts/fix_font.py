"""TTF에서 손상된 kern 테이블을 제거하는 스크립트."""
import struct, math, sys

def remove_kern(src_path, dst_path):
    with open(src_path, "rb") as f:
        data = bytearray(f.read())

    # --- Offset Table (12 bytes) ---
    sfVersion, num_tables = struct.unpack_from(">IH", data, 0)
    table_dir_offset = 12

    # --- Table Directory ---
    tables = {}
    for i in range(num_tables):
        off = table_dir_offset + i * 16
        tag, checksum, tbl_offset, tbl_length = struct.unpack_from(">4sIII", data, off)
        tables[tag.decode("ascii")] = (i, off, checksum, tbl_offset, tbl_length)

    if "kern" not in tables:
        print("kern 테이블 없음 — 그대로 복사")
        import shutil; shutil.copy(src_path, dst_path)
        return

    kern_idx, kern_dir_off, _, kern_data_off, kern_data_len = tables["kern"]
    print(f"kern 제거: offset={kern_data_off}, length={kern_data_len}")

    # 새 table 수
    new_num = num_tables - 1
    n = new_num
    max_pow2 = 1 << int(math.log2(n)) if n > 0 else 1
    new_search_range = max_pow2 * 16
    new_entry_selector = int(math.log2(max_pow2))
    new_range_shift = n * 16 - new_search_range

    # 새 Offset Table 작성
    new_header = struct.pack(">IHHHH",
        sfVersion, new_num, new_search_range, new_entry_selector, new_range_shift)

    # kern 제외한 나머지 테이블 디렉토리 수집
    remaining = [(tag, v) for tag, v in tables.items() if tag != "kern"]
    remaining.sort(key=lambda x: x[1][3])  # offset 순 정렬

    # kern 데이터를 제외한 테이블 데이터 재배치
    # 새 디렉토리 크기
    new_dir_size = new_num * 16
    new_data_start = 12 + new_dir_size

    new_dir = bytearray()
    new_data = bytearray()
    offset_map = {}  # 기존 offset → 새 offset

    for tag, (idx, dir_off, checksum, tbl_offset, tbl_length) in remaining:
        if tbl_offset == kern_data_off:
            continue  # kern 자체는 건너뜀
        # 4-byte 정렬
        pad = (4 - len(new_data) % 4) % 4
        new_data.extend(b"\x00" * pad)
        new_off = new_data_start + len(new_data)
        tbl_data = data[tbl_offset:tbl_offset + tbl_length]
        new_data.extend(tbl_data)
        new_dir.extend(struct.pack(">4sIII",
            tag.encode("ascii"), checksum, new_off, tbl_length))

    result = new_header + new_dir + new_data
    with open(dst_path, "wb") as f:
        f.write(result)
    print(f"저장 완료: {dst_path} ({len(result):,} bytes)")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else r"E:\projects\mind-teum\fonts\GangwonEduSaeum.ttf"
    dst = sys.argv[2] if len(sys.argv) > 2 else r"E:\projects\mind-teum\fonts\GangwonEduSaeum-fixed.ttf"
    remove_kern(src, dst)
