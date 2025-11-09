from flask import Flask, render_template, request, jsonify
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Line, Radar, Scatter, Gauge, TreeMap
from pyecharts.commons.utils import JsCode
import json
import os


app = Flask(__name__)

# 全局变量存储数据
df = None
military_df = None

# 文件路径配置
EXPENDITURE_EXCEL_PATH = "SIPRI Military Expenditure Database.xlsx"
MILITARY_DATA_EXCEL_PATH = "military_data_2023.xlsx"


def init_data():
    """初始化数据"""
    global df, military_df
    df = load_excel_data()
    military_df = load_military_data()


def load_excel_data():
    """从Excel文件加载军费支出数据"""
    try:
        if os.path.exists(EXPENDITURE_EXCEL_PATH):
            # 读取Excel文件，指定工作表名称
            df = pd.read_excel(EXPENDITURE_EXCEL_PATH, sheet_name='SIPRI Military Expenditure Data')
            print(f"成功从 {EXPENDITURE_EXCEL_PATH} 加载军费数据")
            print(f"数据列: {df.columns.tolist()}")
            print(f"数据行数: {len(df)}")

            # 筛选我们需要的六个国家
            target_countries = ['United States of America', 'China', 'India', 'Japan', 'Korea, South', 'Russia']
            df = df[df['Country'].isin(target_countries)]

            return df
        else:
            raise FileNotFoundError(f"军费数据文件 {EXPENDITURE_EXCEL_PATH} 不存在")

    except Exception as e:
        print(f"加载军费数据时出错: {e}")
        raise


def load_military_data():
    """从Excel文件加载军事力量数据"""
    try:
        if os.path.exists(MILITARY_DATA_EXCEL_PATH):
            # 读取Excel文件，指定工作表名称
            df = pd.read_excel(MILITARY_DATA_EXCEL_PATH, sheet_name='military_data_2023')
            print(f"成功从 {MILITARY_DATA_EXCEL_PATH} 加载军事力量数据")
            print(f"数据列: {df.columns.tolist()}")

            # 重命名列以匹配原有代码
            df = df.rename(columns={
                'country_name': 'country_name',
                'active_mil_personnel': 'active_mil_personnel',
                'reserve_mil_personnel': 'reserve_mil_personnel',
                'paramilitary': 'paramilitary',
                'air_force_personnel': 'air_force_personnel',
                'army_personnel': 'army_personnel',
                'navy_personnel': 'navy_personnel',
                'total_aircraft': 'total_aircraft',
                'aircrafts_ready': 'aircrafts_ready',
                'fighter_aircrafts': 'fighter_aircrafts',
                'attack_aircrafts': 'attack_aircrafts',
                'helicopters': 'helicopters',
                'attack_helicopters': 'attack_helicopters',
                'tanks': 'tanks',
                'self_propelled_artillery': 'self_propelled_artillery',
                'towed_artillery': 'towed_artillery',
                'rocket_artillery': 'rocket_artillery',
                'aircraft_carriers': 'aircraft_carriers',
                'destroyers': 'destroyers',
                'frigates': 'frigates',
                'corvettes': 'corvettes',
                'submarines': 'submarines',
                'patrol_vessels': 'patrol_vessels',
                'mine_warfare': 'mine_warfare',
                'power_index': 'power_index',
                'defense_budget_million_usd': 'defense_budget'
            })

            # 将defense_budget从百万美元转换为十亿美元
            df['defense_budget'] = df['defense_budget'] / 1000

            return df
        else:
            raise FileNotFoundError(f"军事数据文件 {MILITARY_DATA_EXCEL_PATH} 不存在")

    except Exception as e:
        print(f"加载军事力量数据时出错: {e}")
        raise


