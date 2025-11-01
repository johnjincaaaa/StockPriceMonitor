import time
import threading
import requests
import re
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import logging
from collections import defaultdict
import os
import ran

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stock_monitor.log",encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 随机User-Agent池，避免反爬虫
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/113.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/113.0.1774.57"
]

# 主力流入数据接口
def fund_flow(stock_code):
    """获取主力净流入数据（万元）"""
    try:
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": f"https://data.eastmoney.com/zjlx/{stock_code[2:]}.html",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": random.choice(USER_AGENTS),
            "sec-ch-ua": "\"Google Chrome\";v=\"114\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"114\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }

        area = {'sh': '1', 'sz': '0'}
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            "cb": f"jQuery11230{random.randint(1000000000000, 9999999999999)}_{int(time.time() * 1000)}",
            "fltt": "2",
            "secids": f"{area[stock_code[:2]]}.{stock_code[2:]}",
            "fields": "f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f64,f65,f70,f71,f76,f77,f82,f83,f164,f166,f168,f170,f172,f252,f253,f254,f255,f256,f124,f6,f278,f279,f280,f281,f282",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
            "_": int(time.time() * 1000)
        }

        # 最多重试3次
        for _ in range(3):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=10
                )
                if response.status_code == 200:
                    break
                time.sleep(1)
            except Exception as e:
                logging.warning(f"主力净流入请求失败，重试中: {str(e)}")
                time.sleep(1)
        else:
            logging.error(f"获取 {stock_code} 主力净流入失败，多次重试无效")
            return "0.00"

        # 解析数据
        data_match = re.findall(r'\(.*?\)', response.text)
        if not data_match:
            return "0.00"

        data = json.loads(data_match[0].strip('()'))
        if data.get('data', {}).get('diff'):
            net_inflow = data['data']['diff'][0].get('f62', 0)
            return float(net_inflow) / 10000  # 转换为万元
        return 0.00

    except Exception as e:
        logging.error(f"主力净流入解析错误: {str(e)}")
        return 0.00

# 数据接口
def get_data(stock_code):
    """获取股票基本数据（价格、涨跌幅等）"""
    try:
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": f"https://quote.eastmoney.com/{stock_code}.html",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": random.choice(USER_AGENTS),
            "sec-ch-ua": "\"Google Chrome\";v=\"114\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"114\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }

        area = {'sh': '1', 'sz': '0'}
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "cb": f"jQuery3510{random.randint(1000000000000, 9999999999999)}_{int(time.time() * 1000)}",
            "secid": f"{area[stock_code[:2]]}.{stock_code[2:]}",
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "1",
            "beg": "0",
            "end": "20500101",
            "smplmt": "460",
            "lmt": "1000000",
            "_": int(time.time() * 1000)
        }

        # 最多重试3次
        for _ in range(3):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=10
                )
                if response.status_code == 200:
                    break
                time.sleep(1)
            except Exception as e:
                logging.warning(f"股票数据请求失败，重试中: {str(e)}")
                time.sleep(1)
        else:
            logging.error(f"获取 {stock_code} 股票数据失败，多次重试无效")
            return None

        # 解析数据
        data_match = re.findall(r'\(.*?\)', response.text)
        if not data_match:
            return None

        data = json.loads(data_match[0].strip('()'))
        if not data.get('data'):
            return None

        # 提取最新数据
        klines = data['data'].get('klines', [])
        if not klines:
            return None

        latest_data = klines[-1].split(',')
        if len(latest_data) < 10:
            return None

        return {
            'stock_name': data['data'].get('name', '未知'),
            'new_price': latest_data[2],  # 最新价
            'price_limit': latest_data[8],  # 涨跌幅(%)
        }

    except Exception as e:
        logging.error(f"股票数据解析错误: {str(e)}")
        return None


