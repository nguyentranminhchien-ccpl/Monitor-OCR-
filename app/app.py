import os
import sys
import json
import base64
import glob
import re
from datetime import datetime, timedelta
import io
import time
import requests
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

USER_HOME = os.path.expanduser("~")
DEFAULT_PATIENT_ROOT = os.environ.get("PATIENT_ROOT_DIR", os.path.join(USER_HOME, "Documents"))

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
        "patient_root_dir": DEFAULT_PATIENT_ROOT,
        "default_model": "gemini-3.1-flash-lite",
        "step_minutes": 3,
        "default_impute": "forward-fill"
    }

def save_config(cfg):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_effective_model(cfg):
    model = cfg.get("default_model", "gemini-3.1-flash-lite")
    if model in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]:
        model = "gemini-3.1-flash-lite"
    return model

# ==================== GEMINI VISION API ====================

def standardize_time(t_str):
    if not t_str:
        return ""
    t_str = str(t_str).strip()
    m = re.match(r"^(\d{1,2}):(\d{1,2})(?::\d{1,2})?$", t_str)
    if m:
        h, mn = int(m.group(1)), int(m.group(2))
        return f"{h:02d}:{mn:02d}"
    return t_str

def parse_time_str(t_str):
    t_str = standardize_time(t_str)
    parts = t_str.split(':')
    return int(parts[0]), int(parts[1])

def clean_val(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return int(round(val))
    val_str = str(val).strip()
    if val_str in ["", "-", "--", "---", "-?-", "null", "None", "?", "N/A"]:
        return None
    m = re.search(r'\d+', val_str)
    if m:
        return int(m.group(0))
    return None

# ==================== GEMINI VISION API ====================

def call_gemini_vision(image_bytes, mime_type, api_key, model="gemini-3.1-flash-lite"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    prompt = """Bạn là chuyên gia phân tích ảnh màn hình monitor theo dõi huyết động bệnh nhân trong can thiệp lấy huyết khối (EVT) (Philips IntelliVue MX550/MP70, GE, Mindray...).
Nhiệm vụ: Trích xuất TOÀN BỘ các cột dữ liệu lịch sử theo từng phút hiển thị trong bảng "Vital Signs" (Dấu hiệu sinh tồn) trên màn hình.

Quy tắc trích xuất từng cột thời gian:
- time: Giờ hiển thị ở dòng dưới cùng của bảng, định dạng chuẩn 24h "HH:MM" (ví dụ "00:54", "01:00", "17:30"). Nếu là 1 chữ số giờ như 0:54 hay 1:00, BẮT BUỘC thêm số 0 thành "00:54", "01:00".
- hr: Hàng HR (nhịp tim). Nếu ghi '-?-' hoặc để trống, trả về null.
- sbp: Hàng NBPs (huyết áp tâm thu). Nếu ghi '---' hoặc để trống, trả về null.
- dbp: Hàng NBPd (huyết áp tâm trương). Nếu ghi '---' hoặc để trống, trả về null.
- map: Hàng NBPm (huyết áp trung bình). Nếu ghi '---' hoặc để trống, trả về null.
- spo2: Hàng SpO2 (%). Nếu ghi '-?-' hoặc để trống, trả về null.
- etco2: Hàng etCO2. Nếu ghi '---' hoặc để trống, trả về null.
- rr: Hàng RR. Nếu ghi '-?-' hoặc để trống, trả về null.

BẮT BUỘC trả về dữ liệu thuần định dạng JSON Array of Objects, sắp xếp theo thời gian tăng dần:
[
  {
    "time": "00:54",
    "hr": 103,
    "sbp": 146,
    "dbp": 99,
    "map": 115,
    "spo2": 100,
    "etco2": 37,
    "rr": 15
  }
]
Tuyệt đối không bọc trong markdown code block, chỉ trả về JSON hợp lệ."""

    b64_data = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type or "image/jpeg",
                            "data": b64_data
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json"
        }
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=45)
    if resp.status_code != 200:
        raise Exception(f"Gemini API lỗi ({resp.status_code}): {resp.text}")

    resp_json = resp.json()
    try:
        raw_text = resp_json["candidates"][0]["content"]["parts"][0]["text"].strip()
        data = json.loads(raw_text)
        if isinstance(data, dict):
            for k in data:
                if isinstance(data[k], list):
                    data = data[k]
                    break
            else:
                data = [data]
        # Clean and standardize
        cleaned_list = []
        for r in data:
            t = standardize_time(r.get("time"))
            if t:
                cleaned_list.append({
                    "time": t,
                    "hr": clean_val(r.get("hr")),
                    "sbp": clean_val(r.get("sbp")),
                    "dbp": clean_val(r.get("dbp")),
                    "map": clean_val(r.get("map")),
                    "spo2": clean_val(r.get("spo2")),
                    "etco2": clean_val(r.get("etco2")),
                    "rr": clean_val(r.get("rr"))
                })
        return cleaned_list
    except Exception as e:
        raise Exception(f"Không thể phân tích kết quả JSON từ Gemini: {e}")