# 保留所有原有的图表创建函数
def create_military_expenditure_trend_chart(df):
    """创建1993-2024年六国军费动态变化图"""
    country_names = {
        'United States of America': '美国',
        'China': '中国',
        'India': '印度',
        'Japan': '日本',
        'Korea, South': '韩国',
        'Russia': '俄罗斯'
    }

    years = sorted(df['Year'].unique())

    line = (
        Line(init_opts=opts.InitOpts(width="100%", height="600px"))
        .add_xaxis([str(year) for year in years])
    )

    # 国家颜色配置
    country_colors = {
        'United States of America': '#dc3545',
        'China': '#198754',
        'India': '#fd7e14',
        'Japan': '#0dcaf0',
        'Korea, South': '#6f42c1',
        'Russia': '#ffc107'
    }

    # 为每个国家添加数据线
    for country in df['Country'].unique():
        if country in country_names:
            country_data = df[df['Country'] == country].sort_values('Year')
            # 将数据转换为十亿美元单位
            values_in_billions = [round(value / 1000, 1) for value in country_data['Value']]
            line.add_yaxis(
                series_name=country_names[country],
                y_axis=values_in_billions,
                is_smooth=True,
                symbol="circle",
                symbol_size=6,
                linestyle_opts=opts.LineStyleOpts(width=3),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=country_colors[country]),
            )

    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title="1993-2024年六国军费动态变化图",
            title_textstyle_opts=opts.TextStyleOpts(font_size=20, font_weight='bold')
        ),
        legend_opts=opts.LegendOpts(
            pos_top="10%",
            type_="scroll",
            page_button_position="end"
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            axis_pointer_type="cross"
        ),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=False,
            name="年份",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color="#666")
            )
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="军事支出 (十亿美元)",
            axislabel_opts=opts.LabelOpts(formatter="${value}B"),
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color="#666")
            ),
            splitline_opts=opts.SplitLineOpts(
                is_show=True,
                linestyle_opts=opts.LineStyleOpts(type_="dashed", opacity=0.3)
            )
        ),
        datazoom_opts=[
            opts.DataZoomOpts(
                type_="inside",
                range_start=0,
                range_end=100
            ),
            opts.DataZoomOpts(
                type_="slider",
                pos_bottom="5%",
                range_start=0,
                range_end=100
            )
        ],
    )

    return line.dump_options_with_quotes()


def create_personnel_composition_chart(military_df):
    """创建军事人员构成图 - 使用堆叠柱状图"""
    country_names = {
        'Japan': '日本',
        'South Korea': '韩国',
        'India': '印度',
        'China': '中国',
        'Russia': '俄罗斯',
        'United States': '美国'
    }

    countries = [country_names[name] for name in military_df['country_name']]

    # 准备数据（转换为万人）
    army_data = [row['army_personnel'] / 10000 for _, row in military_df.iterrows()]
    navy_data = [row['navy_personnel'] / 10000 for _, row in military_df.iterrows()]
    air_force_data = [row['air_force_personnel'] / 10000 for _, row in military_df.iterrows()]
    reserve_data = [row['reserve_mil_personnel'] / 10000 for _, row in military_df.iterrows()]
    paramilitary_data = [row['paramilitary'] / 10000 for _, row in military_df.iterrows()]

    bar = (
        Bar(init_opts=opts.InitOpts(width="100%", height="500px"))
        .add_xaxis(countries)
        .add_yaxis("陆军(万人)", army_data, stack="stack1", color="#5470c6")
        .add_yaxis("海军(万人)", navy_data, stack="stack1", color="#91cc75")
        .add_yaxis("空军(万人)", air_force_data, stack="stack1", color="#fac858")
        .add_yaxis("预备役(万人)", reserve_data, stack="stack1", color="#ee6666")
        .add_yaxis("准军事(万人)", paramilitary_data, stack="stack1", color="#73c0de")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="军事人员构成展示"),
            yaxis_opts=opts.AxisOpts(name="人员数量(万人)"),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="shadow"
            ),
            legend_opts=opts.LegendOpts(pos_top="10%"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
        )
    )

    return bar.dump_options_with_quotes()


