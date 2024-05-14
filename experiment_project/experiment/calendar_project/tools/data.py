import random
from datetime import datetime, timedelta
locations = ["Company Conference Room", "Downtown Cafe", "City Park", "Home", "Local Gym", "Art Museum", "New York Office"]
people = ["Alice", "Bob", "Charlie", "Dana", "Evan", "Fiona", "George"]

# 更新基本工作日程模板以包含地点和相关人物
work_events_template = [
    {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": []},
    {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"]},
    {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"]},
    {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"]},
    {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": []},
]





# 定义可能的个人活动
personal_events = [
    {"event_name": "Annual Leave", "description": "Taking a day off for relaxation."},
    {"event_name": "Visit Parents", "description": "Spending quality time with parents."},
    {"event_name": "City Exploration", "description": "Exploring new places in the city."},
    {"event_name": "Dinner with Friends", "description": "Catching up with friends over dinner."},
    {"event_name": "Weekend Getaway", "description": "A short trip to recharge."},
    {"event_name": "Gym Session", "description": "Attending a workout session at the gym."},
    {"event_name": "Book Club Meeting", "description": "Discussing the latest book with the club."},
    {"event_name": "Cooking Class", "description": "Learning new cooking techniques."},
    {"event_name": "Volunteering", "description": "Giving back to the community through volunteering."},
    {"event_name": "Concert Night", "description": "Enjoying live music at a concert."},
    {"event_name": "Movie Marathon", "description": "A cozy night in with back-to-back movies."},
    {"event_name": "Art Exhibition", "description": "Visiting an art exhibition."},
    {"event_name": "Yoga Retreat", "description": "A day of yoga and meditation."},
    {"event_name": "Fishing Trip", "description": "A relaxing day of fishing."},
    {"event_name": "Photography Walk", "description": "Capturing the beauty of the city through the lens."},
]

def create_monthly_schedule(work_template, personal_events,days_num:int=30):
    monthly_schedule = []
    start_date = datetime.now()

    # 生成工作日的日程
    for day_offset in range(days_num):  # 假设一个月30天
        current_date = start_date + timedelta(days=day_offset)
        if current_date.weekday() < 5:  # 0-4为周一至周五
            for event in work_template:
                work_event = event.copy()
                work_event["date"] = current_date.strftime('%Y-%m-%d')
                monthly_schedule.append(work_event)

    # 添加随机个人活动
    for event in personal_events:
        monthly_schedule.append(event)

    return monthly_schedule
def generate_random_events(events_list, num_events=15):
    random_events = []
    start_date = datetime.now()
    for _ in range(num_events):
        event = random.choice(events_list)
        date = (start_date + timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')  # 随机未来60天内的日期
        start_hour = random.randint(8, 17)  # 随机开始小时
        end_hour = start_hour + random.randint(1, 6)  # 随机结束小时，持续1到3小时
        location = random.choice(locations)  # 随机选择地点
        involved_people = random.sample(people, k=random.randint(1, 3))  # 随机选择1到3个相关人物
        random_event = {
            "event_name": event["event_name"],
            "date": date,
            "start_time": f"{start_hour:02d}:00",
            "end_time": f"{end_hour:02d}:00",
            "location": location,
            "description": event["description"],
            "people": involved_people
        }
        random_events.append(random_event)
    return random_events


def create_user_event(days_num:int=15)->list:
    random_personal_events = generate_random_events(personal_events, num_events=25)

    # 合并工作日程和个人活动到一个月的日程中
    # 创建一个月的日程
    monthly_schedule = create_monthly_schedule(work_events_template, random_personal_events,days_num=days_num)

    return monthly_schedule

    # 添加

# 生成随机个人活动

# 打印结果（打印前10个事件作为示例）
