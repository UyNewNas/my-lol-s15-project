'''
Author: slava
Date: 2025-10-27 09:42:21
LastEditTime: 2025-10-28 02:22:39
LastEditors: ch4nslava@gmail.com
Description: 

'''



from playwright.sync_api import sync_playwright, Route
from typing import List, Dict, Optional, Callable, Union
import re
from bs4 import BeautifulSoup
import json
import datetime
import os
DIR = os.path.dirname(os.path.abspath(__file__))

# URL_LOLESPORTS = "https://lolesports.com/schedule?leagues=lol&regions=all&seasons=all"
URL_Bilibili = "https://www.bilibili.com/v/game/match/schedule"



'''
从Bilibili获取LOL S15赛程
0. 访问Bilibili LOL赛程页面
1. 赛事筛选：LOL全球总决赛
2. 选择日期
3. 提取比赛信息：队伍名称、比赛时间、直播链接等
'''

import re
from playwright.sync_api import Playwright, sync_playwright, expect



def scrape_from_bilibili_single_page(playwright: Playwright, date_range: list) -> dict:
    """
    在同一个浏览器页面中连续爬取多个日期的LOL全球总决赛赛程数据
    
    Args:
        playwright: Playwright实例
        date_range: 日期字符串列表，格式为["YYYY-MM-DD", "YYYY-MM-DD", ...]
        
    Returns:
        按日期组织的比赛数据字典
    """
    # 存储所有日期的比赛数据 - 按日期组织
    all_match_data = {}
    total_matches = 0
    
    print(f"开始在单一页面中连续爬取 {len(date_range)} 天的比赛赛程")
    print(f"日期范围: {date_range[0]} 至 {date_range[-1]}")
    
    # 存储API响应数据
    api_response_data = None
    # 获取当前时间的时间戳
    now = datetime.datetime.now().timestamp()
    
    # 处理API响应的函数
    def handle_api_request(route: Route, request):
        nonlocal api_response_data
        # 检查是否是目标API请求
        if "api.bilibili.com/x/esports/matchs/list" in request.url:
            print(f"\n检测到目标API请求: {request.url}")
            # 继续请求并获取响应
            response = route.fetch()
            # 获取响应内容
            response_body = response.body()
            # 解析JSON数据
            try:
                api_response_data = json.loads(response_body)
                print("\nAPI响应数据解析成功！")
            except json.JSONDecodeError:
                print("JSON解析失败")
            # 继续路由
            route.continue_()
        else:
            # 对于其他请求，直接继续
            route.continue_()
    
    # 启动浏览器（只启动一次）
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL_Bilibili)
    
    # 先访问页面，然后点击全球总决赛选项
    page.get_by_role("listitem").filter(has_text="LOL全球总决赛").get_by_role("img").click()
    print("已选择LOL全球总决赛")
    
    # 等待页面更新
    page.wait_for_timeout(1000)
    
    # 设置请求拦截器
    print("开始设置请求拦截器，仅捕获全球总决赛比赛数据")
    context.route("**/api.bilibili.com/x/esports/matchs/list**", handle_api_request)
    
    # 遍历每个日期进行爬取
    for date_idx, date in enumerate(date_range):
        # 重置API响应数据
        api_response_data = None
        
        # 目标年月日
        year = date.split("-")[0]
        month = date.split("-")[1]
        day = date.split("-")[2]
        
        print(f"\n[{date_idx + 1}/{len(date_range)}] 正在爬取 {date} 的比赛赛程")
        
        # 点击日期选择器
        page.locator("#server-game-app").get_by_role("textbox").click()
        page.locator(".iconfont.icon-xia").click()
        
        # 先选择正确的月份
        page.get_by_text("%s 年" % year).nth(1).click()
        
        # 获取当前显示的月份
        current_month_text = page.locator("xpath=/html/body/div[1]/div[2]/div[2]/div[1]/div[3]/div/div/div/div[1]/div[2]/a").text_content()
        
        # 提取当前月份数字（例如从"10月"提取"10"）
        current_month = int(re.search(r'^(\d+)月$', current_month_text).group(1))
        target_month = int(month)
        
        print(f"当前显示月份: {current_month}月，目标月份: {target_month}月")
        
        # 计算需要前进或后退的步数
        month_diff = target_month - current_month
        
        # 根据差值点击相应的前进或后退按钮
        if month_diff > 0:
            # 需要前进的月份数
            print(f"需要前进 {month_diff} 个月")
            for _ in range(month_diff):
                page.locator(".iconfont.icon-ic_into").click()
                page.wait_for_timeout(500)  # 等待页面更新
        elif month_diff < 0:
            # 需要后退的月份数
            print(f"需要后退 {-month_diff} 个月")
            for _ in range(-month_diff):
                page.locator(".iconfont.icon-ic_back").click()
                page.wait_for_timeout(500)  # 等待页面更新
        else:
            print("当前月份就是目标月份，无需调整")
        
        # 获取当前选中的日期
        try:
            # 确保current_selected_date始终有整数值
            current_selected_date = 1  # 默认值设为1
            try:
                # 获取当前高亮的日期元素
                selected_date_element = page.locator(".datepicker-table td.active")
                if selected_date_element.is_visible():
                    current_selected_date_text = selected_date_element.text_content().strip()
                    if current_selected_date_text and current_selected_date_text.isdigit():
                        current_selected_date = int(current_selected_date_text)
                        print(f"当前选中日期: {current_selected_date}")
                    else:
                        print("获取到的日期文本无效，使用默认值1")
                else:
                    print("没有找到高亮的日期元素，使用默认值1")
            except Exception as e:
                print(f"获取当前选中日期时出错: {e}，使用默认值1")
            
            target_day = int(day)
            
            # 计算需要前进或后退的步数
            day_diff = target_day - current_selected_date
            print(f"需要调整的天数差: {day_diff}")
            
            if day_diff > 0:
                # 需要前进的天数
                print(f"需要前进 {day_diff} 天")
                for _ in range(day_diff):
                    page.locator(".time-direction.time-aright").click()
                    page.wait_for_timeout(300)
            elif day_diff < 0:
                # 需要后退的天数
                print(f"需要后退 {-day_diff} 天")
                for _ in range(-day_diff):
                    page.locator(".time-direction").first.click()
                    page.wait_for_timeout(300)
            else:
                print("当前日期已经是目标日期，无需调整")
                
        except Exception as e:
            print(f"使用方向键选择日期时出错: {e}")
            # 如果方向键选择失败，尝试备选方案 - 直接点击日期
            try:
                page.get_by_title(date).click()
                print("备选方案：直接通过title选择日期成功")
            except:
                print("备选方案也失败了，尝试直接点击日期数字")
                try:
                    page.locator(f".datepicker-table td:has-text('{day}')").click()
                except:
                    print(f"警告: 无法选择日期 {date}，继续执行")
        
        # 无论日期选择是否成功，都等待一段时间让页面更新
        page.wait_for_timeout(1000)
        
        # 等待一段时间，确保API请求被捕获
        # page.wait_for_timeout(4000)  # 稍微减少等待时间提高效率
        
        # 当前日期的比赛数据
        day_match_data = {}
        
        # 解析API响应数据
        if api_response_data and "data" in api_response_data:
            try:
                data = api_response_data["data"]
                print(f"\n数据结构:")
                print(f"  - 总比赛数: {data.get('total', 0)}")
                print(f"  - 当前页数: {data.get('pn', 0)}")
                print(f"  - 每页数量: {data.get('ps', 0)}")
                
                # 解析比赛列表
                if "list" in data:
                    print(f"  - 比赛列表数量: {len(data['list'])}")
                    for i, match in enumerate(data['list'], 1):
                        match_info_json = {}
                        print(f"\n  比赛 {i}:")
                        print(f"    - 比赛ID: {match.get('id', 'N/A')}")
                        print(f"    - 比赛名称: {match.get('game_stage', 'N/A')}")
                        # 转化时间戳为日期时间格式
                        start_time = datetime.datetime.fromtimestamp(match.get('start_time', 0))
                        end_time = datetime.datetime.fromtimestamp(match.get('end_time', 0))
                        print(f"    - 比赛开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"    - 比赛结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        # 根据时间戳判断比赛状态
                        if now < match.get('start_time', 0):
                            match_status = "未开始"
                        elif now < match.get('end_time', 0):
                            match_status = "进行中"
                        else:
                            match_status = "已结束"
                        print(f"    - 比赛状态: {match_status}") 
                        # 对阵信息
                        if "away_team" in match and "home_team" in match:
                            match_away_team = match.get('away_team', {})
                            match_home_team = match.get('home_team', {})
                            print(f"    - 客队 名称: {match_away_team.get('title', 'N/A')}")                                 
                            print(f"    - 客队 比分: {match.get('away_score', 'N/A')}")
                            print(f"    - 主队 名称: {match_home_team.get('title', 'N/A')}")
                            print(f"    - 主队 比分: {match.get('home_score', 'N/A')}")
                            match_info_json  = {
                                "match_id": match.get('id', 'N/A'),
                                "match_name": match.get('game_stage', 'N/A'),
                                "match_start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                "match_end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
                                "match_status": match_status,
                                "match_away_team": match_away_team.get('title', 'N/A'),
                                "match_away_score": match.get('away_score', 'N/A'),
                                "match_home_team": match_home_team.get('title', 'N/A'),
                                "match_home_score": match.get('home_score', 'N/A'),
                                "date": date  # 添加日期信息
                            }
                            day_match_data[match_info_json["match_id"]] = match_info_json
            except Exception as e:
                print(f"解析比赛数据时出错: {e}")
        else:
            print("未捕获到API响应数据")
        
        # 如果当天有比赛数据，按日期存储
        if day_match_data:
            # 将当天的比赛数据存储到日期键下
            all_match_data[date] = {
                "date": date,
                "total_matches": len(day_match_data),
                "matches": day_match_data
            }
            total_matches += len(day_match_data)
            print(f"  日期 {date} 已添加 {len(day_match_data)} 场比赛")
        else:
            # 如果当天没有比赛数据，也记录空数据
            all_match_data[date] = {
                "date": date,
                "total_matches": 0,
                "matches": {}
            }
            print(f"  日期 {date} 没有找到比赛数据")
    
    # 关闭浏览器（只关闭一次）
    context.close()
    browser.close()
    
    print(f"\n所有日期爬取完成！总爬取场次: {total_matches}")
    
    # 返回所有日期的比赛数据
    return all_match_data

def scrape_date_range(start_date_str: str, end_date_str: str, output_file: str = "lol_s15_schedule.json") -> None:
    """
    在同一个页面中连续爬取指定日期范围内的所有LOL全球总决赛赛程数据并按日期保存到JSON文件
    
    Args:
        start_date_str: 开始日期字符串，格式为"YYYY-MM-DD"
        end_date_str: 结束日期字符串，格式为"YYYY-MM-DD"
        output_file: 输出的JSON文件路径
    """
    # 转换日期字符串为datetime对象
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    
    # 验证日期范围
    if start_date > end_date:
        print("错误：开始日期不能晚于结束日期")
        return
    
    # 生成日期列表
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime("%Y-%m-%d"))
        current_date += datetime.timedelta(days=1)
    
    total_days = len(date_range)
    print(f"开始爬取日期范围：{start_date_str} 至 {end_date_str}（共 {total_days} 天）")
    print("数据将按日期组织存储在JSON文件中")
    
    # 使用单一页面爬取所有日期的数据
    with sync_playwright() as playwright:
        all_match_data = scrape_from_bilibili_single_page(playwright, date_range)
    
    # 统计总比赛场次
    total_matches = sum(date_data.get('total_matches', 0) for date_data in all_match_data.values())
    
    # 保存数据到JSON文件
    print(f"\n爬取完成！共获取到 {total_matches} 场比赛数据")
    print(f"涉及 {len([d for d in all_match_data.values() if d['total_matches'] > 0])} 天有比赛")
    print(f"正在保存数据到文件: {output_file}")
    
    try:
        # 确保输出目录存在
        import os
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存为JSON文件，使用中文编码和美观的格式
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_match_data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已成功保存到: {os.path.abspath(output_file)}")
        print(f"\n数据统计:")
        print(f"- 总比赛场次: {total_matches}")
        
        # 统计不同状态的比赛数量
        status_count = {"未开始": 0, "进行中": 0, "已结束": 0}
        for date_data in all_match_data.values():
            for match_info in date_data.get('matches', {}).values():
                status = match_info.get('match_status', '未知')
                if status in status_count:
                    status_count[status] += 1
        
        for status, count in status_count.items():
            print(f"- {status}的比赛: {count} 场")
        
        # 按日期输出有比赛的天数
        print(f"- 有比赛的天数: {len([d for d in all_match_data.values() if d['total_matches'] > 0])} 天")
        
    except Exception as e:
        print(f"保存数据失败: {e}")

# 如果直接运行脚本，爬取默认日期范围的赛程
def main():
    # 默认爬取10月1日到10月31日的赛程
    scrape_date_range("2025-10-14", "2025-11-09", os.path.join(DIR, "lol_s15_schedule.json"))

if __name__ == "__main__":
    main()
