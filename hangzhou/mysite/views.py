import re

from django.shortcuts import render
from pyecharts import Bar, Pie, Line, Scatter, Boxplot, Radar, WordCloud
import numpy as np
import pandas as pd

REMOTE_HOST = "https://pyecharts.github.io/assets/js"


def index(request):
    return render(request, 'mysite/index.html')


def food_page_first(request):
    food = pd.read_csv('../data/food.csv')
    type_info = food.groupby('type').name.count().sort_values(ascending=False)
    type_bar = Bar('各菜系商家数量', width='1000px', title_pos='center', title_top='bottom')
    type_bar.add('数量', type_info.index, type_info.values, is_label_show=True, bar_category_gap='30%', xaxis_rotate=50)
    zone_info = food.groupby('zone').name.count().sort_values(ascending=False).head(15)
    zone_bar = Bar('各商圈商家数量', title_pos='center', title_top='bottom')
    zone_bar.add('数量', zone_info.index, zone_info.values, is_label_show=True, xaxis_rotate=30)
    star_list = ['二星商户', '三星商户', '准四星商户', '四星商户', '准五星商户', '五星商户']
    star_data = food[food.star.isin(['二星商户', '三星商户', '准四星商户', '四星商户', '准五星商户', '五星商户'])]
    star_data['star'] = star_data['star'].astype('category')
    star_data['star'].cat.set_categories(star_list, inplace=True)
    star_data.sort_values('star', inplace=True)
    star_info = star_data.groupby('star').name.count()
    star_pie = Pie('商家星级比例', title_pos='center', title_top='bottom')
    star_pie.add('数量', star_info.index, star_info.values, is_label_show=True)
    context = dict(
        echart1=type_bar.render_embed(),
        echart2=zone_bar.render_embed(),
        echart3=star_pie.render_embed(),
        host=REMOTE_HOST,
        script_list=type_bar.get_js_dependencies()
    )
    return render(request, 'mysite/food1.html', context)


def food_page_second(request):
    food = pd.read_csv('../data/food.csv')
    price_data = food.dropna(subset=['price'])
    for i, price in enumerate(price_data.price.values):
        price_data.price.values[i] = price.strip('￥')
    price_data[['price']] = price_data[['price']].astype(int)
    price_data = price_data[price_data.price < 2000]
    price_data.rename(columns={'recommend.0': 'recommend0', 'recommend.1': 'recommend1', 'recommend.2': 'recommend2'},
                      inplace=True)
    price_data_high = price_data.sort_values(by='price', ascending=False).head(5)
    highs = [row for index, row in price_data_high.iterrows()]
    price_data_high_bar = Bar("人均消费水平最高的五家店铺", width='600px', title_pos='center', title_top='bottom')
    price_data_high_bar.add('', price_data_high.name, price_data_high.price, xaxis_rotate=10, bar_category_gap='30%',
                            yaxis_name='元', yaxis_name_pos='end')
    price_data_low = price_data.sort_values(by='price').head(5)
    lows = [row for index, row in price_data_low.iterrows()]
    price_data_low_bar = Bar("人均消费水平最低的五家店铺", width='600px', title_pos='center', title_top='bottom')
    price_data_low_bar.add('', price_data_low.name, price_data_low.price, xaxis_rotate=10, bar_category_gap='30%',
                           yaxis_name='元', yaxis_name_pos='end')
    price_data_sub = price_data[price_data.price < 500]
    price_info = price_data_sub.groupby('price').name.count()
    price_limit = [i for i in price_info.index]
    price_scatter = Scatter("人均消费(<=500元)", title_pos='center', title_top='bottom')
    price_scatter.add('', price_info.index, price_info.values, extra_data=price_limit, is_visualmap=True,
                      xaxis_name='人均/元',
                      xaxis_name_pos='end', yaxis_name='店铺数量/家', yaxis_name_pos='end', visual_range=[0, 500])
    boxplot = Boxplot('人均消费箱型图', width='400px', title_pos='center', title_top='bottom')
    x_axis = ['']
    boxplot.add('', x_axis, boxplot.prepare_data([price_data.price]), yaxis_name='元', yaxis_name_pos='end')
    price_range = list(range(0, 201, 20))
    price_range.append(13000)
    price_data['range'] = pd.cut(price_data.price, price_range, right=True)
    price_data_range = price_data.groupby('range').name.count()
    x_range = ['(0, 20]', '(20, 40]', '(40, 60]', '(60, 80]', '(80, 100]', '(100, 120]',
               '(120, 140]', '(140, 160]', '(160, 180]', '(180, 200]', '>200']
    line = Line("分区间人均消费水平", width='600px', title_pos='center', title_top='bottom')
    line.add('', x_range, price_data_range.values, xaxis_rotate=30)
    context = dict(
        echart1=price_scatter.render_embed(),
        echart2=boxplot.render_embed(),
        echart3=line.render_embed(),
        echart4=price_data_high_bar.render_embed(),
        echart5=price_data_low_bar.render_embed(),
        highs=highs,
        lows=lows,
        price_data_high=price_data_high,
        price_data_high_name=price_data_high.name,
        price_data_high_price=price_data_high.price,
        host=REMOTE_HOST,
        script_list=price_scatter.get_js_dependencies()
    )
    return render(request, 'mysite/food2.html', context)


