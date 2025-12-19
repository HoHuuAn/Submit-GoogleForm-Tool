import random
import requests
from faker import Faker

# Assuming the URL for the form in result.json; replace if different
# Replace with actual form URL
URL = "https://docs.google.com/forms/d/e/1FAIpQLSf6HWgzme6oukUgylq5Hh4Ljd6fZQFdm6WVD4DuNoEWN7b9lQ/formResponse"

fake = Faker(locale='vi_VN')  # For Vietnamese names

# Form fields based on result.json
form_fields = {
    "entry.1387744577": ['Có (Mời Anh/Chị tiếp tục khảo sát)', 'Không (Mời Anh/Chị có thể dừng khảo sát tại đây)'],
    "entry.1982015768": "name",  # Will be set to fake name
    "entry.909430394": ['Nam', 'Nữ', 'Khác'],
    "entry.232998764": ['Dưới 18', '18 - 30', '30 - 45', 'Trên 45'],
    "entry.199590829": ['Học sinh/Sinh Viên', 'Nhân viên văn phòng', 'Nội trợ', 'ANY TEXT!!'],
    "entry.1277523354": ['Dưới 5.000.000 VNĐ/', '5.000.000 - 10.000.000 VNĐ/tháng', '10.000.000 - 15.000.000 VNĐ/tháng', 'Trên 15.000.000 VNĐ/tháng'],
    "entry.253045659": ['Miền Bắc', 'Miền Trung', 'Miền Nam'],
    "entry.1447088759": ['Thường xuyên (≥3 lần/tuần)', 'Thỉnh thoảng (1–2 lần/tuần)', 'Hiếm khi', 'Không bao giờ'],
    "entry.1302435919": ['Bữa sáng', 'Bữa trưa', 'Bữa tối', 'Ăn vặt'],
    "entry.522591443": ['Tự làm', 'Siêu thị/ Cửa hàng tiện lợi', 'Nhà hàng/ Quán ăn', 'ANY TEXT!!'],
    "entry.421539902": ['Thường xuyên thay đổi để thử hương vị mới', 'Thỉnh thoảng đổi', 'Gần như chỉ dùng một loại cố định'],
    "entry.32803414": ['Hàng tuần', '2–3 tuần/lần', 'Hàng tháng', 'Hiếm khi'],
    "entry.1828067096": ['Siêu thị/Cửa hàng tiện lợi', 'Chợ truyền thống', 'Sàn thương mại điện tử (Shopee, Lazada,....)', 'ANY TEXT!!'],
    # Checkbox, max 3
    "entry.1382807682": ['Hương vị', 'Thành phần tự nhiên', 'Thương hiệu uy tín', 'Bao bì đẹp mắt', 'Giá cả hợp lý', 'Phổ biến', 'Ít béo/tốt cho sức khỏe'],
    "entry.1646014574": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.1802054787": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.533999246": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.1565291616": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.2001980187": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.1975868997": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.685556570": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.264873993": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.67776201": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.1770637100": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.524372760": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.1047007171": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.1818164049": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.649916967": ['Không quan tâm', 'Ít quan tâm', 'Quan tâm', 'Hơi quan tâm', 'Rất quan tâm'],
    "entry.1889743316": ['Chai nhựa', 'Chai thủy tinh', 'Túi nhỏ'],
    "entry.229032267": ['Dưới 35.000 VNĐ', '35.000 - 50.000 VNĐ', 'Trên 50.000 VNĐ'],
    "entry.1661558202": ['Bạn bè/người thân giới thiệu', 'Mạng xã hội (Facebook, TikTok,...)', 'Siêu thị/Cửa hàng tiện lợi', 'Trang web của công ty', 'Các sàn thương mại điện tử (Shopee, Lazada,...)'],
    "entry.840854392": ['Rất sẵn sàng', 'Có thể thử', 'Còn phân vân', 'Không hứng thú'],
    "entry.473134838": "text",  # Any text, will generate fake sentence
    "pageHistory": "0,1,2,3"
}


def fill_form(name):
    value = {}
    for key, options in form_fields.items():
        if key == "entry.1982015768":
            value[key] = name
        elif key == "entry.473134838":
            value[key] = fake.sentence()  # Generate fake comment
        elif key == "pageHistory":
            value[key] = options
        elif key == "entry.1387744577":  # Always choose 'Có'
            value[key] = options[0]
        elif isinstance(options, list):
            if key == "entry.1382807682":  # Checkbox, max 3
                num_choices = random.randint(1, 3)
                value[key] = random.sample(options, num_choices)
            else:
                # Avoid "ANY TEXT!!" if present
                filtered_options = [
                    opt for opt in options if opt != 'ANY TEXT!!']
                if filtered_options:
                    value[key] = random.choice(filtered_options)
                else:
                    value[key] = ""  # Or handle differently
        else:
            value[key] = ""
    return value


def submit(url, data):
    ''' Submit form to url with data '''
    try:
        res = requests.post(url, data=data, timeout=5)
        if res.status_code != 200:
            raise Exception("Error! Can't submit form", res.status_code)
        return True
    except Exception as e:
        print("Error!", e)
        return False


# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Running script to submit 1000 times...", flush=True)
    for i in range(10):
        print(fake.safe_email())
        name = fake.name()
        data = fill_form(name)
        success = submit(URL, data)
        if success:
            print(f"Submission {i+1} successful")
        else:
            print(f"Submission {i+1} failed")
        import time
        time.sleep(1)