def create_comprehensive_equipment_chart(military_df):
    """创建综合装备图 - 使用雷达图"""
    country_names = {
        'Japan': '日本', 'South Korea': '韩国', 'India': '印度',
        'China': '中国', 'Russia': '俄罗斯', 'United States': '美国'
    }

    countries = [country_names[name] for name in military_df['country_name']]

    # 装备类型 - 标准化数据
    equipment_types = ['坦克', '作战飞机', '预警机', '直升机', '武直','战略轰炸']

    equipment_data = {
        '坦克': military_df['tanks'].tolist(),
        '作战飞机': military_df['fightaircrafts'].tolist(),
        '预警机': military_df['aew'].tolist(),
        '直升机': military_df['helicopters'].tolist(),
        '武直': military_df['attack_helicopters'].tolist(),
        '战略轰炸':military_df['bombers'].tolist()
    }

    # 计算最大值
    max_values = {eq_type: max(equipment_data[eq_type]) * 1.2 for eq_type in equipment_types}

    radar = (
        Radar(init_opts=opts.InitOpts(width="100%", height="600px"))
        .add_schema(
            schema=[
                opts.RadarIndicatorItem(name=eq_type, max_=max_values[eq_type])
                for eq_type in equipment_types
            ],
            splitarea_opt=opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=0.1)),
        )
    )

    colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#9a60b4']

    for idx, country in enumerate(countries):
        values = [equipment_data[eq_type][idx] for eq_type in equipment_types]
        radar.add(
            series_name=country,
            data=[values],
            linestyle_opts=opts.LineStyleOpts(width=2),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.1),
            color=colors[idx]
        )

    radar.set_global_opts(
        title_opts=opts.TitleOpts(title="陆军/空军装备数量展示"),
        legend_opts=opts.LegendOpts(pos_right="5%", orient="vertical"),
    )
    radar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

    return radar.dump_options_with_quotes()

def create_artillery_comparison_chart(military_df):
    """创建炮兵装备数量图 - 使用堆叠柱状图"""
    country_names = {
        'Japan': '日本', 'South Korea': '韩国', 'India': '印度',
        'China': '中国', 'Russia': '俄罗斯', 'United States': '美国'
    }

    countries = [country_names[name] for name in military_df['country_name']]

    bar = (
        Bar(init_opts=opts.InitOpts(width="100%", height="500px"))
        .add_xaxis(countries)
        .add_yaxis("自行火炮", military_df['self_propelled_artillery'].tolist(),
                   stack="stack1", color="#5470c6")
        .add_yaxis("牵引火炮", military_df['towed_artillery'].tolist(),
                   stack="stack1", color="#91cc75")
        .add_yaxis("火箭炮", military_df['rocket_artillery'].tolist(),
                   stack="stack1", color="#fac858")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="炮兵装备数量展示"),
            yaxis_opts=opts.AxisOpts(name="装备数量"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            legend_opts=opts.LegendOpts(pos_top="10%"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )

    return bar.dump_options_with_quotes()


def create_navy_comprehensive_chart(military_df):
    """创建海军综合图 - 使用水平堆叠条形图"""
    country_names = {
        'Japan': '日本', 'South Korea': '韩国', 'India': '印度',
        'China': '中国', 'Russia': '俄罗斯', 'United States': '美国'
    }

    countries = [country_names[name] for name in military_df['country_name']]

    bar = (
        Bar(init_opts=opts.InitOpts(width="100%", height="600px"))
        .add_xaxis(countries)
        .add_yaxis("航空母舰", military_df['aircraft_carriers'].tolist(),
                   stack="stack1", color="#54A0FF")
        .add_yaxis("巡洋舰", military_df['cruisers'].tolist(),
                   stack="stack1", color="#96CEA5")
        .add_yaxis("驱逐舰", military_df['destroyers'].tolist(),
                   stack="stack1", color="#FF6B6B")
        .add_yaxis("护卫舰", military_df['frigates'].tolist(),
                   stack="stack1", color="#4ECDC4")
        .add_yaxis("潜艇", military_df['submarines'].tolist(),
                   stack="stack1", color="#96CEB4")
        .reversal_axis()
        .set_global_opts(
            title_opts=opts.TitleOpts(title="海军主力舰艇构成"),
            xaxis_opts=opts.AxisOpts(name="数量"),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=0)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="shadow"
            ),
            legend_opts=opts.LegendOpts(pos_top="5%"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False)
        )
    )

    return bar.dump_options_with_quotes()