def food_page_third(request):
    food = pd.read_csv('../data/food.csv')
    comment_data = food.dropna(subset=['comment'])
    comment_data_most = comment_data.sort_values(by='comment', ascending=False).head(5)
    popular_shop = [row for index, row in comment_data_most.iterrows()]
    comment_bar = Bar("评论最多的店铺", width='600px', title_pos='center', title_top='bottom')
    comment_bar.add('', comment_data_most.name, comment_data_most.comment, xaxis_rotate=15, is_label_show=True)
    comment_data['name'] = comment_data['name'].map(lambda x: x.split('(')[0])
    shop = comment_data.groupby('name').name.count().sort_values(ascending=False).head(15)
    shop_bar = Bar("分店最多的店铺", title_pos='center', title_top='bottom')
    shop_bar.add('', shop.index, shop.values, xaxis_rotate=30, is_label_show=True)
    context = dict(
        echart1=shop_bar.render_embed(),
        echart2=comment_bar.render_embed(),
        popular_shop=popular_shop,
        host=REMOTE_HOST,
        script_list=shop_bar.get_js_dependencies()
    )
    return render(request, 'mysite/food3.html', context)


def food_page_fourth(request):
    food = pd.read_csv('../data/food.csv')
    filter_data = food.groupby('type').filter(lambda x: x['name'].count() >= 100)
    score_data = filter_data.groupby('type')['name', 'taste', 'env', 'service'].mean()
    score_data.dropna(inplace=True)
    score_data_name = score_data.index
    score_data_taste = score_data['taste']
    score_data_env = score_data['env']
    score_data_service = score_data['service']
    line = Line("各菜系口味、环境、服务平均得分", width='1200px', title_pos='center', title_top='bottom')
    line.add('口味', score_data_name, score_data_taste, xaxis_rotate=60)
    line.add('环境', score_data_name, score_data_env, xaxis_rotate=60)
    line.add('服务', score_data_name, score_data_service, xaxis_rotate=60)
    taste_high_data = food.sort_values(by='taste', ascending=False).head(5)
    env_high_data = food.sort_values(by='env', ascending=False).head(5)
    service_high_data = food.sort_values(by='service', ascending=False).head(5)
    schema = [
        ("口味", 10), ("环境", 10), ("服务", 10)
    ]
    rader1 = Radar("口味最好的五家店铺", width='1000px', title_pos='center', title_top='bottom')
    rader1.config(schema)
    for index, row in taste_high_data.iterrows():
        rader1.add(row['name'], [[row.taste, row.env, row.service]], legend_selectedmode='single')
    rader2 = Radar("环境最好的五家店铺", width='1000px', title_pos='center', title_top='bottom')
    rader2.config(schema)
    for index, row in env_high_data.iterrows():
        rader2.add(row['name'], [[row.taste, row.env, row.service]], legend_selectedmode='single')
    rader3 = Radar("服务最好的五家店铺", width='1000px', title_pos='center', title_top='bottom')
    rader3.config(schema)
    for index, row in service_high_data.iterrows():
        rader3.add(row['name'], [[row.taste, row.env, row.service]], legend_selectedmode='single')
    context = dict(
        echart1=line.render_embed(),
        echart2=rader1.render_embed(),
        echart3=rader2.render_embed(),
        echart4=rader3.render_embed(),
        host=REMOTE_HOST,
        script_list=line.get_js_dependencies()
    )
    return render(request, 'mysite/food4.html', context)