class StockMonitor:
    def __init__(self):
        self.stocks = {}  # 存储股票信息 {code: {name, price, net_inflow, ...}}
        self.monitoring_threads = {}  # 监控线程
        self.alert_settings = defaultdict(dict)  # 提醒设置 {code: {indicator: (threshold, direction)}}
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.stop_event.set()  # 初始状态为停止

        # 初始化UI
        self.init_ui()

        # 加载股票列表（优先加载保存的，无则加载默认）
        if not self.load_stocks():
            self.load_default_stocks()

        # 加载提醒设置
        self.load_alert_settings()

    def init_ui(self):
        """初始化用户界面"""
        self.root = tk.Tk()
        self.root.title("实时股票监控系统")
        self.root.geometry("1200x700")

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 股票列表区域
        stock_frame = ttk.LabelFrame(main_frame, text="股票监控列表", padding="10")
        stock_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 创建表格
        columns = ("代码", "名称", "最新价", "涨跌幅(%)", "主力净流入(万)", "更新时间")
        self.tree = ttk.Treeview(stock_frame, columns=columns, show="headings")

        # 设置列宽和标题
        for col in columns:
            self.tree.heading(col, text=col)
            width = 150 if col != "名称" else 100
            self.tree.column(col, width=width, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(stock_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 操作按钮区域
        btn_frame = ttk.Frame(main_frame, padding="10")
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="添加股票", command=self.add_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="移除股票", command=self.remove_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="设置提醒", command=self.set_alert).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="开始监控", command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="停止监控", command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)

        # 状态区域
        self.status_var = tk.StringVar(value="监控未启动")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 提醒日志区域
        alert_frame = ttk.LabelFrame(main_frame, text="提醒日志", padding="10")
        alert_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.alert_text = tk.Text(alert_frame, height=10, wrap=tk.WORD)
        self.alert_text.pack(fill=tk.BOTH, expand=True)
        self.alert_text.config(state=tk.DISABLED)

        # 窗口关闭事件绑定
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_default_stocks(self):
        """加载默认股票列表"""
        default_stocks = [
            {"code": "sz301171", "name": "华研精机"},
            {"code": "sh600036", "name": "招商银行"},
            {"code": "sz000858", "name": "五粮液"},
            {"code": "sh600519", "name": "贵州茅台"}
        ]

        for stock in default_stocks:
            self.stocks[stock["code"]] = {
                "name": stock["name"],
                "price": "0.00",
                "change_percent": "0.00",
                "net_inflow": "0.00",
                "update_time": ""
            }
            self.tree.insert("", tk.END, iid=stock["code"], values=(
                stock["code"], stock["name"], "0.00", "0.00", "0.00", ""
            ))

    def save_stocks(self):
        """保存股票列表到文件"""
        try:
            with open("stocks.json", "w", encoding="utf-8") as f:
                json.dump(self.stocks, f, ensure_ascii=False, indent=2)
            logging.info("股票列表保存成功")
        except Exception as e:
            logging.error(f"保存股票列表失败: {str(e)}")

    def load_stocks(self):
        """从文件加载股票列表"""
        try:
            if os.path.exists("stocks.json"):
                with open("stocks.json", "r", encoding="utf-8") as f:
                    self.stocks = json.load(f)

                # 加载到UI
                for code, info in self.stocks.items():
                    self.tree.insert("", tk.END, iid=code, values=(
                        code,
                        info["name"],
                        info["price"],
                        info["change_percent"],
                        info["net_inflow"],
                        info["update_time"]
                    ))
                logging.info("股票列表加载成功")
                return True
            return False
        except Exception as e:
            logging.error(f"加载股票列表失败: {str(e)}")
            return False

    def add_stock(self):
        """添加股票"""
        code = simpledialog.askstring("添加股票", "请输入股票代码(如sz301171):")
        if not code:
            return

        # 验证股票代码格式
        if not (code.startswith(('sh', 'sz')) and len(code) == 8):
            messagebox.showerror("错误", "股票代码格式错误，应为sh或sz开头加6位数字")
            return

        if code in self.stocks:
            messagebox.showinfo("提示", f"股票 {code} 已在监控列表中")
            return

        # 尝试获取股票名称
        name = self.get_stock_name(code) or "未知"

        self.stocks[code] = {
            "name": name,
            "price": "0.00",
            "change_percent": "0.00",
            "net_inflow": "0.00",
            "update_time": ""
        }

        self.tree.insert("", tk.END, iid=code, values=(
            code, name, "0.00", "0.00", "0.00", ""
        ))

        # 保存股票列表
        self.save_stocks()
        logging.info(f"添加股票: {code} {name}")

        # 如果正在监控，启动该股票的监控线程
        if not self.stop_event.is_set() and code not in self.monitoring_threads:
            self.start_stock_monitor(code)

    def remove_stock(self):
        """移除股票"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要移除的股票")
            return

        code = selected[0]  # 直接使用iid作为code
        if code in self.stocks:
            del self.stocks[code]

        self.tree.delete(selected)

        # 停止并移除监控线程
        with self.lock:
            if code in self.monitoring_threads:
                del self.monitoring_threads[code]

        # 保存股票列表
        self.save_stocks()
        logging.info(f"移除股票: {code}")

    def set_alert(self):
        """设置提醒阈值"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择股票")
            return

        code = selected[0]  # 使用iid作为code
        item = self.tree.item(code)
        name = item["values"][1]

        # 创建提醒设置窗口
        alert_window = tk.Toplevel(self.root)
        alert_window.title(f"设置 {name}({code}) 的提醒")
        alert_window.geometry("400x300")
        alert_window.transient(self.root)
        alert_window.grab_set()

        frame = ttk.Frame(alert_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # 主力净流入提醒设置
        ttk.Label(frame, text="主力净流入提醒设置:").pack(anchor=tk.W, pady=5)

        threshold_frame = ttk.Frame(frame)
        threshold_frame.pack(fill=tk.X, pady=5)

        ttk.Label(threshold_frame, text="阈值(万元):").pack(side=tk.LEFT, padx=5)
        threshold_var = tk.StringVar()

        # 填充现有设置
        if code in self.alert_settings and "net_inflow" in self.alert_settings[code]:
            threshold_var.set(str(self.alert_settings[code]["net_inflow"][0]))

        ttk.Entry(threshold_frame, textvariable=threshold_var, width=10).pack(side=tk.LEFT, padx=5)

        direction_var = tk.StringVar(value="above")
        ttk.Radiobutton(threshold_frame, text="大于", variable=direction_var, value="above").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(threshold_frame, text="小于", variable=direction_var, value="below").pack(side=tk.LEFT, padx=5)

        # 保存按钮
        def save_alert_settings():
            try:
                threshold = float(threshold_var.get())
                direction = direction_var.get()

                self.alert_settings[code]["net_inflow"] = (threshold, direction)
                self.save_alert_settings()

                messagebox.showinfo("成功", "提醒设置已保存")
                alert_window.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数值")

        ttk.Button(frame, text="保存设置", command=save_alert_settings).pack(pady=20)

    def start_monitoring(self):
        """开始监控所有股票"""
        if not self.stop_event.is_set():
            messagebox.showinfo("提示", "监控已经在运行中")
            return

        self.stop_event.clear()
        self.status_var.set("正在监控中...")

        # 为每个股票启动监控线程
        for code in self.stocks:
            if code not in self.monitoring_threads:
                self.start_stock_monitor(code)

        logging.info("开始监控所有股票")

    def start_stock_monitor(self, code):
        """启动单个股票的监控线程"""
        thread = threading.Thread(target=self.monitor_stock, args=(code,), daemon=True)
        thread.start()
        with self.lock:
            self.monitoring_threads[code] = thread

    def stop_monitoring(self):
        """停止监控所有股票"""
        if self.stop_event.is_set():
            messagebox.showinfo("提示", "监控已经停止")
            return

        self.stop_event.set()
        self.status_var.set("监控已停止")

        # 清空线程字典
        with self.lock:
            self.monitoring_threads.clear()

        logging.info("停止监控所有股票")

    def monitor_stock(self, code):
        """监控单个股票的线程函数"""
        logging.info(f"开始监控股票: {code}")

        # 随机设置初始延迟，避免请求集中
        time.sleep(random.uniform(0, 2))

        while not self.stop_event.is_set():
            # 检查股票是否已被移除
            if code not in self.stocks:
                break

            try:
                # 获取股票数据
                stock_data = self.get_stock_data(code)

                if stock_data:
                    with self.lock:
                        # 更新股票数据
                        self.stocks[code].update(stock_data)
                        self.stocks[code]["update_time"] = datetime.now().strftime("%H:%M:%S")

                    # 更新UI
                    self.update_stock_ui(code)

                    # 检查是否需要触发提醒
                    self.check_alert(code, stock_data)

            except Exception as e:
                logging.error(f"监控股票 {code} 时出错: {str(e)}")

            # 等待一段时间再进行下一次查询（5-10秒随机）
            sleep_time = random.uniform(5, 10)
            for _ in range(int(sleep_time * 10)):
                if self.stop_event.is_set() or code not in self.stocks:
                    break
                time.sleep(0.1)

        logging.info(f"停止监控股票: {code}")

    def get_stock_data(self, code):
        """从东方财富网获取股票数据并处理"""
        try:
            data = get_data(code)
            if not data:
                logging.warning(f"获取 {code} 基本数据失败")
                return None

            # 获取主力净流入
            net_inflow = fund_flow(code)

            # 处理数据类型
            try:
                price = float(data.get('new_price', 0))
                change_percent = float(data.get('price_limit', 0))
                net_inflow_val = float(net_inflow)
            except (ValueError, TypeError):
                return None

            return {
                "name": data.get('stock_name', "未知"),
                "price": f"{price:.2f}",
                "change_percent": f"{change_percent:.2f}",
                "net_inflow": f"{net_inflow_val:.2f}"
            }

        except Exception as e:
            logging.error(f"获取 {code} 数据出错: {str(e)}")
            return None

    def get_stock_name(self, code):
        """获取股票名称（用于添加新股票时）"""
        try:
            data = get_data(code)
            return data.get('stock_name') if data else None
        except Exception as e:
            logging.error(f"获取 {code} 名称失败: {str(e)}")
            return None

    def update_stock_ui(self, code):
        """高效更新UI中的股票数据"""

        def update():
            if code in self.tree.get_children():  # 检查节点是否存在
                stock = self.stocks[code]
                self.tree.item(code, values=(
                    code,
                    stock["name"],
                    stock["price"],
                    stock["change_percent"],
                    stock["net_inflow"],
                    stock["update_time"]
                ))

        self.root.after(0, update)

    def check_alert(self, code, stock_data):
        """检查是否需要触发提醒"""
        if code not in self.alert_settings:
            return

        # 检查主力净流入提醒
        if "net_inflow" in self.alert_settings[code]:
            try:
                threshold, direction = self.alert_settings[code]["net_inflow"]
                current_value = float(stock_data["net_inflow"])

                alert_triggered = False
                alert_msg = ""

                if direction == "above" and current_value >= threshold:
                    alert_triggered = True
                    alert_msg = f"{stock_data['name']}({code}) 主力净流入达到 {current_value:.2f} 万元，超过阈值 {threshold:.2f} 万元"
                elif direction == "below" and current_value <= threshold:
                    alert_triggered = True
                    alert_msg = f"{stock_data['name']}({code}) 主力净流入达到 {current_value:.2f} 万元，低于阈值 {threshold:.2f} 万元"

                if alert_triggered:
                    self.show_alert(alert_msg)
                    logging.warning(alert_msg)

            except (ValueError, TypeError) as e:
                logging.error(f"检查 {code} 提醒时出错: {str(e)}")

    def show_alert(self, message):
        """显示提醒信息"""

        def display():
            self.alert_text.config(state=tk.NORMAL)
            time_str = datetime.now().strftime("%H:%M:%S")
            self.alert_text.insert(tk.END, f"[{time_str}] {message}\n")
            self.alert_text.see(tk.END)
            self.alert_text.config(state=tk.DISABLED)

            # 弹出提醒窗口
            messagebox.showinfo("股票提醒", message)

        self.root.after(0, display)

    def save_alert_settings(self):
        """保存提醒设置到文件"""
        try:
            with open("alert_settings.json", "w", encoding="utf-8") as f:
                json.dump(dict(self.alert_settings), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存提醒设置失败: {str(e)}")

    def load_alert_settings(self):
        """从文件加载提醒设置"""
        try:
            if os.path.exists("alert_settings.json"):
                with open("alert_settings.json", "r", encoding="utf-8") as f:
                    self.alert_settings = defaultdict(dict, json.load(f))
        except Exception as e:
            logging.error(f"加载提醒设置失败: {str(e)}")

    def on_close(self):
        """窗口关闭事件处理"""
        if not self.stop_event.is_set():
            self.stop_monitoring()
        self.save_stocks()  # 确保最后状态被保存
        self.root.destroy()

    def run(self):
        """运行主程序"""
        self.root.mainloop()


if __name__ == "__main__":
    monitor = StockMonitor()
    monitor.run()