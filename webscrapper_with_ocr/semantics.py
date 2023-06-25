import re
import os
from glob import glob
import pandas as pd
import yaml
import csv
from typing import List
from utils import image_downloader
from ocr import BEEStarLabelOCR
from tqdm import tqdm
import ast

from const import patterns_amazon, patterns_flipkart, patterns_croma, columns_based_on_prod

# patterns = {
#     'model_name' : r'[0-9\-]{4}\s[M|m]odel\,?\s?([A-Za-z0-9\-]+)\,?',
#     'star_rating' : r'([0-5]{1})\s?(?:S|s)tar',
#     'model_name_wh' : r'(.+)\s[0-9-]{1,2}\s?\-?(?:[L|l]itre|L|l)',
# }

# patterns_prod_info_bullet = {
#     'star_rating' : r'([0-5]{1})\s?(?:S|s)tar',
#     'star_rating_ceil_fan' : r'([0-5]{1}\.[0-9])\s?\n?[0-9,]+\s?[R|r]atings',
#     'ee_value_ac_vs' : r'ISEER\s?(?:V|v)alue\s?\:\s?([0-5]{1}\.[0-9]+)',
#     'ee_value_ref_ff' : r'[A|a]nnual\s?[E|e]nergy\s[C|c]onsumption\s?([0-9]+)',
# }

# patterns_prod_info_table = {
#     'star_rating' : r'([0-5]{1}\.?(?:[0-9]+)?)\sout\sof\s[0-5]{1}\s?(?:S|s)tar[s]?',
#     'model_name' : r'(?:M|m)odel\s?([a-zA-Z0-9\-\s\/]+)\s*?\n(?:[C|c]apacity|[W|w]eighted|[E|e]nergy)',
#     'model_name_color_tv' : r'[M|m]odel\s?([a-zA-Z0-9\s\-\/\\]+)\n?[M|m]odel\s?[N|n]ame',
#     'model_name_color_tv2' : r'[M|m]odel\s?([a-zA-Z0-9\s\-\/\\]+)\n?[M|m]odel\s?',
#     'ee_value_ac_vs' : r'ISEER\s?(?:V|v)alue\s?\:\s?([0-5]{1}\.[0-9]+)',    # this maybe change if find any sample data
#     'ee_value_ref_ff' : r'[A|a]nnual\s?[E|e]nergy\s[C|c]onsumption\s?([0-9]+)',
#     'brand_name_tfl' : r'[B|b]rand\s?([a-zA-z]+)',
# }


