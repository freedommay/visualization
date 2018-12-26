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
    type = [i for i in type_info.index]
    type_count = [i for i in type_info.values]
    type_bar = Bar('各菜系商家数量', width='1000px', title_pos='center', title_top='bottom')
    type_bar.add('数量', type, type_count, is_label_show=True, bar_category_gap='30%', xaxis_rotate=50)
    zone_info = food.groupby('zone').name.count().sort_values(ascending=False).head(15)
    zone = [i for i in zone_info.index]
    zone_count = [i for i in zone_info.values]
    zone_bar = Bar('各商区商家数量', title_pos='center', title_top='bottom')
    zone_bar.add('数量', zone, zone_count, is_label_show=True, xaxis_rotate=30)
    star_list = ['二星商户', '三星商户', '准四星商户', '四星商户', '准五星商户', '五星商户']
    star_data = food[food.star.isin(['二星商户', '三星商户', '准四星商户', '四星商户', '准五星商户', '五星商户'])]
    star_data['star'] = star_data['star'].astype('category')
    star_data['star'].cat.set_categories(star_list, inplace=True)
    star_data.sort_values('star', inplace=True)
    star_info = star_data.groupby('star').name.count()
    star = [i for i in star_info.index]
    star_count = [i for i in star_info.values]
    star_pie = Pie('商家星级比例', title_pos='center', title_top='bottom')
    star_pie.add('数量', star, star_count, is_label_show=True)
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
    price = [i for i in price_data.price]
    price_data_high = price_data.sort_values(by='price', ascending=False).head(5)
    highs = [row for index, row in price_data_high.iterrows()]
    price_data_high_name = [i for i in price_data_high.name]
    price_data_high_price = [i for i in price_data_high.price]
    price_data_high_bar = Bar("人均消费水平最高的五家店铺", width='600px', title_pos='center', title_top='bottom')
    price_data_high_bar.add('', price_data_high_name, price_data_high_price, xaxis_rotate=10, bar_category_gap='30%',
                            yaxis_name='元', yaxis_name_pos='end')
    price_data_low = price_data.sort_values(by='price').head(5)
    lows = [row for index, row in price_data_low.iterrows()]
    price_data_low_name = [i for i in price_data_low.name]
    price_data_low_price = [i for i in price_data_low.price]
    price_data_low_bar = Bar("人均消费水平最低的五家店铺", width='600px', title_pos='center', title_top='bottom')
    price_data_low_bar.add('', price_data_low_name, price_data_low_price, xaxis_rotate=10, bar_category_gap='30%',
                           yaxis_name='元', yaxis_name_pos='end')
    price_data_sub = price_data[price_data.price < 500]
    price_info = price_data_sub.groupby('price').name.count()
    price_sub = [i for i in price_info.index]
    price_count = [i for i in price_info.values]
    price_limit = [i for i in price_info.index]
    price_scatter = Scatter("人均消费(<=500元)", title_pos='center', title_top='bottom')
    price_scatter.add('', price_sub, price_count, extra_data=price_limit, is_visualmap=True, xaxis_name='人均/元',
                      xaxis_name_pos='end', yaxis_name='店铺数量/家', yaxis_name_pos='end', visual_range=[0, 500])
    boxplot = Boxplot('人均消费箱型图', width='400px', title_pos='center', title_top='bottom')
    x_axis = ['']
    boxplot.add('', x_axis, boxplot.prepare_data([price]), yaxis_name='元', yaxis_name_pos='end')
    price_range = list(range(0, 201, 20))
    price_range.append(13000)
    price_data['range'] = pd.cut(price_data.price, price_range, right=True)
    price_data_range = price_data.groupby('range').name.count()
    x_range = ['(0, 20]', '(20, 40]', '(40, 60]', '(60, 80]', '(80, 100]', '(100, 120]',
               '(120, 140]', '(140, 160]', '(160, 180]', '(180, 200]', '>200']
    range_count = [i for i in price_data_range.values]
    line = Line("分区间人均消费水平", width='600px', title_pos='center', title_top='bottom')
    line.add('', x_range, range_count, xaxis_rotate=30)
    context = dict(
        echart1=price_scatter.render_embed(),
        echart2=boxplot.render_embed(),
        echart3=line.render_embed(),
        echart4=price_data_high_bar.render_embed(),
        echart5=price_data_low_bar.render_embed(),
        highs=highs,
        lows=lows,
        price_data_high=price_data_high,
        price_data_high_name=price_data_high_name,
        price_data_high_price=price_data_high_price,
        host=REMOTE_HOST,
        script_list=price_scatter.get_js_dependencies()
    )
    return render(request, 'mysite/food2.html', context)