def food_page_fifth(request):
    food = pd.read_csv('../data/food.csv')
    recommends = pd.concat([food['recommend.0'], food['recommend.1'], food['recommend.2']], )
    recommends = pd.DataFrame({'recommend': recommends})
    recommend_data = recommends.groupby('recommend').recommend.count().sort_values(ascending=False).head(200)
    recommend_name = [i for i in recommend_data.index]
    for i, name in enumerate(recommend_name):
        recommend_name[i] = name.strip('不少于')
    worldcloud = WordCloud(width=1000, height=800)
    worldcloud.add("", recommend_name, recommend_data.values, word_size_range=[10, 100], shape='star')
    context = dict(
        echart=worldcloud.render_embed(),
        host=REMOTE_HOST,
        script_list=worldcloud.get_js_dependencies()
    )
    return render(request, 'mysite/food5.html', context)


def spot_page_first(request):
    spot = pd.read_csv('../data/spot.csv')
    spot_sub_data = spot.head(100)
    spot_value = [1] * 100
    worldcloud = WordCloud(width=1000, height=800)
    worldcloud.add("", spot_sub_data.title, spot_value, word_size_range=[20, 20])
    context = dict(
        echart=worldcloud.render_embed(),
        host=REMOTE_HOST,
        script_list=worldcloud.get_js_dependencies()
    )
    return render(request, 'mysite/spot1.html', context)


def spot_page_second(request):
    spot = pd.read_csv('../data/spot.csv')
    comment_data = spot.dropna(subset=['comment'])
    comment_data['comment'] = comment_data['comment'].map(lambda x: int("".join(filter(str.isdigit, x))))
    top10 = comment_data.sort_values(by='comment', ascending=False).head(10)
    comment_bar = Bar('热门景点', width=1000, title_pos='center', title_top='bottom')
    comment_bar.add('', top10.title, top10['comment'], xaxis_rotate=30, yaxis_name='评论数', yaxis_name_pos='end')
    context = dict(
        echart=comment_bar.render_embed(),
        host=REMOTE_HOST,
        script_list=comment_bar.get_js_dependencies()
    )
    return render(request, 'mysite/spot2.html', context)


def spot_page_third(request):
    spot = pd.read_csv('../data/spot.csv')
    ticket_data = spot.dropna(subset=['ticket'])
    ticket_data.index = pd.RangeIndex(len(ticket_data.index))
    ticket_data.index = range(len(ticket_data.index))
    for i, ticket in enumerate(ticket_data['ticket']):
        ticket = "".join(ticket.split(" "))
        if ticket.find('免费') >= 0:
            ticket_data['ticket'][i] = 0
        elif "人民币" in ticket:
            ticket_data['ticket'][i] = int(re.findall(r"(\d+)人民币", ticket)[0])
        elif "元" in ticket:
            ticket_data['ticket'][i] = int(re.findall(r"(\d+)元", ticket)[0])
        elif "¥" in ticket:
            ticket_data['ticket'][i] = int(re.findall(r"¥(\d+)", ticket)[0])
        elif "￥" in ticket:
            ticket_data['ticket'][i] = int(re.findall(r"￥(\d+)", ticket)[0])
        elif "无需门票" in ticket or "不需要门票" in ticket:
            ticket_data['ticket'][i] = 0
        elif '人均:' in ticket or '/人' in ticket:
            ticket_data['ticket'][i] = int(re.findall(r"(\d+)", ticket)[0])
        elif '成人票' in ticket:
            ticket_data['ticket'][i] = int(re.findall(r"(\d+)", ticket)[0])
        elif '.' in ticket:
            ticket_data['ticket'][i] = int(ticket.split('.')[0])
    for i, ticket in enumerate(ticket_data.ticket):
        if isinstance(ticket, str):
            ticket_data.drop(i, inplace=True)
    top10 = ticket_data.sort_values(by='ticket', ascending=False).head(10)
    free = ticket_data.sort_values(by='ticket').head(10)
    price_bar1 = Bar('价格最高的景点', width=1000, title_pos='center', title_top='bottom')
    price_bar2 = Bar('免费景点', width=1000, title_pos='center', title_top='bottom')
    price_bar1.add('', top10['title'], top10['ticket'], yaxis_name='价格', yaxis_name_pos='end', xaxis_rotate=30,
                   is_label_show=True)
    price_bar2.add('', free['title'], free['ticket'], xaxis_rotate=30,
                   is_label_show=True)
    context = dict(
        echart1=price_bar1.render_embed(),
        echart2=price_bar2.render_embed(),
        host=REMOTE_HOST,
        script_list=price_bar1.get_js_dependencies()
    )
    return render(request, 'mysite/spot3.html', context)


