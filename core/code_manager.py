"""
Code Manager - Fetch, cache và quản lý queue code từ yumifang3.site
Tích hợp vào Macro Studio để hỗ trợ action type set_clipboard_code.
"""

import json
import re
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

from PySide6.QtCore import QObject, Signal

API_URL = "https://yumifang3.site/fang3/zfy"


@dataclass
class CodeItem:
    id: int
    context: str

    def preview(self, max_len: int = 30) -> str:
        text = self.context
        if len(text) > max_len:
            text = text[:max_len] + "…"
        return f"#{self.id}: {text}"


class CodeManager(QObject):
    """Quản lý code: fetch từ API, cache vào JSON, cung cấp queue cho macro."""

    codes_loaded = Signal(list)       # list[CodeItem]
    error_occurred = Signal(str)

    def __init__(self, json_path: Path) -> None:
        super().__init__()
        self.json_path = json_path
        self._all_codes: list[CodeItem] = []
        self._queue: list[CodeItem] = []
        self._queue_index: int = 0
        self._lock = threading.Lock()

    # ─── Fetch từ API ───────────────────────────────────

    def fetch_from_api(self) -> None:
        """Gọi API trên thread riêng, lưu vào JSON, phát signal."""
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self) -> None:
        try:
            req = Request(API_URL, headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=15) as resp:
                raw = json.loads(resp.read().decode("utf-8"))

            items = raw.get("data", [])
            codes = []
            for item in items:
                try:
                    code_id = int(item.get("id", 0))
                    context = str(item.get("context", ""))
                    # Xóa toàn bộ khoảng trắng, dấu cách, dấu xuống dòng, tab (do code game không có khoảng trắng)
                    context = re.sub(r'\s+', '', context)
                    if code_id > 0 and context:
                        codes.append(CodeItem(id=code_id, context=context))
                except (ValueError, TypeError):
                    continue

            codes.sort(key=lambda c: c.id)

            # Lưu vào JSON
            payload = {
                "last_updated": datetime.now().isoformat(timespec="seconds"),
                "codes": [asdict(c) for c in codes],
            }
            self.json_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            with self._lock:
                self._all_codes = codes

            self.codes_loaded.emit(codes)

        except (URLError, json.JSONDecodeError, OSError) as exc:
            self.error_occurred.emit(f"Lỗi tải code: {exc}")

    def import_from_text(self, text: str) -> None:
        """Đọc codes từ đoạn văn bản (text), lưu vào JSON và phát signal."""
        try:
            codes = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Hỗ trợ định dạng: "1. code", "1 code", "1/ code", "1- code", "1: code", "1) code", v.v.
                match = re.match(r'^\s*(\d+)[.\s/:_)-]+\s*(.*)$', line)
                if match:
                    code_id = int(match.group(1))
                    context = match.group(2) # Giữ nguyên khoảng cách, không xóa khoảng trắng
                    if code_id > 0 and context:
                        codes.append(CodeItem(id=code_id, context=context))
            
            if not codes:
                self.error_occurred.emit("Không tìm thấy code nào hợp lệ trong đoạn văn bản.")
                return

            codes.sort(key=lambda c: c.id)

            # Lưu vào JSON
            payload = {
                "last_updated": datetime.now().isoformat(timespec="seconds"),
                "codes": [asdict(c) for c in codes],
            }
            self.json_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            with self._lock:
                self._all_codes = codes

            self.codes_loaded.emit(codes)
        except Exception as exc:
            self.error_occurred.emit(f"Lỗi khi nhập code từ văn bản: {exc}")

    # ─── Load từ JSON (offline) ─────────────────────────

    def load_from_json(self) -> None:
        """Đọc codes.json đã cache, phát signal."""
        try:
            if not self.json_path.exists():
                self.error_occurred.emit("Chưa có file codes.json. Hãy tải code từ web trước.")
                return

            raw = json.loads(self.json_path.read_text(encoding="utf-8"))
            items = raw.get("codes", [])
            codes = []
            for item in items:
                try:
                    context = str(item["context"])
                    context = re.sub(r'\s+', '', context)
                    codes.append(CodeItem(id=int(item["id"]), context=context))
                except (KeyError, ValueError, TypeError):
                    continue

            codes.sort(key=lambda c: c.id)

            with self._lock:
                self._all_codes = codes

            self.codes_loaded.emit(codes)

        except (json.JSONDecodeError, OSError) as exc:
            self.error_occurred.emit(f"Lỗi đọc codes.json: {exc}")

    # ─── Lọc theo phạm vi ──────────────────────────────

    def get_filtered(self, range_text: str) -> list[CodeItem]:
        """Lọc code theo phạm vi. Hỗ trợ: '1-50', '1 5 10-20', rỗng = tất cả."""
        with self._lock:
            all_codes = list(self._all_codes)

        if not range_text.strip():
            return all_codes

        ids_to_include: set[int] = set()
        for part in range_text.strip().split():
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                segments = part.split("-", 1)
                try:
                    start, end = int(segments[0]), int(segments[1])
                    for i in range(start, end + 1):
                        ids_to_include.add(i)
                except ValueError:
                    continue
            else:
                try:
                    ids_to_include.add(int(part))
                except ValueError:
                    continue

        return [c for c in all_codes if c.id in ids_to_include]

    # ─── Queue cho macro loop ───────────────────────────

    def setup_queue(self, range_text: str) -> int:
        """Tạo queue code theo phạm vi. Trả về số lượng code trong queue."""
        filtered = self.get_filtered(range_text)
        with self._lock:
            self._queue = filtered
            self._queue_indices = {} # Khởi tạo lại indices dictionary
        return len(filtered)

    def next_code(self, device_id: str) -> Optional[str]:
        """Lấy code tiếp theo trong queue cho thiết bị cụ thể. Trả về None nếu hết."""
        with self._lock:
            if device_id not in self._queue_indices:
                self._queue_indices[device_id] = 0
                
            idx = self._queue_indices[device_id]
            if idx >= len(self._queue):
                return None
            code = self._queue[idx]
            self._queue_indices[device_id] = idx + 1
            return code.context

    def reset_queue(self, device_id: str = None) -> None:
        """Reset queue về đầu. Nếu truyền device_id thì chỉ reset cho thiết bị đó, ngược lại reset tất cả."""
        with self._lock:
            if device_id is not None:
                self._queue_indices[device_id] = 0
            else:
                self._queue_indices.clear()

    def get_progress(self, device_id: str) -> tuple[int, int]:
        """Trả về (current_index, total) của queue cho thiết bị."""
        with self._lock:
            idx = self._queue_indices.get(device_id, 0)
            return idx, len(self._queue)

    def get_current_code_id(self, device_id: str) -> Optional[int]:
        """Trả về ID của code vừa được lấy (cho hiển thị) của thiết bị."""
        with self._lock:
            idx = self._queue_indices.get(device_id, 0) - 1
            if 0 <= idx < len(self._queue):
                return self._queue[idx].id
            return None

    @property
    def total_codes(self) -> int:
        with self._lock:
            return len(self._all_codes)
