import asyncio
import json
import re
import os
import sys
import base64
import requests
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from openai import OpenAI

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
# [解耦点]：导入提示词模板
from app.core.prompts import TEXT_EXTRACT_PROMPT, VISION_STEP_PROMPT

load_dotenv()

class ServiceImporter:
    def __init__(self):
        self.db = SessionLocal()
        self.ds_client = OpenAI(api_key=os.getenv("DeepSeek_API_Key"), 
                                base_url=os.getenv("DeepSeek_Base_URL"))
        self.qwen_client = OpenAI(api_key=os.getenv("DASHSCOPE_API_Key"), 
                                  base_url=os.getenv("DASHSCOPE_Base_URL"))

    async def _get_page_content(self, url):
        """工具：纯粹负责网页抓取与截图"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # 模拟真实浏览器请求头
            await page.set_extra_http_headers({"Referer": "https://zwfw.dl.gov.cn/"})
            await page.goto(url, wait_until="networkidle")
            
            # 1. 获取文本内容（主容器定位）
            container = await page.query_selector(".item-detail-container") or await page.query_selector("body")
            raw_text = await container.inner_text()
            
            # 2. 【核心优化】精准定位流程图图片
            # 根据你提供的截图，ID 是 flow_chart
            img_b64 = None
            img_locator = page.locator("#flow_chart img")
            
            try:
                # 确保图片已加载
                await img_locator.wait_for(state="visible", timeout=5000)
                # 自动执行：定位 -> 捕获显存内容 -> 转为 Base64
                img_bytes = await img_locator.screenshot()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                print(f"📸 成功通过逻辑定位提取流程图数据 (size: {len(img_b64)})")
            except Exception as e:
                print(f"⚠️ 流程图提取失败 (ID: #flow_chart 可能未加载): {e}")

            await browser.close()
            return raw_text, img_b64

    def _get_latlng(self, address):
        
        if not address or address in ["暂无", "详见官方说明"]:
            return None

        url = "https://restapi.amap.com/v3/geocode/geo"
        key = os.getenv("AMAP_WEB_KEY")
        
        # 清洗：截断详细窗口信息
        clean_address = re.split(r'\(|（|第|楼|窗', address)[0]
        
        params = {"key": key, "address": clean_address, "city": "大连"}

        try:
            res = requests.get(url, params=params, timeout=5).json()
            if res.get('status') == '1' and res.get('geocodes'):
                location = res['geocodes'][0]['location']
                return location
            else:
                # 记录具体原因但不再返回假数据
                print(f"⚠️ 地理编码失败: {address} (高德回复: {res.get('info')})")
                return None
        except Exception as e:
            print(f"❌ 地理编码请求异常: {e}")
            return None

    def _ai_parse_text(self, text):
        """工具：调用 DeepSeek 结构化文本"""
        prompt = TEXT_EXTRACT_PROMPT.format(raw_text=text)
        res = self.ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content
        return json.loads(re.search(r'\{.*\}', res, re.DOTALL).group())

    def _ai_parse_vision(self, img_b64):
        """工具：调用 Qwen-VL 解析流程图"""
        if not img_b64: return []
        res = self.qwen_client.chat.completions.create(
            model="qwen3-vl-flash",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": VISION_STEP_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]}]
        ).choices[0].message.content
        match = re.search(r'\[.*\]', res, re.DOTALL)
        return json.loads(match.group()) if match else []

    async def process_single_url(self, url):
        """核心管线：串联所有解耦后的步骤"""
        print(f"开始处理: {url}")
        
        # 1. 抓取原始资源
        raw_text, img_b64 = await self._get_page_content(url)
        
        # 2. AI 语义解析
        text_data = self._ai_parse_text(raw_text)
        flow_steps = self._ai_parse_vision(img_b64)
        
        # 3. 坐标转换
        latlng = self._get_latlng(text_data['address'])
        
        # 4. 数据封装入库
        new_guide = models.ServiceGuide(
            title=text_data['title'],
            dept_name=text_data['dept_name'],
            conditions=json.dumps(text_data['conditions'], ensure_ascii=False),
            materials=json.dumps(text_data['materials'], ensure_ascii=False),
            flow_steps=json.dumps(flow_steps, ensure_ascii=False),
            address=text_data['address'],
            latlng=latlng,
            office_time=text_data['office_time'],
            phone=text_data['phone'],
            source_url=url,
            modify_by=1
        )
        self.db.add(new_guide)
        self.db.commit()
        print(f"成功导入: {text_data['title']}")

    def start_batch(self, urls):
        """执行批量任务"""
        for url in urls:
            try:
                asyncio.run(self.process_single_url(url))
            except Exception as e:
                print(f"URL {url} 处理失败: {e}")

    async def collect_urls_from_filter(self, filter_url, user_topic_types=None, corp_topic_types=None):
        """
        从服务目录筛选页批量收集所有详情页 URL。
        参数:
            filter_url — 筛选页 URL（提供基础参数和 access_token）
            user_topic_types — 个人主题 ID，逗号分隔，如 "125,130"（多选时必传）
            corp_topic_types — 法人主题 ID，逗号分隔（多选时必传）
        返回: 去重后的详情页 URL 列表
        """
        print(f"正在收集 URL: {filter_url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers({"Referer": "https://zwfw.dl.gov.cn/"})
            await page.goto(filter_url, wait_until="networkidle")

            # 1. 调第一页 API 获取总数（支持覆盖多选主题参数）
            first_page = await page.evaluate("""([topicTypes, corpTypes]) => {
                const formData = new URLSearchParams();
                for (const el of document.querySelectorAll('#form input')) {
                    if (el.name) formData.append(el.name, el.value);
                }
                if (topicTypes) formData.set('userTopicType', topicTypes);
                if (corpTypes) formData.set('corpTopicType', corpTypes);
                formData.set('pageNumber', '1');
                formData.set('pageSize', '5');
                return fetch(webRoot + '/item/itemList', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData.toString()
                }).then(r => r.json());
            }""", [user_topic_types, corp_topic_types])

            total = first_page["count"]
            total_pages = (total + 4) // 5
            print(f"共 {total} 条，{total_pages} 页")

            item_ids = set()
            for page_num in range(1, total_pages + 1):
                print(f"收集第 {page_num}/{total_pages} 页...")
                data = await page.evaluate("""([pageNum, topicTypes, corpTypes]) => {
                    const formData = new URLSearchParams();
                    for (const el of document.querySelectorAll('#form input')) {
                        if (el.name) formData.append(el.name, el.value);
                    }
                    if (topicTypes) formData.set('userTopicType', topicTypes);
                    if (corpTypes) formData.set('corpTopicType', corpTypes);
                    formData.set('pageNumber', String(pageNum));
                    formData.set('pageSize', '5');
                    return fetch(webRoot + '/item/itemList', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: formData.toString()
                    }).then(r => r.json());
                }""", [page_num, user_topic_types, corp_topic_types])

                for group in data.get("itemList", []):
                    for item in group.get("itemList", []):
                        item_ids.add(item["ITEM_ID"])

                await asyncio.sleep(1)  # 礼貌延迟

            await browser.close()

        urls = [f"https://zwfw.dl.gov.cn/dlPortal/item/toDetails/{iid}" for iid in item_ids]
        print(f"收集完成: {len(urls)} 个唯一 URL")
        return urls

if __name__ == "__main__":
    importer = ServiceImporter()

    # 步骤1: 从筛选页自动收集所有办事指南 URL
    filter_url = "https://zwfw.dl.gov.cn/dlPortal/filterWork?areaCode=210201000000&userTopicType=125&serverType=1"
    # 多选主题时传逗号分隔字符串（在页面勾选后从 #UserTopicType 的值获取）
    urls = asyncio.run(importer.collect_urls_from_filter(
        filter_url,
        user_topic_types="010,065,075,085,090",  # 替换为实际勾选的主题 ID 列表 document.querySelector('#UserTopicType').value
    ))

    # 过滤已导入的 URL
    existing = {g.source_url for g in importer.db.query(models.ServiceGuide.source_url).all()}
    new_urls = [u for u in urls if u not in existing]
    print(f"已入库 {len(existing)} 条，新增 {len(new_urls)} 条")

    # 步骤2: 逐条抓取并入库
    importer.start_batch(new_urls)