def spot_page_fourth(request):
    spot = pd.read_csv('../data/spot.csv')
    gt_threehours = spot[spot.time == '3小时以上'].head(10)
    onehour = spot[spot.time == '1小时以下'].head(10)
    threehours = spot[spot.time == '1-3小时'].head(10)
    values = [1] * 10
    worldcloud1 = WordCloud(width=400, height=200)
    worldcloud1.add("", gt_threehours.title, values, word_size_range=[15, 20], shape='triangle')
    worldcloud2 = WordCloud(width=400, height=200)
    worldcloud2.add("", onehour.title, values, word_size_range=[15, 20], shape='triangle')
    worldcloud3 = WordCloud(width=400, height=200)
    worldcloud3.add("", threehours.title, values, word_size_range=[15, 20], shape='triangle')
    context = dict(
        echart1=worldcloud1.render_embed(),
        echart2=worldcloud2.render_embed(),
        echart3=worldcloud3.render_embed(),
        host=REMOTE_HOST,
        script_list=worldcloud1.get_js_dependencies()
    )
    return render(request, 'mysite/spot4.html', context)


def spot_page_fifth(request):
    spot = pd.read_csv('../data/spot.csv')
    position_data = spot.dropna(subset=['position'])
    position_data.index = pd.RangeIndex(len(position_data.index))
    position_data.index = range(len(position_data.index))
    for i, position in enumerate(position_data['position']):
        if "杭州市" in position:
            position_data['position'][i] = position.replace('杭州市', '')
        if "杭州" in position_data['position'][i]:
            position_data['position'][i] = position_data['position'][i].replace('杭州', '')
        if "浙江省" in position_data['position'][i]:
            position_data['position'][i] = position_data['position'][i].replace('浙江省', '')
        if "浙江" in position_data['position'][i]:
            position_data['position'][i] = position_data['position'][i].replace('浙江', '')
        if "中国" in position_data['position'][i]:
            position_data['position'][i] = position_data['position'][i].replace('中国', '')
        if "区" in position_data['position'][i]:
            position_data['position'][i] = position_data['position'][i].split('区')[0] + "区"
        if "县" in position_data['position'][i]:
            position_data['position'][i] = position_data['position'][i].split('县')[0] + "县"
        if "市" in position_data['position'][i]:
            position_data['position'][i] = position_data['position'][i].split('市')[0] + "市"
        if "西湖" in position_data['position'][i]:
            position_data['position'][i] = "西湖区"
        if "千岛" in position_data['position'][i]:
            position_data['position'][i] = "淳安县"
    for i, position in enumerate(position_data['position']):
        if ("市" not in position_data['position'][i] and "县" not in position_data['position'][i] and "区" not in
            position_data['position'][i]) or len(position_data['position'][i]) != 3:
            position_data.drop(i, inplace=True)
    top6 = position_data.groupby('position').count().sort_values(by='title', ascending=False).head(6)
    pie = Pie('各区县的景点分布', width='800px', height='600px', title_pos='center', title_top='bottom')
    pie.add('', top6.index, top6['title'], is_label_show=True)
    context = dict(
        echart=pie.render_embed(),
        host=REMOTE_HOST,
        script_list=pie.get_js_dependencies()
    )
    return render(request, 'mysite/spot5.html', context)