def create_detailed_readiness_dashboard(military_df):
    """创建详细战备率仪表盘 - 显示所有国家的战备率对比"""
    country_names = {
        'Japan': '日本', 'South Korea': '韩国', 'India': '印度',
        'China': '中国', 'Russia': '俄罗斯', 'United States': '美国'
    }

    # 准备数据
    data = []
    for _, row in military_df.iterrows():
        country = country_names[row['country_name']]
        if row['total_aircraft'] > 0:
            readiness_rate = (row['aircrafts_ready'] / row['total_aircraft']) * 100
        else:
            readiness_rate = 0

        data.append({
            "name": country,
            "value": round(readiness_rate, 1)
        })

    pie = (
        Pie(init_opts=opts.InitOpts(width="100%", height="600px"))
        .add(
            series_name="空军战备率",
            data_pair=[(item["name"], item["value"]) for item in data],
            radius=["30%", "75%"],
            center=["50%", "50%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(
                formatter="{b}: {c}%",
                font_size=12
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各国空军战备率分布",
                subtitle="环形图展示各国战备率占比"
            ),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_left="left",
                pos_top="middle"
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{a}<br/>{b}: {c}%"
            ),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                formatter="{b}: {c}%",
                font_size=12
            )
        )
    )

    return pie.dump_options_with_quotes()


def create_military_power_bubble_chart(military_df):
    """创建军力综合对比气泡图 - 带不同颜色"""
    country_names = {
        'Japan': '日本', 'South Korea': '韩国', 'India': '印度',
        'China': '中国', 'Russia': '俄罗斯', 'United States': '美国'
    }

    # 国家颜色配置 - 鲜明的不同颜色
    country_colors = {
        '日本': '#FF6B6B',
        '韩国': '#9B59B6',
        '印度': '#FFA726',
        '中国': '#2ECC71',
        '俄罗斯': '#F1C40F',
        '美国': '#3498DB'
    }

    # 准备数据
    data = []
    for _, row in military_df.iterrows():
        country = country_names[row['country_name']]
        power_index = float(row['power_index'])
        defense_budget = float(row['defense_budget'])
        total_troops = (float(row['active_mil_personnel']) + float(row['reserve_mil_personnel'])) / 10000

        tooltip_text = f"{country}<br/>军力指数: {power_index:.4f}<br/>军费预算: ${defense_budget:.1f}B<br/>总兵力: {total_troops:.1f}万人"

        data.append({
            "name": country,
            "value": [power_index, defense_budget, total_troops],
            "tooltip": tooltip_text,
            "itemStyle": {
                "color": country_colors[country],
                "borderColor": "#333",
                "borderWidth": 1
            },
            "symbolSize": total_troops * 0.8
        })

    scatter = (
        Scatter(init_opts=opts.InitOpts(width="100%", height="600px"))
        .add_xaxis(xaxis_data=[])
        .add_yaxis(
            series_name="",
            y_axis=[],
            symbol_size=JsCode("function(data){return data[2] * 0.8;}")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="军力综合展示",
                subtitle="\n气泡大小代表总兵力规模，位置反映军费与军力指数关系"
            ),
            xaxis_opts=opts.AxisOpts(
                name="军力指数\n（越低越强）",
                type_="value",
                min_=0.06,
                max_=0.18,
                is_inverse=True,
            ),
            yaxis_opts=opts.AxisOpts(
                name="军费预算（十亿美元）",
                type_="value",
                min_=0,
                max_=1000,
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter=JsCode("function(params){return params.data.tooltip;}")
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=True,
                position="right",
                formatter="{b}",
                font_size=12,
                color="#333",
                font_weight="bold"
            )
        )
    )

    scatter.options["series"][0]["data"] = data

    return scatter.dump_options_with_quotes()