def food_page_third(request):
    food = pd.read_csv('../data/food.csv')
    comment_data = food.dropna(subset=['comment'])
    comment_data_most = comment_data.sort_values(by='comment', ascending=False).head(5)
    popular_shop = [row for index, row in comment_data_most.iterrows()]
    comment = [i for i in comment_data_most.comment]
    name = [i for i in comment_data_most.name]
    comment_bar = Bar("'网红'店铺", width='600px', title_pos='center', title_top='bottom')
    comment_bar.add('', name, comment, xaxis_rotate=15, is_label_show=True)
    comment_data['name'] = comment_data['name'].map(lambda x: x.split('(')[0])
    shop = comment_data.groupby('name').name.count().sort_values(ascending=False).head(15)
    shop_name = [i for i in shop.index]
    shop_count = [i for i in shop.values]
    shop_bar = Bar("分店最多的店铺", title_pos='center', title_top='bottom')
    shop_bar.add('', shop_name, shop_count, xaxis_rotate=30, is_label_show=True)
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
    score_data_name = [i for i in score_data.index]
    score_data_taste = [i for i in score_data['taste']]
    score_data_env = [i for i in score_data['env']]
    score_data_service = [i for i in score_data['service']]
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
    recommend_value = [i for i in recommend_data.values]
    worldcloud = WordCloud(width=1000, height=800)
    worldcloud.add("", recommend_name, recommend_value, word_size_range=[10, 100], shape='star')
    context = dict(
        echart=worldcloud.render_embed(),
        host=REMOTE_HOST,
        script_list=worldcloud.get_js_dependencies()
    )
    return render(request, 'mysite/food5.html', context)


def spot_page_first(request):
    spot = pd.read_csv('../data/spot.csv')
    spot_sub_data = spot.head(200)
    spot_title = [i for i in spot_sub_data.title]
    spot_value = [1] * 200
    worldcloud = WordCloud(width=1000, height=800)
    worldcloud.add("", spot_title, spot_value, word_size_range=[10, 10])
    context = dict(
        echart=worldcloud.render_embed(),
        host=REMOTE_HOST,
        script_list=worldcloud.get_js_dependencies()
    )
    return render(request, 'mysite/spot1.html', context)


def house_page_first(request):
    return render(request, 'mysite/house1.html')


def weather_page_first(request):
    weather = pd.read_csv('./data/weather.csv')
    date = [i for i in weather.date]
    max_temp = [i for i in weather['max']]
    min_temp = [i for i in weather['min']]
    line = Line("历史天气温度(2011年1月1日至2018年10月31日)", width=1200, title_pos='center', title_top='bottom')
    line.add("一天中最高温度", date, max_temp, is_datazoom_show=True)
    line.add("一天中最低温度", date, min_temp, is_datazoom_show=True)
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
    weather_category = [i for i in weather_data.index]
    weather_count = [i for i in weather_data.values]
    weather_pie = Pie('各种天气所占比例', width='1200px', height='700px', title_pos='center', title_top='bottom')
    weather_pie.add('数量', weather_category, weather_count, radius=[40, 75], label_text_color=None,
                    is_label_show=True, legend_orient="vertical", legend_pos="left")
    weather_data_transform = weather.copy()
    for i, w in enumerate(weather_data_transform.weather):
        if w.find('雨') >= 0:
            weather_data_transform.weather[i] = '雨'
    weather_data_transform['date'] = weather_data_transform['date'].map(lambda x: x.split('-')[0])
    grouped = weather_data_transform.groupby(['date', 'weather']).weather.count()
    rain_data = grouped.unstack()['雨']
    year = [i for i in rain_data.index]
    rain_count = [i for i in rain_data.values]
    line = Line("每年下雨的天数", width=800, title_pos='center', title_top='bottom')
    line.add('', year, rain_count)
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
    direction = [i for i in direction_data.index]
    direction_count = [i for i in direction_data.values]
    direction_pie = Pie('风向所占比例', width='1000px', height='600px', title_pos='center', title_top='bottom')
    direction_pie.add('数量', direction, direction_count, label_text_color=None, is_label_show=True,
                      legend_orient="vertical", legend_pos="left")
    context = dict(
        echart1=direction_pie.render_embed(),
        host=REMOTE_HOST,
        script_list=direction_pie.get_js_dependencies(),
    )
    return render(request, "mysite/weather3.html", context)