# ==================== DATA NORMALIZATION ====================

def normalize_vitals(raw_list, t0_str, tend_str, impute_method="forward-fill", step_minutes=3):
    """
    Chuẩn hóa chuỗi thời gian bắt đầu từ 0 phút tại t0_str,
    tăng đều step_minutes (3 phút/lần) cho đến tend_str.
    Hỗ trợ xử lý khuyết thiếu: forward-fill (lấy mốc trước), average (lấy trung bình), skip (bỏ qua).
    """
    t0_str = standardize_time(t0_str)
    tend_str = standardize_time(tend_str)
    
    # Chuẩn hóa time và deduplicate / merge dữ liệu thô
    merged = {}
    for item in raw_list:
        t = standardize_time(item.get("time"))
        if not t:
            continue
        cleaned = {
            "time": t,
            "hr": clean_val(item.get("hr")),
            "sbp": clean_val(item.get("sbp")),
            "dbp": clean_val(item.get("dbp")),
            "map": clean_val(item.get("map")),
            "spo2": clean_val(item.get("spo2")),
            "etco2": clean_val(item.get("etco2")),
            "rr": clean_val(item.get("rr")),
        }
        if t not in merged:
            merged[t] = cleaned
        else:
            # Merge: ưu tiên giữ số đo có giá trị thay vì null
            for k, v in cleaned.items():
                if v is not None and (merged[t].get(k) is None or k in ["sbp", "dbp", "map"]):
                    merged[t][k] = v

    h0, m0 = parse_time_str(t0_str)
    hend, mend = parse_time_str(tend_str)
    base_date = datetime(2026, 1, 1, h0, m0)
    end_date = datetime(2026, 1, 1, hend, mend)
    if end_date < base_date:
        end_date += timedelta(days=1)

    result = []
    curr = base_date
    minute_offset = 0

    last_valid_sbp = None
    last_valid_dbp = None
    last_valid_map = None
    last_valid_hr = None
    last_valid_spo2 = None
    last_valid_etco2 = None

    # Quét từng phút một để không bỏ sót các lần đo lẻ giữa các mốc 3 phút
    while curr <= end_date:
        t_str = curr.strftime("%H:%M")
        row_data = merged.get(t_str, {})
        
        has_real_sbp = row_data.get("sbp") is not None and row_data.get("dbp") is not None
        has_real_hr = row_data.get("hr") is not None
        has_real_spo2 = row_data.get("spo2") is not None
        has_real_etco2 = row_data.get("etco2") is not None

        if has_real_sbp:
            last_valid_sbp = row_data.get("sbp")
            last_valid_dbp = row_data.get("dbp")
            last_valid_map = row_data.get("map")
        if has_real_hr:
            last_valid_hr = row_data.get("hr")
        if has_real_spo2:
            last_valid_spo2 = row_data.get("spo2")
        if has_real_etco2:
            last_valid_etco2 = row_data.get("etco2")

        if minute_offset % step_minutes == 0:
            sbp = row_data.get("sbp")
            dbp = row_data.get("dbp")
            map_val = row_data.get("map")
            hr = row_data.get("hr")
            spo2 = row_data.get("spo2")
            etco2 = row_data.get("etco2")

            is_imputed = False

            if sbp is None or dbp is None:
                if impute_method == "forward-fill" and last_valid_sbp is not None:
                    sbp = last_valid_sbp
                    dbp = last_valid_dbp
                    map_val = last_valid_map
                    is_imputed = True

            if hr is None:
                if impute_method == "forward-fill" and last_valid_hr is not None:
                    hr = last_valid_hr
                    is_imputed = True

            if spo2 is None and impute_method == "forward-fill" and last_valid_spo2 is not None:
                spo2 = last_valid_spo2

            if etco2 is None and impute_method == "forward-fill" and last_valid_etco2 is not None:
                etco2 = last_valid_etco2

            result.append({
                "minute": minute_offset,
                "time": t_str,
                "hr": hr,
                "sbp": sbp,
                "dbp": dbp,
                "map": map_val,
                "spo2": spo2,
                "etco2": etco2,
                "method": "cuff",
                "_imputed": is_imputed
            })

        curr += timedelta(minutes=1)
        minute_offset += 1

    # Xử lý bù khuyết đầu chuỗi (nếu mốc 0 chưa gắn điện cực HR hoặc NBP)
    if impute_method == "forward-fill":
        first_valid_hr = None
        for r in result:
            if r["hr"] is not None:
                first_valid_hr = r["hr"]
                break
        if first_valid_hr is not None:
            for r in result:
                if r["hr"] is None:
                    r["hr"] = first_valid_hr
                    r["_imputed"] = True
                else:
                    break

        first_valid_sbp = None
        first_valid_dbp = None
        first_valid_map = None
        for r in result:
            if r["sbp"] is not None:
                first_valid_sbp = r["sbp"]
                first_valid_dbp = r["dbp"]
                first_valid_map = r["map"]
                break
        if first_valid_sbp is not None:
            for r in result:
                if r["sbp"] is None:
                    r["sbp"] = first_valid_sbp
                    r["dbp"] = first_valid_dbp
                    r["map"] = first_valid_map
                    r["_imputed"] = True
                else:
                    break

    # Lấy trung bình (Average mốc trước và mốc sau) nếu được chọn
    if impute_method in ["average", "linear-interpolation", "trung-binh"]:
        for i in range(len(result)):
            if result[i]["sbp"] is None:
                prev_i = None
                for p in range(i - 1, -1, -1):
                    if result[p]["sbp"] is not None:
                        prev_i = p
                        break
                next_i = None
                for n in range(i + 1, len(result)):
                    if result[n]["sbp"] is not None:
                        next_i = n
                        break

                if prev_i is not None and next_i is not None:
                    ratio = (i - prev_i) / (next_i - prev_i)
                    result[i]["sbp"] = int(round(result[prev_i]["sbp"] + ratio * (result[next_i]["sbp"] - result[prev_i]["sbp"])))
                    result[i]["dbp"] = int(round(result[prev_i]["dbp"] + ratio * (result[next_i]["dbp"] - result[prev_i]["dbp"])))
                    if result[prev_i]["map"] is not None and result[next_i]["map"] is not None:
                        result[i]["map"] = int(round(result[prev_i]["map"] + ratio * (result[next_i]["map"] - result[prev_i]["map"])))
                    if result[i]["hr"] is None and result[prev_i]["hr"] is not None and result[next_i]["hr"] is not None:
                        result[i]["hr"] = int(round(result[prev_i]["hr"] + ratio * (result[next_i]["hr"] - result[prev_i]["hr"])))
                    result[i]["_imputed"] = True

    return result

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    return send_from_directory(templates_dir, 'index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'GET':
        cfg = load_config()
        # Mask key for privacy
        masked_key = cfg.get("gemini_api_key", "")
        if masked_key and len(masked_key) > 8:
            masked_key = masked_key[:4] + "..." + masked_key[-4:]
        return jsonify({
            "has_key": bool(cfg.get("gemini_api_key")),
            "masked_key": masked_key,
            "patient_root_dir": cfg.get("patient_root_dir", DEFAULT_PATIENT_ROOT),
            "default_model": cfg.get("default_model", "gemini-2.0-flash"),
            "step_minutes": cfg.get("step_minutes", 3)
        })
    else:
        req_data = request.json or {}
        cfg = load_config()
        if "gemini_api_key" in req_data and req_data["gemini_api_key"]:
            cfg["gemini_api_key"] = req_data["gemini_api_key"].strip()
        if "patient_root_dir" in req_data:
            cfg["patient_root_dir"] = req_data["patient_root_dir"].strip()
        if "default_model" in req_data:
            cfg["default_model"] = req_data["default_model"].strip()
        save_config(cfg)
        return jsonify({"success": True, "message": "Đã lưu cấu hình thành công!"})

def find_image_files(folder_path):
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
    if not os.path.exists(folder_path):
        return []
    try:
        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(valid_exts) and os.path.isfile(os.path.join(folder_path, f))
        ]
        files.sort()
        return files
    except Exception:
        return []