def create_pla_treemap_chart(military_df):
    """创建解放军人员装备矩阵树图"""
    # 获取中国数据
    china_data = military_df[military_df['country_name'] == 'China'].iloc[0]

    # 构建数据，对人员数据进行缩放，使其与装备数据在同一量级
    def scale_personnel(value):
        """将人员数量缩放到与装备相近的量级"""
        return value / 1000  # 将人员数量除以1000

    def scale_small_equipment(value):
        """对小数量装备进行放大"""
        if value < 100:
            return value * 10  # 对小数量装备放大10倍以便显示
        return value

    # 构建数据，分组显示
    data = [
        # 人员组
        {
            "name": "人员构成",
            "value": 1,  # 父节点用固定值
            "children": [
                {"value": scale_personnel(int(china_data['active_mil_personnel'])),
                 "name": f"现役人员\n{int(china_data['active_mil_personnel']):,}"},
                {"value": scale_personnel(int(china_data['reserve_mil_personnel'])),
                 "name": f"预备役\n{int(china_data['reserve_mil_personnel']):,}"},
                {"value": scale_personnel(int(china_data['paramilitary'])),
                 "name": f"准军事\n{int(china_data['paramilitary']):,}"},
                {"value": scale_personnel(int(china_data['army_personnel'])),
                 "name": f"陆军\n{int(china_data['army_personnel']):,}"},
                {"value": scale_personnel(int(china_data['navy_personnel'])),
                 "name": f"海军\n{int(china_data['navy_personnel']):,}"},
                {"value": scale_personnel(int(china_data['air_force_personnel'])),
                 "name": f"空军\n{int(china_data['air_force_personnel']):,}"},
            ]
        },
        # 空军装备组
        {
            "name": "空军装备",
            "value": 1,
            "children": [
                {"value": int(china_data['fighter_aircrafts']),
                 "name": f"战斗机\n{int(china_data['fighter_aircrafts'])}"},
                {"value": int(china_data['attack_aircrafts']),
                 "name": f"攻击机\n{int(china_data['attack_aircrafts'])}"},
                {"value": int(china_data['helicopters']), "name": f"直升机\n{int(china_data['helicopters'])}"},
                {"value": scale_small_equipment(int(china_data['attack_helicopters'])),
                 "name": f"攻击直升机\n{int(china_data['attack_helicopters'])}"},
            ]
        },
        # 陆军装备组
        {
            "name": "陆军装备",
            "value": 1,
            "children": [
                {"value": int(china_data['tanks']), "name": f"坦克\n{int(china_data['tanks'])}"},
                {"value": int(china_data['self_propelled_artillery']),
                 "name": f"自行火炮\n{int(china_data['self_propelled_artillery'])}"},
                {"value": int(china_data['towed_artillery']),
                 "name": f"牵引火炮\n{int(china_data['towed_artillery'])}"},
                {"value": int(china_data['rocket_artillery']),
                 "name": f"火箭炮\n{int(china_data['rocket_artillery'])}"},
            ]
        },
        # 海军装备组
        {
            "name": "海军装备",
            "value": 1,
            "children": [
                {"value": scale_small_equipment(int(china_data['aircraft_carriers'])),
                 "name": f"航空母舰\n{int(china_data['aircraft_carriers'])}"},
                {"value": int(china_data['destroyers']), "name": f"驱逐舰\n{int(china_data['destroyers'])}"},
                {"value": int(china_data['frigates']), "name": f"护卫舰\n{int(china_data['frigates'])}"},
                {"value": int(china_data['corvettes']), "name": f"护卫艇\n{int(china_data['corvettes'])}"},
                {"value": int(china_data['submarines']), "name": f"潜艇\n{int(china_data['submarines'])}"},
                {"value": int(china_data['patrol_vessels']), "name": f"巡逻艇\n{int(china_data['patrol_vessels'])}"},
                {"value": int(china_data['mine_warfare']), "name": f"扫雷舰\n{int(china_data['mine_warfare'])}"},
            ]
        }
    ]

    print(f"树图数据结构构建完成")

    # 创建矩阵树图
    treemap = (
        TreeMap(init_opts=opts.InitOpts(width="100%", height="600px"))
        .add(
            series_name="解放军构成",
            data=data,
            levels=[
                {
                    "itemStyle": {
                        "borderColor": "#555",
                        "borderWidth": 2,
                        "gapWidth": 2
                    },
                    "upperLabel": {
                        "show": True,
                        "height": 30,
                        "color": "#fff",
                        "backgroundColor": "rgba(0,0,0,0.3)"
                    }
                },
                {
                    "itemStyle": {
                        "borderColor": "#777",
                        "borderWidth": 1,
                        "gapWidth": 1
                    },
                    "emphasis": {
                        "itemStyle": {
                            "borderColor": "#ddd",
                            "borderWidth": 2
                        }
                    }
                }
            ]
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="解放军军事力量构成分析",
                subtitle="矩形大小反映相对数量规模（人员数据已缩放）"
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}"
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(
                position="inside",
                formatter="{b}",
                font_size=12,
                color="#fff"
            )
        )
    )

    return treemap.dump_options_with_quotes()

