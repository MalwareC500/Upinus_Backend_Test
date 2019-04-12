#!/usr/bin/python
# -*- coding: utf8 -*-
import json
from datetime import time, datetime, date
import operator
import os
import csv

import zipfile

import shutil
import json

class process:

    def __init__(self):
        pass

    def process_order(self, stock_file, priority_file, order_list_file, order_dir):

        def read_csv(fname):
            # print(fname)
            with open(fname) as f:
                res = [{k: str(v) for k, v in row.items()}
                for row in csv.DictReader(f, skipinitialspace=True)]
            # print(res)
            return res

        self.stock = read_csv(stock_file)
        self.priority = read_csv(priority_file)
        self.order_list = read_csv(order_list_file)
        self.suplier = []

        def get_agent_name(s):
            return str(s).split()[1]
        
        def get_pname_and_brand(p_id):
            for item in self.priority:
                if item["SKU"] == p_id:
                    b_list = []
                    for agent in self.suplier:
                        if item[agent] != "":
                            b_list.append({"name": agent, "priority": int(item[agent])})
                        else:
                            b_list.append({"name": agent, "priority": -1})
                    b_list = sorted(b_list, key = lambda i: i['priority'])
                    return item["Tên viết tắt"], b_list, 1
            
            return "", [], 0

        def get_supplier_name(product_id, number):
            product_name, brand_list, status = get_pname_and_brand(product_id)
            # check_error = 0
            check_exist = 0
            id = -1
            for i in range(0, len(self.stock)):
                item = self.stock[i]
                if item["SKU"] != product_id:
                    continue
                product = item
                id = i
            
            if id < 0:
                return '__error__', "iphone", 0  
            for brand in brand_list:
                if brand['priority'] == -1:
                    continue
                name = brand["name"]
                if int(product[name]) >= number:
                    product[name] = str(int(product[name]) - number)
                    self.stock[id] = product
                    return name, product_name, 1
            return '__error__', "iphone", 0

        def zipdir(path, ziph):
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                print(root)
                for file in files:
                    ziph.write(os.path.join(root, file), os.path.join(root[root.find("result"):], file))

            
        # create directory to save temporary result
        res_dir = os.path.join(order_dir, "result")
        os.mkdir(res_dir)
        agents = self.priority[0].keys()
        result = {}
        for agent in agents:
            if "Agent" not in str(agent):
                continue
            dname = get_agent_name(agent)
            self.suplier.append(agent)
            result[agent] = {}
            brand_dname = os.path.join(res_dir, dname)
            try:
                os.mkdir(brand_dname)
            except:
                pass
        print(self.suplier)
        error_file = open(os.path.join(res_dir, "error_order.csv"), mode = "w", encoding = "utf8")
        error_writer = csv.writer(error_file)
        for order in self.order_list:
            order_id = order["Order ID"]
            # print(order_id)
            order_name = order["Order Name"]
            order_quantity = order["Quantity"]
            order_item_id = order["Lineitem SKU"]
            d = date.today()
            order_day = '{:02d}'.format(d.day)
            order_month = '{:02d}'.format(d.month)
            now = datetime.now()
            now_time = now.time()
            if now_time <= time(12,00):
                order_session = "a"
            else:
                order_session = "b"
            order_supplier_name, order_item_name, status = get_supplier_name(order_item_id, int(order_quantity))
            # print(order_supplier_name)
            if status == 1:
                if order_item_name in result[order_supplier_name].keys():
                    try:
                        result[order_supplier_name][order_item_name]["number"] += int(order_quantity)
                        result[order_supplier_name][order_item_name]["date"]  = '.'.join([order_day, order_month])
                        result[order_supplier_name][order_item_name]["orders"].append([order_id, order_name, order_quantity, ' '.join(["P", order_session, '/'.join([order_day, order_month]), order_supplier_name])])
                    except:
                        pass
                else:
                    try:
                        result[order_supplier_name][order_item_name] = {}
                        result[order_supplier_name][order_item_name]["number"] = int(order_quantity)
                        result[order_supplier_name][order_item_name]["date"]  = '.'.join([order_day, order_month])
                        result[order_supplier_name][order_item_name]["orders"] = []
                        result[order_supplier_name][order_item_name]["orders"].append([order_id, order_name, order_quantity, ' '.join(["P", order_session, '/'.join([order_day, order_month]), order_supplier_name])])

                    except:
                        result[order_supplier_name][order_item_name] = {}
                        result[order_supplier_name][order_item_name]["number"] = 0
                        result[order_supplier_name][order_item_name]["orders"] = []
                        result[order_supplier_name][order_item_name]["date"]  = '.'
            else:
                row = []
                for key, value in order.items():
                    row.append(value)
                error_writer.writerows([row])
        for brand, order in result.items():
            print(brand)
            for pname, detail in order.items():
                brand_dir = os.path.join(res_dir, get_agent_name(brand))
                fname = os.path.join(brand_dir, '_'.join([pname, str(detail['number']) + 'pcs', detail["date"], brand]) + ".csv")
                csv_writer = csv.writer(open(fname, mode = "w", encoding = "utf8"))
                csv_writer.writerows([["Order ID","Order Name","Quatity","Status"]])
                csv_writer.writerows(detail['orders'])
        res_fname = "result" + str(datetime.now()) + ".zip"
        res_file = "http://localhost:4041/static/" + res_fname
        zipf = zipfile.ZipFile('result.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(res_dir, zipf)
        shutil.move("result.zip", os.path.join("static/", res_fname))
        return json.dumps({"download_link": res_file})