@app.route('/api/patients', methods=['GET'])
def list_patients():
    cfg = load_config()
    root_dir = cfg.get("patient_root_dir", DEFAULT_PATIENT_ROOT)
    if not os.path.exists(root_dir):
        return jsonify({"error": f"Thư mục không tồn tại: {root_dir}", "patients": []})

    patients = []
    try:
        entries = os.listdir(root_dir)
        for entry in entries:
            full_path = os.path.join(root_dir, entry)
            if os.path.isdir(full_path):
                imgs = find_image_files(full_path)
                patients.append({
                    "name": entry,
                    "path": full_path,
                    "image_count": len(imgs)
                })
    except Exception as e:
        return jsonify({"error": str(e), "patients": []})

    return jsonify({"root_dir": root_dir, "patients": patients})

@app.route('/api/patient-images', methods=['GET'])
def get_patient_images():
    patient_path = request.args.get('path', '')
    if not patient_path or not os.path.exists(patient_path):
        return jsonify({"error": "Đường dẫn không hợp lệ", "images": []})

    imgs = find_image_files(patient_path)
    
    images_info = []
    for img_path in imgs:
        images_info.append({
            "filename": os.path.basename(img_path),
            "full_path": img_path,
            "size_kb": round(os.path.getsize(img_path) / 1024, 1)
        })

    return jsonify({"patient_path": patient_path, "images": images_info})