def house_page_first(request):
    # 杭州市各区房源数量
    house = pd.read_csv('../data/house.csv')
    region_info = house.groupby('region').title.count().sort_values(ascending=False)
    region_bar = Bar('杭州市各区房源数量', width='1000px', title_pos='center', title_top='bottom')
    region_bar.add('数量', region_info.index, region_info.values, is_label_show=True, bar_category_gap='30%')

    # 房源朝向统计
    orient_data = house.copy()
    orient_data['orient'] = orient_data['orient'].map(lambda x: x.split(' ')[0])
    orient_list = ['朝北', '朝南', '朝东', '朝西', '朝西南', '朝东南', '朝东北', '朝西北']
    orient_data = orient_data[orient_data.orient.isin(['朝北', '朝南', '朝东', '朝西', '朝西南', '朝东南', '朝东北', '朝西北'])]
    orient_data['orient'] = orient_data['orient'].astype('category')
    orient_data['orient'].cat.set_categories(orient_list, inplace=True)
    orient_info = orient_data.groupby('orient').title.count()
    orient_pie = Pie('房屋朝向', width='1000px', title_pos='center', title_top='bottom')
    orient_pie.add('数量', orient_info.index, orient_info.values, is_label_show=True)

    # 租赁方式
    house_data = house[house['house'].isin(['整租', '合租'])]
    house_info = house_data.groupby('house').title.count().sort_values(ascending=False)
    house_bar = Bar('租赁方式', width='800px', title_pos='center', title_top='bottom')
    house_bar.add('数量', house_info.index, house_info.values, is_label_show=True)

    # 户型
    type_data = house.groupby('type').title.count().sort_values(ascending=False)
    type_info = type_data[type_data.values >= 20]
    type_pie = Pie('户型', width='1000px', height='800px', title_pos='center', title_top='bottom')
    type_pie.add('数量', type_info.index, type_info.values, radius=[10, 50], is_label_show=True, legend_orient="vertical",
                 legend_pos="right")
    context = dict(
        echart1=region_bar.render_embed(),
        echart2=orient_pie.render_embed(),
        echart3=house_bar.render_embed(),
        echart4=type_pie.render_embed(),
        host=REMOTE_HOST,
        script_list=region_bar.get_js_dependencies(),
    )
    return render(request, 'mysite/house1.html', context)


def house_page_second(request):
    house = pd.read_csv('../data/house.csv')
    # 杭州市整体租房房源均价
    price_data = house.dropna(subset=['price'])
    price_data[['price']] = price_data[['price']].astype(int)
    price_range = list(range(0, 7501, 500))
    price_range.append(13000)
    price_data['range'] = pd.cut(price_data.price, price_range, right=True)
    price_data_range = price_data.groupby('range').title.count()
    x_range = ['(0, 500]', '(500, 1000]', '(1000, 1500]', '(1500, 2000]', '(2000, 2500]', '(2500, 3000]',
               '(3000, 3500]', '(3500, 4000]', '(4000, 4500]', '(4500, 5000]', '(5000, 5500]', '(5500, 6000]',
               '(6000, 6500]', '(6500, 7000]', '(7000, 7500]', '>7500']
    line1 = Line("整体租房价格分布", width='1200px', title_pos='center', title_top='bottom')
    line1.add('', x_range, price_data_range.values, xaxis_rotate=30, yaxis_name='数量', yaxis_name_pos='end')
    area_price_data = house.dropna(subset=['area'])
    area_price_data['area'] = area_price_data['area'].map(lambda x: x.split('㎡')[0])
    area_price_data[['area']] = area_price_data[['area']].astype(int)
    area_price_info = area_price_data.groupby('area').price.mean().map(lambda x: round(x)).sort_index()
    line2 = Line("每平方米平均价格", width='1200px', title_pos='center', title_top='bottom')
    line2.add('', area_price_info.index, area_price_info.values, yaxis_name='价格', yaxis_name_pos='end',
              xaxis_rotate=30, is_datazoom_show=True)
    region_price = house.groupby('region').price.mean().sort_values(ascending=False)
    line3 = Line("各区县租房房价均价", width='1200px', title_pos='center', title_top='bottom')
    line3.add('', region_price.index, region_price.values, yaxis_name='价格', yaxis_name_pos='end')
    area_price_data['price_per_square'] = area_price_data['price'] / area_price_data['area']
    area_price_per_info = area_price_data.groupby('region').price_per_square.mean().sort_values(ascending=False)
    line4 = Line("各区县租房每平方米均价", width='1200px', title_pos='center', title_top='bottom')
    line4.add('', area_price_per_info.index, area_price_per_info.values, yaxis_name='价格', yaxis_name_pos='end')
    context = dict(
        echart1=line1.render_embed(),
        echart2=line2.render_embed(),
        echart3=line3.render_embed(),
        echart4=line4.render_embed(),
        host=REMOTE_HOST,
        script_list=line1.get_js_dependencies()
    )
    return render(request, 'mysite/house2.html', context)