def get_statistics(df):
    """获取统计数据"""
    current_year = 2024
    current_data = df[df['Year'] == current_year]
    total_expenditure = current_data['Value'].sum()
    avg_expenditure = current_data['Value'].mean()
    max_country = current_data.loc[current_data['Value'].idxmax(), 'Country']
    max_value = current_data['Value'].max()
    country_names = {
        'United States of America': '美国',
        'China': '中国',
        'India': '印度',
        'Japan': '日本',
        'Korea, South': '韩国',
        'Russia': '俄罗斯'
    }
    return {
        'total_expenditure': total_expenditure,
        'avg_expenditure': avg_expenditure,
        'max_country': country_names.get(max_country, max_country),
        'max_value': max_value,
        'current_year': current_year
    }


@app.route('/')
def index():
    init_data()
    # 精选图表
    expenditure_options = create_military_expenditure_trend_chart(df)
    personnel_options = create_personnel_composition_chart(military_df)
    equipment_options = create_comprehensive_equipment_chart(military_df)
    artillery_options = create_artillery_comparison_chart(military_df)
    navy_options = create_navy_comprehensive_chart(military_df)
    readiness_gauge_options = create_detailed_readiness_dashboard(military_df)
    power_bubble_options = create_military_power_bubble_chart(military_df)
    pla_treemap_options = create_pla_treemap_chart(military_df)  # 新增的矩阵树图
    stats = get_statistics(df)
    return render_template(
        'index.html',
        expenditure_options=expenditure_options,
        personnel_options=personnel_options,
        equipment_options=equipment_options,
        artillery_options=artillery_options,
        navy_options=navy_options,
        air_force_options=readiness_gauge_options,
        power_bubble_options=power_bubble_options,
        pla_treemap_options=pla_treemap_options,  # 新增
        stats=stats
    )


@app.route('/search', methods=['POST'])
def search():
    """处理搜索请求"""
    search_query = request.json.get('query', '').lower().strip()

    if not search_query:
        return jsonify({'show_all': True})

    # 定义图表关键词映射
    chart_keywords = {
        'expenditure': ['军费', '支出', '经费', '预算', 'money', 'expenditure', 'spending', 'trend', '趋势'],
        'personnel': ['人员', '军人', '部队', '兵力', '人事', 'personnel', 'troops', 'soldiers', '人力'],
        'equipment': ['装备', '武器', '坦克', '飞机', 'equipment', 'weapons', 'tanks', 'aircraft', '雷达'],
        'artillery': ['炮兵', '火炮', 'artillery', 'cannon', '自行火炮', '牵引火炮', '火箭炮'],
        'navy': ['海军', '舰艇', '军舰', '航母', 'navy', 'ships', 'vessels', 'carriers', '驱逐舰', '潜艇'],
        'air_force': ['空军', '战机', '飞机', 'air force', 'aircraft', 'fighters', '战备', '战备率', '空军战备'],
        'power': ['军力', '实力', 'power', 'strength', '综合', '对比', 'bubble', '气泡'],
        'pla_treemap': ['解放军', 'pla', 'tree', '树图', '矩阵', 'treemap', '构成', '结构']
    }

    # 检查搜索词匹配
    matched_charts = set()

    if len(search_query) <= 1 or not any(char.isalnum() or '\u4e00' <= char <= '\u9fff' for char in search_query):
        return jsonify({
            'show_all': False,
            'show_expenditure': False,
            'show_personnel': False,
            'show_equipment': False,
            'show_artillery': False,
            'show_navy': False,
            'show_air_force': False,
            'show_power': False
        })

    for chart_type, keywords in chart_keywords.items():
        for keyword in keywords:
            if (keyword in search_query) or (keyword.isalpha() and keyword in search_query.split()):
                matched_charts.add(chart_type)
                break

    if not matched_charts:
        return jsonify({
            'show_all': False,
            'show_expenditure': False,
            'show_personnel': False,
            'show_equipment': False,
            'show_artillery': False,
            'show_navy': False,
            'show_air_force': False,
            'show_power': False
        })

    return jsonify({
        'show_all': False,
        'show_expenditure': 'expenditure' in matched_charts,
        'show_personnel': 'personnel' in matched_charts,
        'show_equipment': 'equipment' in matched_charts,
        'show_artillery': 'artillery' in matched_charts,
        'show_navy': 'navy' in matched_charts,
        'show_air_force': 'air_force' in matched_charts,
        'show_power': 'power' in matched_charts,
        'show_pla_treemap': 'pla_treemap' in matched_charts
    })


if __name__ == '__main__':
    init_data()
    app.run(debug=True, port=5000)