@app.route('/api/image-preview')
def image_preview():
    img_path = request.args.get('path', '')
    if not img_path or not os.path.exists(img_path):
        return "Image not found", 404
    dir_name = os.path.dirname(img_path)
    file_name = os.path.basename(img_path)
    return send_from_directory(dir_name, file_name)

@app.route('/api/ocr-image', methods=['POST'])
def ocr_single_image():
    cfg = load_config()
    api_key = cfg.get("gemini_api_key")
    if not api_key:
        return jsonify({"error": "Chưa cấu hình Gemini API Key! Vui lòng vào Cài đặt để nhập Key."}), 400

    model = cfg.get("default_model", "gemini-3.1-flash-lite")

    # Check if file upload or file path
    if 'file' in request.files:
        file = request.files['file']
        image_bytes = file.read()
        mime_type = file.mimetype or "image/jpeg"
        filename = file.filename
    else:
        req_json = request.json or {}
        img_path = req_json.get('image_path')
        if not img_path or not os.path.exists(img_path):
            return jsonify({"error": f"Không tìm thấy file ảnh: {img_path}"}), 404
        with open(img_path, 'rb') as f:
            image_bytes = f.read()
        mime_type = "image/jpeg"
        if img_path.lower().endswith(".png"):
            mime_type = "image/png"
        filename = os.path.basename(img_path)

    try:
        extracted = call_gemini_vision(image_bytes, mime_type, api_key, model=model)
        return jsonify({
            "success": True,
            "filename": filename,
            "records": extracted
        })
    except Exception as e:
        return jsonify({"error": str(e), "filename": filename}), 500