class InfoScrapper:

    def __init__(self, dummy_excel_path : str, site : str, product_category : str, out_file_name : str) -> None:
        self.dummy_excel = pd.ExcelFile(dummy_excel_path)
        self.site = site                              # amazon, flipkart, reliance, croma
        self.product_category = product_category      # AC_variable_speed, AC_fixed_speed, Refrigerator_Frost_Free, Refrigerator_Direct_Cool
        self.out_file_name = out_file_name
        self.report = []

    def save_report(self, final_data : List, report_file_name : str):
        with open(report_file_name + '.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(final_data)

        print("report generated!")

    def search_pattern(self, patterns : List, text : List):
        for t in text:
            for pattern in patterns:
                match = re.search(pattern, str(t))
                if match:
                    try:
                        return (True, match.group(1))
                    except:
                        return (True, 'NA')
        else:
            return (False, None)
        
    def get_general_report(self, appliance : str, website_type : str, row_cnt : int, data : pd.DataFrame):
        brand = data['Title'][row_cnt].split(' ')[0]
        return [row_cnt, self.site, website_type, appliance, brand]
    
        
    def fetch_info(self, raw_data_path : str):
        #-----------------------------------------------
        patterns = patterns_croma.copy()
        #-----------------------------------------------
        base_path = f'reports_new2/{self.product_category}/'
        if not os.path.exists(base_path):
            os.makedirs(f'{base_path}')
        
        os.makedirs(f'{base_path}{self.site}/images/')

        raw_data = pd.read_csv(raw_data_path)
        fields = pd.read_excel(self.dummy_excel, f'{columns_based_on_prod[self.product_category][0]}').columns.tolist()
        fields = fields[:-4]
        self.report.append(fields)

        for idx in tqdm(range(raw_data.shape[0]), desc = f'fetching {self.site} {self.product_category} info...'):
            # # saving images
            try:
                image_links = ast.literal_eval(raw_data['image link'][idx])
            except:
                print("issue in ast literal_eval")
                image_links = []
            os.mkdir(f'{base_path}/{self.site}/images/{idx}/')
            image_downloader(urls = image_links, target_path = f'{base_path}/{self.site}/images/{idx}/')

            temp_report = []
            general_report = self.get_general_report(f'{self.product_category}', 'E- commerce website', idx, raw_data)

            temp_report.extend(general_report)

            #---------------------------- TITLE AND MAIN HEADING -------------------------------------

            if self.product_category == 'Ceiling_fan' or self.product_category == 'Colour_TV':
                match_flag, out = self.search_pattern(patterns = patterns['model_number'], text = [raw_data['table'][idx]])
                if match_flag:
                     model_number = out
                else:
                    model_number = ""
            elif self.product_category == 'Refrigerator_frost_free' or self.product_category == 'Refrigerator_direct_cool':
                try:
                    match_flag, out = self.search_pattern(patterns = patterns['model_number'], text = [raw_data['table'][idx]])
                    if match_flag:
                        model_number = out
                    else:
                        model_number = raw_data['Title'][idx].split('(')[1].split(',')[0]
                except:
                    model_number = ''

            elif self.product_category == 'AC_variable_speed' or self.product_category == 'AC_fixed_speed':
                try:
                    match_flag, out = self.search_pattern(patterns = patterns['model_number'], text = [raw_data['table'][idx]])
                    if match_flag:
                        model_number = out
                    else:
                        model_number = raw_data['Title'][idx].split('(')[1].split(',')[-1]
                except:
                    model_number = ''
                    
            elif self.product_category == 'tabular_florescent_lamps':
                match_flag, out = self.search_pattern(patterns = patterns['model_number'], text = [raw_data['table'][idx], raw_data['Title'][idx]])
                if match_flag:
                     model_number = out
                else:
                    model_number = ""
            else:
                match_flag, out = self.search_pattern(patterns = patterns['model_number'], text = [raw_data['table'][idx], raw_data['bullet points'][idx], raw_data['Title'][idx]])

                if match_flag:
                    model_number = out
                    if len(model_number) > 20:
                        model_number = model_number.split(' ')[0]
                else:
                    model_number = ""

            web_link_of_product_page = raw_data['Link'][idx]

            match_flag, out = self.search_pattern(patterns = patterns['star_rating'], text = [raw_data['Title'][idx]])
            if match_flag:
                is_star_rating_mentioned = 'Yes'
                star_rating_mentioned = out
            else:
                is_star_rating_mentioned = 'No'
                star_rating_mentioned = 'NA'

            if self.site == 'amazon':
                website_contain_prod_info = 'No'       # DEFAULT for amazon
            else:
                website_contain_prod_info = 'Yes' if raw_data['prodDescp'][idx] != None else 'No'

            temp_report.extend([model_number, web_link_of_product_page])            
                
            temp_ocr_report = ['NA' for _ in range(columns_based_on_prod[self.product_category][1])]    # for OCR part
            temp_report.extend(temp_ocr_report)
            temp_report.extend([is_star_rating_mentioned, star_rating_mentioned, website_contain_prod_info])

            #------------------------- PRODUCT INFO BULLET POINTS --------------------------------

            match_flag, out = self.search_pattern(patterns = patterns['star_rating'], text = [raw_data['bullet points'][idx]])
            if match_flag:
                is_star_rating_in_info_bullet = 'Yes'
                star_rating_in_info_bullet = out
            else:
                is_star_rating_in_info_bullet = 'No'
                star_rating_in_info_bullet = 'NA'

            #----------------------------------------------------------------------------------------------------------------
            #----------------------------------------------------------------------------------------------------------------

            # match_flag, out = self.search_pattern(patterns = patterns['ee_value']['AC'], text = [raw_data['bullet points'][idx]])
            match_flag, out = self.search_pattern(patterns = patterns['ee_value']['REF'], text = [raw_data['bullet points'][idx]])
            
            #----------------------------------------------------------------------------------------------------------------
            #----------------------------------------------------------------------------------------------------------------
            
            if match_flag:
                is_ee_param_mentioned_in_info_bullet = 'Yes'
                ee_param_value_in_info_bullet = out
            else:
                is_ee_param_mentioned_in_info_bullet = 'No'
                ee_param_value_in_info_bullet = 'NA'

            temp_report.extend([is_star_rating_in_info_bullet, star_rating_in_info_bullet, 
                                is_ee_param_mentioned_in_info_bullet, ee_param_value_in_info_bullet])


            #------------------------- PRODUCT DESCRIPTION -----------------------------

            # for amazon - from the manifacturer
            if self.site == 'amazon':
                temp_prod_desc_report = ['NA' for _ in range(4)]
                temp_report.extend(temp_prod_desc_report)
            else:
                match_flag, out = self.search_pattern(patterns = patterns['star_rating'], text = [raw_data['prodDescp'][idx]])
                if match_flag:
                    is_star_rating_in_info_prod_desc = 'Yes'
                    star_rating_in_info_prod_desc = out
                else:
                    is_star_rating_in_info_prod_desc = 'No'
                    star_rating_in_info_prod_desc = 'NA'

                #----------------------------------------------------------------------------------------------------------------
                #----------------------------------------------------------------------------------------------------------------
                # match_flag, out = self.search_pattern(patterns = patterns['ee_value']['AC'], text = [raw_data['prodDescp'][idx]])
                match_flag, out = self.search_pattern(patterns = patterns['ee_value']['REF'], text = [raw_data['prodDescp'][idx]])

                #---------------------------------------------------------------------------------------------------------------
                #---------------------------------------------------------------------------------------------------------------

                if match_flag:
                    is_ee_param_mentioned_in_prod_desc = 'Yes'
                    ee_param_value_in_prod_desc = out
                else:
                    is_ee_param_mentioned_in_prod_desc = 'No'
                    ee_param_value_in_prod_desc = 'NA'

                temp_report.extend([is_star_rating_in_info_prod_desc, star_rating_in_info_prod_desc, 
                                    is_ee_param_mentioned_in_prod_desc, ee_param_value_in_prod_desc])

            #------------------------- PRODUCT INFO TABLE ----------------------------- 

            match_flag, out = self.search_pattern(patterns = patterns['star_rating'], text = [raw_data['table'][idx]])
            if match_flag:
                is_star_rating_in_info_table = 'Yes'
                star_rating_in_info_table = out
            else:
                is_star_rating_in_info_table = 'No'
                star_rating_in_info_table = 'NA'

            #----------------------------------------------------------------------------------------------------------------
            #----------------------------------------------------------------------------------------------------------------

            # match_flag, out = self.search_pattern(patterns = patterns['ee_value']['AC'], text = [raw_data['table'][idx]])
            match_flag, out = self.search_pattern(patterns = patterns['ee_value']['REF'], text = [raw_data['table'][idx]])
            
            #----------------------------------------------------------------------------------------------------------------
            #----------------------------------------------------------------------------------------------------------------

            if match_flag:
                is_ee_param_mentioned_in_info_table = 'Yes'
                ee_param_value_in_info_table = out
            else:
                is_ee_param_mentioned_in_info_table = 'No'
                ee_param_value_in_info_table = 'NA'

            temp_report.extend([is_star_rating_in_info_table, star_rating_in_info_table, 
                                is_ee_param_mentioned_in_info_table, ee_param_value_in_info_table]) 

            self.report.append(temp_report)

        self.save_report(final_data = self.report, report_file_name = f'{base_path}/{self.site}/{self.out_file_name}')
        # self.save_report(final_data = self.report, report_file_name = 'test_reports/water_heater2')




if __name__ == "__main__":


    fetch_info = InfoScrapper(dummy_excel_path = 'assesment_sheet_compilance.xlsx', site = 'croma', 
                              product_category = 'tabular_florescent_lamps', out_file_name = 'tfl_report')

    fetch_info.fetch_info('market xl/croma/finalTFL.csv')