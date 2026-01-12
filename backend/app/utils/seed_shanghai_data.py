
import random
import math

def generate_random_shanghai_points(count=300):
    """
    Generate random locations around Shanghai center (People's Square)
    Center: 31.2304, 121.4737
    """
    center_lat = 31.2304
    center_lng = 121.4737
    
    locations = []
    
    # Districts for fake addresses (Chinese)
    districts = ["黄浦区", "徐汇区", "长宁区", "静安区", "普陀区", "虹口区", "杨浦区", "浦东新区"]
    streets = ["南京路", "淮海路", "延安路", "四川路", "西藏路", "北京路", "福州路", "衡山路", "华山路", "江苏路"]
    
    first_names = ["张", "王", "李", "赵", "陈", "刘", "周", "吴", "郑", "孙"]
    last_names = ["伟", "芳", "娜", "敏", "静", "秀英", "丽", "强", "军", "洋", "勇", "杰", "磊", "超"]

    for i in range(count):
        # Random radius distribution (0 to 15km)
        radius = 0.15 * math.sqrt(random.random()) 
        angle = random.random() * 2 * math.pi
        
        # Calculate offsets
        lat_offset = radius * math.cos(angle)
        lng_offset = radius * math.sin(angle)
        
        lat = center_lat + lat_offset
        lng = center_lng + lng_offset * 1.1 # Adjust for longitude projection slightly
        
        dist = random.choice(districts)
        street = random.choice(streets)
        num = random.randint(1, 9999)
        
        name = random.choice(first_names) + random.choice(last_names)
        
        locations.append({
            "name": f"{street}{num}号",
            "address": f"上海市{dist}{street}{num}号",
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "district": dist,
            "recipient": name
        })
        
    return locations

# Generate once on module load or call function
SHANGHAI_LOCATIONS = generate_random_shanghai_points(300)

def get_shanghai_locations():
    return SHANGHAI_LOCATIONS