def process_ocr_chunk(image_paths, api_key, model="gemini-3.1-flash-lite"):
    prompt = """Bạn là chuyên gia phân tích ảnh màn hình monitor theo dõi huyết động bệnh nhân trong can thiệp lấy huyết khối (EVT) (Philips IntelliVue MX550/MP70, GE, Mindray...).
Nhiệm vụ: Trích xuất TOÀN BỘ các mốc thời gian hiển thị trong bảng "Vital Signs" (Dấu hiệu sinh tồn) trên các ảnh.

Quy tắc trích xuất từng cột thời gian:
- time: Giờ hiển thị ở dòng dưới cùng của bảng, định dạng chuẩn 24h "HH:MM" (ví dụ "00:54", "01:00", "17:30"). Nếu là 1 chữ số giờ như 0:54 hay 1:00, BẮT BUỘC thêm số 0 thành "00:54", "01:00".
- hr: Hàng HR (nhịp tim). Nếu ghi '-?-' hoặc để trống, trả về null.
- sbp: Hàng NBPs (huyết áp tâm thu). Nếu ghi '---' hoặc để trống, trả về null.
- dbp: Hàng NBPd (huyết áp tâm trương). Nếu ghi '---' hoặc để trống, trả về null.
- map: Hàng NBPm (huyết áp trung bình). Nếu ghi '---' hoặc để trống, trả về null.
- spo2: Hàng SpO2 (%). Nếu ghi '-?-' hoặc để trống, trả về null.
- etco2: Hàng etCO2. Nếu ghi '---' hoặc để trống, trả về null.
- rr: Hàng RR. Nếu ghi '-?-' hoặc để trống, trả về null.

BẮT BUỘC trả về dữ liệu thuần định dạng JSON Array of Objects, sắp xếp theo thời gian tăng dần:
[
  {
    "time": "00:54",
    "hr": 103,
    "sbp": 146,
    "dbp": 99,
    "map": 115,
    "spo2": 100,
    "etco2": 37,
    "rr": 15
  }
]
Tuyệt đối không bọc trong markdown code block, chỉ trả về JSON hợp lệ."""

    candidate_models = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]
    if model not in candidate_models:
        candidate_models.insert(0, model)
    else:
        candidate_models.remove(model)
        candidate_models.insert(0, model)

    parts = [{"text": prompt}]
    for p in image_paths:
        try:
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": b64
                }
            })
        except Exception as e:
            print(f"Error reading image {p}: {e}")

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json"
        }
    }

    last_error = ""
    for current_model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json=payload, timeout=90)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    for k in data:
                        if isinstance(data[k], list):
                            data = data[k]
                            break
                    else:
                        data = [data]
                cleaned = []
                for r in data:
                    t = standardize_time(r.get("time"))
                    if t:
                        cleaned.append({
                            "time": t,
                            "hr": clean_val(r.get("hr")),
                            "sbp": clean_val(r.get("sbp")),
                            "dbp": clean_val(r.get("dbp")),
                            "map": clean_val(r.get("map")),
                            "spo2": clean_val(r.get("spo2")),
                            "etco2": clean_val(r.get("etco2")),
                            "rr": clean_val(r.get("rr"))
                        })
                return cleaned
            elif resp.status_code in [429, 503]:
                last_error = f"Model {current_model} bận ({resp.status_code})"
                print(f"{last_error}, chuyển sang model dự phòng...")
                time.sleep(1)
                continue
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text}"
                print(f"Gemini API error with {current_model}: {last_error}")
        except Exception as req_err:
            last_error = str(req_err)
            print(f"Request error with {current_model}: {req_err}")

    raise Exception(f"Lỗi gọi Gemini API sau khi thử các model: {last_error}")

