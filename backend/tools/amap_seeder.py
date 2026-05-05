import os
import requests
import models
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal

load_dotenv()
AMAP_WEB_KEY = os.getenv("AMAP_WEB_KEY")
CITY = "大连"

SEARCH_TARGETS = [
    {"keyword": "医院", "category": "医疗"},
]

def fetch_seed():
    db = SessionLocal()
    print("Fetching seed data from AMap API")
    
    for target in SEARCH_TARGETS:
        url = f"https://restapi.amap.com/v3/place/text?keywords={target['keyword']}&city={CITY}&output=json&key={AMAP_WEB_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == '1':
                pois = data['pois']
                for poi in pois:
                    # 检查是否已存在（根据名称去重）
                    exists = db.query(models.Resource).filter(models.Resource.name == poi['name']).first()
                    if exists: continue

                    # 解析坐标 "121.536767,38.918933"
                    lng, lat = map(float, poi['location'].split(','))

                    new_resource = models.Resource(
                        name=poi['name'],
                        category=target['category'],
                        address=poi['address'] if poi['address'] else "详见地图位置",
                        lng=lng,
                        lat=lat,
                        phone=poi['tel'] if poi.get('tel') else "暂无",
                        tags=f"{target['keyword']},{poi['type']}",
                        description=f"来自高德地图的{target['keyword']}信息"
                    )
                    db.add(new_resource)
                
                db.commit()
                print(f"✅ 已成功导入 {len(pois)} 个[{target['category']}]相关的点位")
            else:
                print(f"❌ API 报错: {data['info']}")
        except Exception as e:
            print(f"⚠️ 处理关键字 [{target['keyword']}] 时出错: {e}")
    
    db.close()

if __name__ == "__main__":
    fetch_seed()