def weather_page_first(request):
    weather = pd.read_csv('./data/weather.csv')
    line = Line("历史天气温度(2011年1月1日至2018年10月31日)", width=1200, title_pos='center', title_top='bottom')
    line.add("一天中最高温度", weather.date, weather['max'], is_datazoom_show=True)
    line.add("一天中最低温度", weather.date, weather['min'], is_datazoom_show=True)
    max_max_all = weather.sort_values(by='max', ascending=False).head(3)
    max_max = [row for index, row in max_max_all.iterrows()]
    min_min_all = weather.sort_values(by='min').head(3)
    min_min = [row for index, row in min_min_all.iterrows()]
    above_t = [i for i in range(40, 32, -1)]
    below_t = [i for i in range(-3, 5, 1)]
    above_count = list(map(lambda i: weather[weather['max'] >= i].date.count(), above_t))
    below_count = list(map(lambda i: weather[weather['min'] <= i].date.count(), below_t))
    context = dict(
        echart=line.render_embed(),
        host=REMOTE_HOST,
        script_list=line.get_js_dependencies(),
        max_max=max_max,
        min_min=min_min,
        above_t=above_t,
        below_t=below_t,
        above_count=above_count,
        below_count=below_count
    )
    return render(request, 'mysite/weather1.html', context)


def weather_page_second(request):
    weather = pd.read_csv('./data/weather.csv')
    weather_data = weather.groupby('weather').weather.count().sort_values(ascending=False)
    weather_data.loc['其他'] = weather_data[weather_data.values <= 15].count()
    weather_data = weather_data[weather_data.values > 15]
    weather_pie = Pie('各种天气所占比例', width='1200px', height='700px', title_pos='center', title_top='bottom')
    weather_pie.add('数量', weather_data.index, weather_data.values, radius=[40, 75], label_text_color=None,
                    is_label_show=True, legend_orient="vertical", legend_pos="left")
    weather_data_transform = weather.copy()
    for i, w in enumerate(weather_data_transform.weather):
        if w.find('雨') >= 0:
            weather_data_transform.weather[i] = '雨'
    weather_data_transform['date'] = weather_data_transform['date'].map(lambda x: x.split('-')[0])
    grouped = weather_data_transform.groupby(['date', 'weather']).weather.count()
    rain_data = grouped.unstack()['雨']
    line = Line("每年下雨的天数", width=800, title_pos='center', title_top='bottom')
    line.add('', rain_data.index, rain_data.values, yaxis_name='天数', yaxis_name_pos='end')
    context = dict(
        echart1=weather_pie.render_embed(),
        echart2=line.render_embed(),
        host=REMOTE_HOST,
        script_list=weather_pie.get_js_dependencies(),
    )
    return render(request, 'mysite/weather2.html', context)


def weather_page_third(request):
    weather = pd.read_csv('./data/weather.csv')
    direction_data = weather.groupby('direction').direction.count().sort_values(ascending=False)
    direction_data.loc['其他'] = direction_data[direction_data.values <= 2].count()
    direction_data = direction_data[direction_data.values > 2]
    direction_pie = Pie('各种风向所占比例', width='1000px', height='600px', title_pos='center', title_top='bottom')
    direction_pie.add('数量', direction_data.index, direction_data.values, label_text_color=None, is_label_show=True,
                      legend_orient="vertical", legend_pos="left")
    force_data = weather.groupby('power').direction.count().sort_values(ascending=False)
    force_data.loc['其他'] = force_data[force_data.values <= 2].count()
    force_data = force_data[force_data.values > 2]
    force_pie = Pie('各种风力所占比例', width='1000px', height='750px', title_pos='center', title_top='bottom')
    force_pie.add('数量', force_data.index, force_data.values, label_text_color=None, is_label_show=True,
                  legend_orient="vertical", legend_pos="left")
    context = dict(
        echart1=direction_pie.render_embed(),
        echart2=force_pie.render_embed(),
        host=REMOTE_HOST,
        script_list=direction_pie.get_js_dependencies(),
    )
    return render(request, "mysite/weather3.html", context)