@app.route('/api/ocr-chunk', methods=['POST'])
def ocr_chunk():
    cfg = load_config()
    api_key = cfg.get("gemini_api_key")
    if not api_key:
        return jsonify({"error": "Chưa cấu hình Gemini API Key! Vui lòng vào Cài đặt để nhập Key."}), 400

    model = get_effective_model(cfg)
    req_json = request.json or {}
    image_paths = req_json.get('image_paths', [])
    if not image_paths:
        return jsonify({"error": "Không có ảnh nào trong nhóm để quét!"}), 400

    valid_paths = [p for p in image_paths if os.path.exists(p)]
    try:
        records = process_ocr_chunk(valid_paths, api_key, model=model)
        return jsonify({"success": True, "records": records, "count": len(records)})
    except Exception as e:
        return jsonify({"error": str(e), "records": []}), 500

@app.route('/api/ocr-patient-batch', methods=['POST'])
def ocr_patient_batch():
    cfg = load_config()
    api_key = cfg.get("gemini_api_key")
    if not api_key:
        return jsonify({"error": "Chưa cấu hình Gemini API Key! Vui lòng vào Cài đặt để nhập Key."}), 400

    model = get_effective_model(cfg)
    req_json = request.json or {}
    image_paths = req_json.get('image_paths', [])
    if not image_paths:
        return jsonify({"error": "Không có ảnh nào để quét!"}), 400

    valid_paths = [p for p in image_paths if os.path.exists(p)]
    
    # Process in chunks of 4 images per batch (tránh payload quá lớn gây 503)
    chunk_size = 4
    chunks = [valid_paths[i:i + chunk_size] for i in range(0, len(valid_paths), chunk_size)]
    
    all_records = []
    last_error = ""

    for chunk in chunks:
        try:
            records = process_ocr_chunk(chunk, api_key, model=model)
            all_records.extend(records)
        except Exception as e:
            last_error = str(e)
            print(f"Error processing chunk: {e}")

    if not all_records and last_error:
        return jsonify({"error": f"Lỗi gọi Gemini API: {last_error}", "records": []}), 500

    # Deduplicate and merge by standardized time
    merged = {}
    for r in all_records:
        t = standardize_time(r.get("time"))
        if not t:
            continue
        r["time"] = t
        if t not in merged:
            merged[t] = dict(r)
        else:
            for k, v in r.items():
                if v is not None and (merged[t].get(k) is None or k in ["sbp", "dbp", "map"]):
                    merged[t][k] = v

    final_list = sorted(list(merged.values()), key=lambda x: x.get("time", ""))
    return jsonify({"success": True, "records": final_list, "count": len(final_list)})

@app.route('/api/normalize', methods=['POST'])
def api_normalize():
    data = request.json or {}
    raw_list = data.get('raw_data', [])
    t0_str = data.get('t0', '')
    tend_str = data.get('tend', '')
    impute_method = data.get('impute_method', 'forward-fill')
    step_minutes = int(data.get('step_minutes', 3))

    if not t0_str or not tend_str:
        return jsonify({"error": "Vui lòng chọn đầy đủ mốc T0 và T kết thúc!"}), 400

    try:
        normalized = normalize_vitals(raw_list, t0_str, tend_str, impute_method, step_minutes)
        return jsonify({"success": True, "normalized": normalized})
    except Exception as e:
        return jsonify({"error": f"Lỗi chuẩn hóa: {str(e)}"}), 500

