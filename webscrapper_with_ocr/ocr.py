from easyocr import Reader
import cv2
import re
from typing import List
from pprint import pprint


class BEEStarLabelOCR:

    def __init__(self):
        self.a = None
        self.reader = Reader(['en'], gpu = False, quantize = False)
        # self.reader = Reader(['en'], gpu = True)   # run using gpu

    def is_target_image(self, extracted_ocr_info):
        pattern = r'power\s?savings'
        for info in extracted_ocr_info:
            match = re.search(pattern, info[1].lower())
            if match:
                return True
        else:
            return False
        
    def image_to_star_label_area_ratio(self, img_path : str, w, h):
        img_shape = cv2.imread(img_path).shape
        W, H = img_shape[0], img_shape[1]
        total_area = int(W * H)
        star_label_area = int(w * h)
        ratio = (star_label_area / total_area) * 100
        return round(ratio, 2), img_shape
        
    def is_image_readable(self, img_path, width):
        im = cv2.imread(img_path)
        im_size = im.shape
        
        area_occupancy = (width / im_size[1]) * 100
        return area_occupancy

    def fetch_image_info_AC(self, extracted_ocr_info : List):
        patterns = {
            'iseer' : r"iseer",
            'label_period' : r'lab(?:e|c)l\s?p(?:e|c)riod',
            'appliance_type' : r'appliance',
            'model_year' : r'mod(?:e|c)l',
            'cooling_100' : r'cooling\s?capacity\s?\((?:1|4|7|i)(?:0|q|o|c)(?:0|q|0|o|c|)\%?\)',
            'cooling_50' : r'cooling\s?capacity\s?\(5(?:0|o|q|)\%\)',
            'electricity_consumption' : r'electricity consumption',
            'compressor' : r'compressor',
            'heat_pump' : r'(?:h(?:e|c)at\s?pump|heat\s?[a-z]{3,4}|[a-z]{3,4}\s?pump)',
        }

        label_period_pattern = r'([a-z0-9]{3,4}\s?(?:jan|feb|mar|apr|may|june|july|aug|sep|oct|nov|dec)\s?\,?\s?\;?[0-9]{4})'

        out = {
            'iseer' : None,
            'label_period' : None,
            'appliance_type' : None,
            'model_year' : None,
            'cooling_100' : None,
            'cooling_50' : None,
            'electricity_consumption' : None,
            'compressor' : None,
            'heat_pump' : 'No',
        }

        for k, p in patterns.items():
            for idx, info in enumerate(extracted_ocr_info):
                match = re.search(p, info.lower())
                if match and k == 'label_period':
                    label_period = re.findall(label_period_pattern, info.lower())
                    if label_period:
                        if len(label_period) > 1:
                            # print(f"{k} -- {label_period[0]} to {label_period[1]}")
                            out['label_period'] = f"{label_period[0]} to {label_period[1]}"
                        elif len(label_period) == 1:
                            # print(f"{k} -- {label_period[0]} to {extracted_ocr_info[idx + 1]}")
                            out['label_period'] = f"{label_period[0]} to {extracted_ocr_info[idx + 1]}"
                    else:
                        out['label_period'] = f"{extracted_ocr_info[idx + 1]} to {extracted_ocr_info[idx + 2]}"
                elif match:
                    # print(f"{k}  -- {extracted_ocr_info[idx + 1]}")
                    try:
                        out[f"{k}"] = f'{extracted_ocr_info[idx + 1]}'
                    except:
                        pass
        if (len(out['heat_pump']) > 3) or (len(out['heat_pump']) == 0):
            out['heat_pump'] = 'No'
        
        return out
    
    def fetch_image_info_REF(self, extracted_ocr_info : List):
        patterns = {
            'electricity_consumption' : r"annual\s?energy\s?consumption",
            'label_period' : r'lab(?:e|c)l\s?p(?:e|c)riod',
            'appliance_type' : r'appliance',
            'brand' : r'brand',
            'model_year' : r'mod(?:e|c)l',
            'type' : r'typ(?:e|c)',
            'total_volume': r'total\s?volum(?:e|c)',
        }

        label_period_pattern = r'([a-z0-9]{3,4}\s?(?:jan|feb|mar|apr|may|june|july|aug|sep|oct|nov|dec)\s?\,?\s?\;?[0-9]{4})'

        out = {
            'electricity_consumption' : None,
            'label_period' : None,
            'appliance_type' : None,
            'brand' : None,
            'model_year' : None,
            'type' : None,
            'total_volume': None,
        }

        for k, p in patterns.items():
            for idx, info in enumerate(extracted_ocr_info):
                match = re.search(p, info.lower())
                if match and k == 'label_period':
                    label_period = re.findall(label_period_pattern, info.lower())
                    if label_period:
                        if len(label_period) > 1:
                            # print(f"{k} -- {label_period[0]} to {label_period[1]}")
                            out['label_period'] = f"{label_period[0]} to {label_period[1]}"
                        elif len(label_period) == 1:
                            # print(f"{k} -- {label_period[0]} to {extracted_ocr_info[idx + 1]}")
                            out['label_period'] = f"{label_period[0]} to {extracted_ocr_info[idx + 1]}"
                    else:
                        out['label_period'] = f"{extracted_ocr_info[idx + 1]} to {extracted_ocr_info[idx + 2]}"
                elif match:
                    # print(f"{k}  -- {extracted_ocr_info[idx + 1]}")
                    try:
                        out[f"{k}"] = f'{extracted_ocr_info[idx + 1]}'
                    except:
                        pass
        return out


    def run_ocr(self, img_path : str, prod_type : str):

        w , h = None, None

        checkers = {
            "AC" : ["power savings", "heat pump"],
            "REF" : ["power savings", "total volume"]
        }
        fetched_text = []
        
        fetched_info = self.reader.readtext(img_path)
        flag = self.is_target_image(fetched_info)
        if not flag:
            return None, None
        # print(fetched_info)
        # x_min, x_max = None, None
        coords = []
        FLAG = 0
        for r in fetched_info:
            if r[1].lower() == checkers[prod_type][0]:
                bboxes = r[0]
                x_min, x_max = bboxes[0][0], bboxes[1][0]
                h = bboxes[0][1]
                w = x_max - x_min
                occupied_bee_label_area = self.is_image_readable(img_path, w)
                coords.append((x_min, x_max, occupied_bee_label_area))

        if not coords:
            return None, None

        target_area = sorted(coords, key = lambda x: x[2], reverse = True)[0]
        x_min, x_max = target_area[0], target_area[1]
        w = x_max - x_min

        for r in fetched_info:
            pointer = r[0][0][0]

            if (pointer > x_min) and (pointer < x_max):
                if FLAG > 0:
                    if FLAG != 2:
                        FLAG += 1
                    else:
                        break
                if r[1].lower() == checkers[prod_type][1]:
                    FLAG += 1
                # print(f"{r[1]} -- {r[0]}\n")
                y_max = r[0][0][1]
                fetched_text.append(r[1])
        h = y_max - h

        # print(self.image_to_star_label_area_ratio(img_path, w, h))
            
        
        # print(fetched_text)
        # print(img_path)
        # print(occupied_bee_label_area)
        if prod_type == 'AC':
            res = self.fetch_image_info_AC(fetched_text)
        else:
            res = self.fetch_image_info_REF(fetched_text)
        return res, occupied_bee_label_area

# if __name__ == "__main__":

#     ocr = BEEStarLabelOCR()
#     # print(ocr.run_ocr('reports/AC_fixed_speed/amazon//images/56/2.png', "AC"))
#     print(ocr.run_ocr('reports_new2/AC_fixed_speed/amazon/images/6/1.png', "AC"))