@app.route('/api/generate-script', methods=['POST'])
def generate_script():
    data = request.json or {}
    vitals_data = data.get('vitals_data', [])
    patient_name = data.get('patient_name', 'BỆNH NHÂN')

    js_code = f"""// ========================================================
// SCRIPT AUTO-FILL THEO DÕI HUYẾT ĐỘNG CAN THIỆP LẤY HUYẾT KHỐI
// Bệnh nhân: {patient_name}
// Sinh tự động bởi Hệ thống Monitor OCR & Auto-fill
// Tác giả: BS. Nguyễn Trần Minh Chiến (nguyentranminhchien.hpmu@gmail.com)
// ========================================================
(function () {{
  console.log("🚀 Bắt đầu tự động nhập liệu dấu hiệu sinh tồn vào form...");

  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype,
    "value"
  ).set;
  const nativeSelectValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLSelectElement.prototype,
    "value"
  ).set;

  function setInputValue(input, val) {{
    if (!input || val === null || val === undefined) return;
    nativeInputValueSetter.call(input, val);
    input.dispatchEvent(new Event("input", {{ bubbles: true }}));
    input.dispatchEvent(new Event("change", {{ bubbles: true }}));
    input.dispatchEvent(new Event("blur", {{ bubbles: true }}));
  }}

  function setSelectValue(select, val) {{
    if (!select) return;
    const target = (val || "cuff").toLowerCase();
    let found = false;
    for (let i = 0; i < select.options.length; i++) {{
      const opt = select.options[i];
      const optVal = opt.value.toLowerCase();
      const optTxt = opt.text.toLowerCase();
      if (optVal === target || optTxt.includes(target) ||
         (target === "cuff" && (optTxt.includes("bao") || optTxt.includes("cuốn") || optVal.includes("cuff"))) ||
         (target === "arterial" && (optTxt.includes("động mạch") || optTxt.includes("xâm lấn") || optVal.includes("art")))) {{
        select.selectedIndex = i;
        found = true;
        break;
      }}
    }}
    if (!found && select.options.length > 1) {{
      select.selectedIndex = 1;
    }}
    nativeSelectValueSetter.call(select, select.value);
    select.dispatchEvent(new Event("input", {{ bubbles: true }}));
    select.dispatchEvent(new Event("change", {{ bubbles: true }}));
  }}

  function findByAttr(container, terms) {{
    for (const term of terms) {{
      const el = container.querySelector(
        `input[name*="${{term}}" i], input[id*="${{term}}" i], input[placeholder*="${{term}}" i], input[aria-label*="${{term}}" i]`
      );
      if (el && el.type !== "hidden") return el;
    }}
    return null;
  }}

  const vitalsData = {json.dumps(vitals_data, ensure_ascii=False, indent=2)};

  const rows = document.querySelectorAll("table tbody tr");
  console.log(`Tìm thấy ${{rows.length}} hàng trên bảng.`);

  if (rows.length < vitalsData.length) {{
    alert(
      `⚠️ Cảnh báo: Bảng trên web hiện có ${{rows.length}} hàng, trong khi dữ liệu có ${{vitalsData.length}} mốc.\\n` +
      `Hãy bấm nút "Thêm mốc theo dõi" (hoặc "Thêm dòng") trên web cho đủ ít nhất ${{vitalsData.length}} hàng rồi chạy lại script!`
    );
    return;
  }}

  let filledCount = 0;
  let imputedCount = 0;

  vitalsData.forEach((data, index) => {{
    const row = rows[index];
    if (!row) return;

    let minInput = null, sbpInput = null, dbpInput = null, mapInput = null, hrInput = null;

    // 1. Phân giải theo từng ô cột (td) - Chuẩn xác nhất, miễn nhiễm input hidden
    const cells = Array.from(row.querySelectorAll("td"));
    if (cells.length >= 5) {{
      const getInp = (cell) => cell ? (cell.querySelector('input:not([type="hidden"])') || cell.querySelector('input')) : null;
      minInput = getInp(cells[0]); // Cột 1: Mốc phút
      sbpInput = getInp(cells[1]); // Cột 2: SBP
      dbpInput = getInp(cells[2]); // Cột 3: DBP
      mapInput = getInp(cells[3]); // Cột 4: MAP
      hrInput  = getInp(cells[4]); // Cột 5: HR
    }} else {{
      // 2. Fallback: Lấy danh sách input hiển thị (bỏ qua input hidden)
      const vis = Array.from(row.querySelectorAll('input:not([type="hidden"])'));
      if (vis.length >= 5) {{
        [minInput, sbpInput, dbpInput, mapInput, hrInput] = vis;
      }} else if (vis.length === 4) {{
        [minInput, sbpInput, dbpInput, hrInput] = vis;
      }} else if (vis.length === 3) {{
        [sbpInput, dbpInput, hrInput] = vis;
      }}
    }}

    // 3. Ưu tiên khớp theo thuộc tính nếu form có đặt name/placeholder
    sbpInput = findByAttr(row, ["sbp", "tam_thu", "systolic"]) || sbpInput;
    dbpInput = findByAttr(row, ["dbp", "tam_truong", "diastolic"]) || dbpInput;
    mapInput = findByAttr(row, ["map", "trung_binh"]) || mapInput;
    hrInput  = findByAttr(row, ["hr", "pulse", "mach", "nhip_tim"]) || hrInput;
    minInput = findByAttr(row, ["minute", "phut", "moc"]) || minInput;

    // 4. Điền giá trị
    if (minInput) setInputValue(minInput, data.minute);
    if (sbpInput) setInputValue(sbpInput, data.sbp);
    if (dbpInput) setInputValue(dbpInput, data.dbp);
    // Nếu MAP không bị khóa readonly/disabled thì điền trực tiếp, nếu form tự tính thì event của SBP/DBP đã kích hoạt
    if (mapInput && !mapInput.readOnly && !mapInput.disabled) {{
      setInputValue(mapInput, data.map);
    }}
    if (hrInput) setInputValue(hrInput, data.hr);

    // 5. Chọn nguồn đo (Nguồn đo / Phương pháp đo)
    const select = (cells.length > 5 ? cells[5].querySelector("select") : null) || row.querySelector("select");
    if (select) {{
      setSelectValue(select, data.method || "cuff");
    }}

    filledCount++;
    if (data._imputed) {{
      imputedCount++;
      console.warn(`[Imputed] Mốc ${{data.minute}}p (${{data.time}}): Điền số liệu bù khuyết.`);
    }}
  }});

  console.log(`🎉 Nhập liệu hoàn tất: Đã điền ${{filledCount}}/${{vitalsData.length}} mốc.`);
  alert(
    `✅ Đã điền thành công ${{filledCount}}/${{vitalsData.length}} mốc theo dõi huyết động vào form!\\n` +
    `Bệnh nhân: {patient_name}`
  );
}})();"""

    return jsonify({"success": True, "script": js_code})

@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    data = request.json or {}
    vitals_data = data.get('vitals_data', [])
    patient_name = data.get('patient_name', 'Bệnh nhân')
    t0 = data.get('t0', '')
    tend = data.get('tend', '')

    if not vitals_data:
        return jsonify({"error": "Không có dữ liệu để xuất Excel"}), 400

    df_data = []
    for item in vitals_data:
        df_data.append({
            "Mốc (phút)": item.get("minute"),
            "Giờ thực tế": item.get("time"),
            "Nhịp tim HR (bpm)": item.get("hr"),
            "Huyết áp tâm thu SBP (mmHg)": item.get("sbp"),
            "Huyết áp tâm trương DBP (mmHg)": item.get("dbp"),
            "Huyết áp trung bình MAP (mmHg)": item.get("map"),
            "SpO2 (%)": item.get("spo2"),
            "etCO2 (mmHg)": item.get("etco2"),
            "Phương pháp đo": "Bao cuốn (Cuff)",
            "Trạng thái": "Bù khuyết thiếu (Imputed)" if item.get("_imputed") else "Đo thực tế"
        })

    df = pd.DataFrame(df_data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Huyết động EVT', index=False, startrow=3)
        ws = writer.sheets['Huyết động EVT']

        # Title headers
        ws['A1'] = f"BẢNG THEO DÕI HUYẾT ĐỘNG TRONG CAN THIỆP LẤY HUYẾT KHỐI (EVT)"
        ws['A2'] = f"Bệnh nhân: {patient_name} | Khoảng thời gian: {t0} - {tend} | Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        # Adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    output.seek(0)
    safe_name = re.sub(r'[^a-zA-Z0-9_\-\s]', '', patient_name).strip().replace(' ', '_')
    filename = f"HuyetDong_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
