import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyvis.network import Network
import datetime
import os
import psycopg2
import calendar
import json
from networkx.readwrite import json_graph
import calendar
import pandas as pd


class ProductNetwork:
    # flow: initialize network -> setQuery -> executeQuery -> analysis -> create network ->visualize
    """
    Initialization
    self.query_network: the query statements

    self.graph: <networkx graph>
    self.original_graph: path of original graph
    self.articultion_graph: path of graph with articulation points
    self.community_graph: path of graph with community

    """

    def __init__(self, username, network_name, type=None, tag=None):

        self.username = username
        self.network_name = network_name

        if not os.path.exists(f"./{username}/{network_name}"):
            os.makedirs(f"./{username}/{network_name}")

        self.query_network = None
        self.type = type # Category, Product, RFM
        self.tag = tag # put specific category here

        self.graph = None
        self.node_attributes = None
        self.edge_attributes = None

        self.original_graph = None
        self.articulation_graph = None
        self.community_graph = None
        self.compare_graph = None

        self.communities = None
        self.articulation_points = None
        self.relationship_df = None
        self.channel_df = None
        self.query_list = None
        self.condition = None

        self.country_dict = {
            "南投縣": "Nantou",
            "嘉義市": "ChiaYiCity",
            "新北市": "NewTaipei",
            "新竹市": "HsinChuCity",
            "新竹縣": "HsinChuCounty",
            "桃園市": "TaoYuan",
            "澎湖縣": "PengHo",
            "臺中市": "Taichung",
            "臺北市": "Taipei",
            "臺南市": "Tainan",
            "臺東縣": "Taitung",
            "花蓮縣": "HuaLien",
            "苗栗縣": "MiaoLi",
            "金門縣": "KingMen",
            "雲林縣": "YuinLin",
            "高雄市": "KaoHsung",
            "嘉義縣": "ChiaYiCounty",
            "基隆市": "KeeLung",
            "宜蘭縣": "YiLan",
            "屏東縣": "PingTung",
            "彰化縣": "ChungHua",
            "nan": "nan",
        }

        # to do save
        self.directory = None

        self.conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="0000",
            host="127.0.0.1",
            port="5432",
        )
        self.cur = self.conn.cursor()
        self.g = None

    def query(
        self,
        query=None,
        datetime_lower_bound=None,
        datetime_upper_bound=None,
        item_name=None,
        unit_price_lower_bound=None,
        unit_price_upper_bound=None,
        item_tag=None,
        item_brand_name=None,
        store_brand_name=None,
        county=None,
        city_area=None,
        segment=None,
        limit=100,
        excludedDiscounts=None
    ):
        condition = ""
        tag = ""
        if datetime_lower_bound and datetime_lower_bound != 'None':
            condition += f"AND datetime >= '{datetime_lower_bound}-01' "

        if datetime_upper_bound and datetime_upper_bound != 'None':
            year, month = map(int, datetime_upper_bound.split('-'))
            # Get the last day of the month
            last_day = calendar.monthrange(year, month)[1]
            condition += f"AND datetime <= '{datetime_upper_bound}-{last_day}'"
        if item_name:
            if isinstance(item_name, list):
                if len(item_name) == 1:
                    condition += f" AND item_name = '{item_name[0]}'"
                else:
                    # Use `IN` for multiple items
                    condition += f" AND item_name IN {tuple(item_name)}"
            else:
                condition += f"AND item_name = '{item_name}'"
        if unit_price_lower_bound:
            condition += f"AND unit_price >= '{unit_price_lower_bound}'"
        if unit_price_upper_bound:
            condition += f"AND unit_price <= '{unit_price_upper_bound}'"

        if item_brand_name:
            condition += f"AND item_brand_name = '{item_brand_name}'"
        if store_brand_name:
            if isinstance(store_brand_name, list):
                condition += f" AND store_brand_name IN {tuple(store_brand_name)}"
            else:
                condition += f" AND store_brand_name = '{store_brand_name}'"
        if county:
            condition += f"AND county = '{county}'"
            self.county = county
        if city_area:
            condition += f"AND city_area = '{city_area}'"
        if segment:
            condition += f"AND segment = '{segment}'"

        self.temp_condition = condition
        if item_tag:
            self.type = item_tag
            #self.temp_condition = condition
            condition += f"AND item_tag = '{item_tag}' "
        # tag2 = f"AND (a_item_tag = '{item_tag}' or b_item_tag = '{item_tag}' ) "

        #if not query:
        #    query = "SELECT * FROM test WHERE 1=1 " + condition + tag
        #else:
        #    query = query + condition
        #print(query)
        self.condition = condition
        print(self.condition)
        print(self.temp_condition)
        #
        # print(condition)
        print(self.country_dict[county])
        q = str(
            f"""
                        WITH INV_NUMBERS AS (
                        SELECT DISTINCT inv_num 
                        FROM test 
                        WHERE 1=1 {condition}
                        )
                        SELECT 
                            t.a_item_tag, 
                            t.b_item_tag,
                            COUNT(t.id) AS coun
                        FROM 
                            public.{self.country_dict[county]} t
                        JOIN 
                            INV_NUMBERS i ON t.inv_num = i.inv_num    
                        WHERE 1=1
                            {"AND t.a_item_tag != '優惠活動/折扣/集點' AND t.b_item_tag != '優惠活動/折扣/集點'" if excludedDiscounts else ""}
                        GROUP BY 
                            t.a_item_tag, 
                            t.b_item_tag 
                        ORDER BY 
                            coun DESC 
                        LIMIT {limit};
                         """
        )
        print(q)
        try:
            # 執行查詢
            self.cur.execute(q)
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")
            return None

        try:
            # 獲取查詢結果並轉換為 DataFrame
            results = self.cur.fetchall()
            if not results:
                print("The result of this query contains no data")
                return None
            df = pd.DataFrame(results)
        except Exception as e:
            print(f"Error converting query result to DataFrame: {e}")
            return None
        if df.shape[0] == 0:
            print("The result of this query contains no data")
            return None

        df = df.sort_values([2], ascending=False)
        df[3] = df[2] / (df[2].sum()) * 100
        df = df.rename(columns={0: "ELEMENT1", 1: "ELEMENT2", 2: "COUNTS", 3: "PERCENTAGE"})
        df = df[:df.shape[0]].round({3: 2}).reset_index(drop=True)
        print(df)

        if self.type == "Category":
            df["item_tag"] = [self.type for i in range(0, df.shape[0])]
        else:
            df["item_tag"] = ["" for i in range(0, df.shape[0])]

        df.reset_index(drop=True)
        self.relationship_df = df
        return df

    def save(self):
        with open(f"./{self.username}/{self.network_name}/graph.json", "w") as f:
            data = json_graph.node_link_data(self.g)
            json.dump(data, f, indent=2)
        self.relationship_df.to_csv(f'./{self.username}/{self.network_name}/relationships.csv')
        print("save successfully")
        return

    # def load(self):
    #     with open(f"./{self.username}/{self.network_name}/graph.json", "r") as f:
    #         js_graph = json.load(f)
    #         print(json_graph.node_link_graph(js_graph))
    #         self.g = json_graph.node_link_graph(js_graph)
    #         self.relationship_df = pd.read_csv(f'./{self.username}/{self.network_name}/relationships.csv')
    #         #pd.read_json(stored_json)
    #         print("load successfully")
    #     return
    def load(self, json, csv):
        print(json_graph.node_link_graph(json))
        self.g = json_graph.node_link_graph(json)
        self.relationship_df = pd.read_json(csv, orient='split')
        print("load successfully")
        return

    # return

    def create_network(self):
        links = self.relationship_df
        g = nx.from_pandas_edgelist(links, "ELEMENT1", "ELEMENT2", edge_attr=True, create_using=nx.Graph())

        # Add item_tag as node attribute
        for node in g.nodes():
            item_tags = links.loc[(links["ELEMENT1"] == node) | (links["ELEMENT2"] == node), "item_tag"]
            if not item_tags.empty:
                g.nodes[node]["item_tag"] = item_tags.iloc[0]

        self.g = g
        return g

    def visualize_graph(self, g, _type, _compare=None):
        if g is None:
            print("Empty graph, nothing to visualize.")
            return None

        graph = Network(notebook=True)
        node_attributes = pd.DataFrame(g.degree, columns=["Node", "Degree"])

        self.articulation_points = list(nx.articulation_points(g))
        a_tf = []
        for i in range(0, node_attributes.shape[0]):
            if node_attributes["Node"][i] in self.articulation_points:
                a_tf.append(True)

            else:
                a_tf.append(False)
        node_attributes["is_articulation_point"] = a_tf

        comm = nx.community.louvain_communities(g, seed=123)
        self.communities = comm
        community = {}
        for i in range(0, len(comm)):
            for item in comm[i]:
                community[item] = i
        color = [
            "#FF0000",
            "#00FFFF",
            "#FFA500",
            "#800080",
            "#A52A2A",
            "#FFFF00",
            "#800000",
            "#008000",
            "#FF00FF",
            "#808000",
            "#FFC0CB",
            "#7FFFD4",
        ]
        node_attributes["Group"] = [community[node_attributes["Node"][i]] for i in range(0, node_attributes.shape[0])]

        # Get the item_tag from node attributes
        item_tag = None

        for node in g.nodes(data=True):
            if "item_tag" in node[1]:
                item_tag = node[1]["item_tag"]
                break

        node_attributes["Size"] = np.sqrt(node_attributes["Degree"]) * 5

        if _type == "original" or _type == None:
            node_attributes["Color"] = np.where(node_attributes["Node"] == item_tag, "orange", "orange")
        else:
            node_attributes["Color"] = np.where(node_attributes["Node"] == item_tag, "red", "orange")

        if _type == "articulation":

            for i in range(0, node_attributes.shape[0]):
                if node_attributes["Node"][i] in self.articulation_points:
                    node_attributes["Color"][i] = "green"

                if node_attributes["Node"][i] == item_tag:
                    node_attributes["Color"][i] = "red"

        if _type == "community":
            node_attributes["Color"] = [
                color[community[node_attributes["Node"][i]]] for i in range(0, node_attributes.shape[0])
            ]

        if _type == "compare_node":
            for i in range(0, node_attributes.shape[0]):
                if node_attributes["Node"][i] in _compare:
                    node_attributes['Color'][i] = "Red"
                else:
                    node_attributes['Color'][i] = "Orange"

        node_attributes["Title"] = node_attributes.apply(lambda x: f"{x['Node']}\nDegree: {x['Degree']}", axis=1)

        print(node_attributes)

        for _, row in node_attributes.iterrows():
            graph.add_node(row["Node"], size=row["Size"], color=row["Color"], title=row["Title"])

        edge_attributes = pd.DataFrame(g.edges(data=True), columns=["Source", "Target", "COUNTS"])

        color = []
        if _type == "compare_edge":
            for i in range(0, edge_attributes.shape[0]):
                if (frozenset([edge_attributes['Source'][i], edge_attributes['Target'][i]]) in _compare):
                    color.append('Red')
                else:
                    color.append('silver')
            edge_attributes['Color'] = color
        else:
            color = ['silver' for x in range(0, edge_attributes.shape[0])]
            edge_attributes['Color'] = color
        print(color)

        for _, row in edge_attributes.iterrows():
            weight_title = f"Weight: {row['COUNTS']['COUNTS']}"

            graph.add_edge(
                row["Source"],
                row["Target"],
                #color="silver",
                color=row['Color'],
                title=weight_title,
                width=(row["COUNTS"]["COUNTS"] / 300),
            )

        print(node_attributes)
        print(edge_attributes)
        self.node_attributes = node_attributes
        self.edge_attributes = edge_attributes
        html_content = graph.generate_html(notebook=False)

        return graph, html_content

    def _insert_relationship(self):
        pass

    def vis_all_graph(self):
        return [
            self.vis_original_graph(),
            self.vis_articulation_graph(),
            self.vis_community_graph(),
        ]

    def vis_original_graph(self):
        original_graph_name = "origin_case.html"
        graph, graph_html = self.visualize_graph(self.g, _type="original")
        graph.show(f"./{self.username}/{self.network_name}/{original_graph_name}")
        # self.original_graph = original_graph_name
        # return self.original_graph
        return graph_html

    def vis_articulation_graph(self):
        articulation_graph_name = "articulation_case.html"
        graph, graph_html = self.visualize_graph(self.g, _type="articulation")
        graph.show(f"./{self.username}/{self.network_name}/{articulation_graph_name}")
        # self.articulation_graph = articulation_graph_name
        # return self.articulation_graph
        return graph_html

    def vis_community_graph(self):
        community_graph_name = "community_case.html"
        graph, graph_html = self.visualize_graph(self.g, _type="community")
        graph.show(f"./{self.username}/{self.network_name}/{community_graph_name}")
        # self.community_graph = community_graph_name
        # return self.community_graph
        return graph_html

    def get_articulation_points(self):
        return self.articulation_points

    def get_communities(self):
        return self.communities

    def get_relationship_df(self):
        return self.relationship_df

    def get_nodes(self):
        return self.node_attributes

    def get_edges(self):
        return self.edge_attributes

    def show_compare(self, type, common):

        compare_graph_name = f"{type}.html"
        graph, graph_html = self.visualize_graph(self.g, type, common)
        graph.show(f"./{self.username}/{self.network_name}/{compare_graph_name}")
        self.compare_graph = compare_graph_name
        return graph_html

    def show_heatmap(self):
        pass

    # def get_item_name(
    #     self,
    #     item_tag,
    #     datetime_lower_bound=None,
    #     datetime_upper_bound=None,
    #     store_brand_name=None,
    #     county=None,
    #     city_area=None,
    #     limit=100
    # ):
    #     condition = ""
    #     tag = ""
    #     # {self.temp_condition}
    #     if datetime_lower_bound:
    #         condition += f"AND datetime >= '{datetime_lower_bound}' "
    #     if datetime_upper_bound:
    #         condition += f"AND datetime <= '{datetime_upper_bound}'"

    #     if store_brand_name:
    #         if isinstance(store_brand_name, list):
    #             condition += f" AND store_brand_name IN {tuple(store_brand_name)}"
    #         else:
    #             condition += f" AND store_brand_name = '{store_brand_name}'"
    #     if county:
    #         condition += f"AND county = '{county}'"
    #         self.county = county
    #     if city_area:
    #         condition += f"AND city_area = '{city_area}'"

    #     self.temp_condition = condition
    #     if item_tag:
    #         # self.type = item_tag
    #         self.temp_condition = condition
    #         condition += f"AND item_tag = '{item_tag}' "
    #     self.cur.execute(
    #         f"""
    #                     SELECT
    #                         item_name,
    #                         SUM(quantity) as TOTAL_QUANTITY,
    #                         SUM(amount) as TOTAL_PROFIT
    #                     FROM
    #                         test
    #                     WHERE
    #                         {condition} AND
    #                         item_tag = '{item_tag}'

    #                     GROUP BY
    #                         item_name
    #                     ORDER BY
    #                         SUM(amount) DESC
    #                     """
    #     )

    def get_item_name(
        self,
        small_tag,
        item_tag,
        product_list,
        datetime_lower_bound=None,
        datetime_upper_bound=None,
        store_brand_name=None,
        county=None,
        city_area=None,
        limit=None
    ):

        condition = ["1=1"]
        # params = []

        if datetime_lower_bound and datetime_lower_bound != 'None':
            condition.append(f" datetime >= '{datetime_lower_bound}-01' ")

        if datetime_upper_bound and datetime_upper_bound != 'None':
            year, month = map(int, datetime_upper_bound.split('-'))
            last_day = calendar.monthrange(year, month)[1]
            condition.append(f" datetime <= '{datetime_upper_bound}-{last_day}'")

        if store_brand_name:
            if isinstance(store_brand_name, list):
                condition.append(f"store_brand_name IN {tuple(store_brand_name)}")
            else:
                condition.append(f"store_brand_name = '{store_brand_name}'")

        # 縣市
        if county:
            condition.append(f"county = '{county}'")

        if city_area:
            condition.append(f"city_area = '{city_area}'")

        # 商品標籤
        if item_tag:
            condition.append(f"item_tag = '{item_tag}'")

        if not limit:
            limit = 100

        # 生成查詢條件
        query_condition = " AND ".join(condition)

        print(item_tag)
        print(small_tag)
        print(product_list)

        if item_tag == small_tag and len(produc_list) != 0:

            query = f"""
            WITH INV_NUMBERS AS (
                        SELECT DISTINCT inv_num 
                        FROM test 
                        WHERE  {query_condition}
                        )
            SELECT 
                item_name, 
                SUM(quantity) as TOTAL_QUANTITY, 
                SUM(amount) as TOTAL_PROFIT
            FROM 
                test
            JOIN
                INV_NUMBERS i ON test.inv_num = i.inv_num
            WHERE 
                1=1 AND item_name IN {tuple(product_list)}
            GROUP BY 
                item_name
            ORDER BY 
                SUM(amount) DESC
            LIMIT {limit};
        """
        # 查詢語句
        else:
            query = f"""
                WITH INV_NUMBERS AS (
                            SELECT DISTINCT inv_num 
                            FROM test 
                            WHERE  {query_condition}
                            )
                SELECT 
                    item_name, 
                    SUM(quantity) as TOTAL_QUANTITY, 
                    SUM(amount) as TOTAL_PROFIT
                FROM 
                    test
                JOIN
                    INV_NUMBERS i ON test.inv_num = i.inv_num
                WHERE 
                    {query_condition}
                GROUP BY 
                    item_name
                ORDER BY 
                    SUM(amount) DESC
                LIMIT {limit};
            """
        print(query)
        self.cur.execute(query)
        result = self.cur.fetchall()

        # 轉換結果為 DataFrame
        df = pd.DataFrame(result)

        if not df.empty:
            df = df.rename(columns={0: "ITEM_NAME", 1: "TOTAL_QUANTITY", 2: "TOTAL_PROFIT"})
        return df

    def get_channel_with_item_tag(self, item_tag):
        self.cur.execute(
            f"""
                        SELECT store_brand_name, SUM(quantity) as TOTAL_QUANTITY, SUM(amount) as TOTAL_PROFITS, (SUM(amount)/SUM(quantity)) as profit_per_unit, COUNT(item_name) AS number_of_sales_count, SUM(amount)/COUNT(item_name) AS profit_per_sales
                        FROM test
                        WHERE 1=1 AND item_tag = '{item_tag}' AND store_brand_name IS NOT NULL
                        GROUP BY store_brand_name
                        ORDER BY SUM(amount) DESC
                         """
        )
        df = pd.DataFrame(self.cur.fetchall())
        print(df)
        df = df.rename(
            columns={
                0: "STORE_NAME",
                1: "TOTAL_QUANTITY",
                2: "TOTAL_PROFIT",
                3: "PROFIT_PER_UNIT",
                4: "NUMBER_OF_SALESRECORD",
                5: "PROFIT_PER_SALES"
            }
        )
        return df

    def get_channel_with_item_name(self, item_name):
        # self.cur.execute(
        #     f"""
        #     SELECT store_brand_name, SUM(quantity) as TOTAL_QUANTITY, SUM(amount) as TOTAL_PROFITS,
        #         (SUM(amount)/SUM(quantity)) as profit_per_unit, COUNT(item_name) AS number_of_sales_count,
        #         SUM(amount)/COUNT(item_name) AS profit_per_sales
        #     FROM test
        #     WHERE item_name IN {tuple(item_name)} AND store_brand_name IS NOT NULL
        #     GROUP BY store_brand_name
        #     ORDER BY SUM(amount) DESC
        #     """
        # )
        self.cur.execute(
            """
            SELECT store_brand_name, SUM(quantity) as TOTAL_QUANTITY, SUM(amount) as TOTAL_PROFITS, 
                (SUM(amount)/SUM(quantity)) as profit_per_unit, COUNT(item_name) AS number_of_sales_count, 
                SUM(amount)/COUNT(item_name) AS profit_per_sales
            FROM test
            WHERE item_name IN %s AND store_brand_name IS NOT NULL
            GROUP BY store_brand_name
            ORDER BY SUM(amount) DESC
            """, (tuple(item_name),)
        )

        df = pd.DataFrame(self.cur.fetchall())
        print(df)
        df = df.rename(
            columns={
                0: "STORE_NAME",
                1: "TOTAL_QUANTITY",
                2: "TOTAL_PROFIT",
                3: "PROFIT_PER_UNIT",
                4: "NUMBER_OF_SALESRECORD",
                5: "PROFIT_PER_SALES"
            }
        )
        return df


def saveJson(username, network_name, data, relationship_df):
    with open(f"./{username}/{network_name}/graph.json", "w") as f:
        json.dump(data, f, indent=2)
    relationship_df.to_csv(f'./{username}/{network_name}/relationships.csv')
    print("save successfully")
    return


def compare_node(g1, g2):
    df1 = g1.relationship_df
    df2 = g2.relationship_df
    set_df1 = set()
    set_df2 = set()

    meta_df1 = dict()
    meta_df2 = dict()

    for i in range(0, df1.shape[0]):
        if df1['ELEMENT1'][i] in meta_df1:
            meta_df1[df1['ELEMENT1'][i]] += df1['COUNTS'][i]
        if df1['ELEMENT2'][i] in meta_df1:
            meta_df1[df1['ELEMENT2'][i]] += df1['COUNTS'][i]

        if df1['ELEMENT1'][i] not in meta_df1:
            meta_df1[df1['ELEMENT1'][i]] = df1['COUNTS'][i]
        if df1['ELEMENT2'][i] not in meta_df1:
            meta_df1[df1['ELEMENT2'][i]] = df1['COUNTS'][i]

    for i in range(0, df2.shape[0]):
        if df2['ELEMENT1'][i] in meta_df2:
            meta_df2[df2['ELEMENT1'][i]] += df2['COUNTS'][i]
        if df2['ELEMENT2'][i] in meta_df2:
            meta_df2[df2['ELEMENT2'][i]] += df2['COUNTS'][i]

        if df2['ELEMENT1'][i] not in meta_df2:
            meta_df2[df2['ELEMENT1'][i]] = df2['COUNTS'][i]
        if df2['ELEMENT2'][i] not in meta_df2:
            meta_df2[df2['ELEMENT2'][i]] = df2['COUNTS'][i]

    for i in range(0, df1.shape[0]):
        set_df1.add(df1['ELEMENT1'][i])
        set_df1.add(df1['ELEMENT2'][i])

    for i in range(0, df2.shape[0]):
        set_df2.add(df2['ELEMENT1'][i])
        set_df2.add(df2['ELEMENT2'][i])
    intersection_df = set_df1 & set_df2
    print(intersection_df)

    node = []
    counts = []
    for key in meta_df1.keys():
        print(key)
        if key in intersection_df:
            node.append(key)
            counts.append(meta_df1[key])

    d = pd.DataFrame([], columns=['NODE', 'COUNTS'])
    d['NODE'] = node
    d['COUNTS'] = counts
    # d = d.sort_values(by=['COUNTS'], ascending=False)
    d1 = d.sort_values(by=['COUNTS'], ascending=False)
    # d.to_csv('./graph1_compare_node.csv')

    node = []
    counts = []
    for key in meta_df2.keys():
        if key in intersection_df:
            node.append(key)
            counts.append(meta_df2[key])

    d = pd.DataFrame([], columns=['NODE', 'COUNTS'])
    d['NODE'] = node
    d['COUNTS'] = counts
    d = d.sort_values(by=['COUNTS'], ascending=False)
    d2 = d.sort_values(by=['COUNTS'], ascending=False)
    # d.to_csv('./graph2_compare_node.csv')

    node = []
    counts = []
    for key in meta_df1.keys():
        if key not in intersection_df:
            node.append(key)
            counts.append(meta_df1[key])

    d = pd.DataFrame([], columns=['NODE', 'COUNTS'])
    d['NODE'] = node
    d['COUNTS'] = counts
    d = d.sort_values(by=['COUNTS'], ascending=False)
    d3 = d.sort_values(by=['COUNTS'], ascending=False)
    # d.to_csv('./not_graph1_compare_node.csv')

    node = []
    counts = []
    for key in meta_df2.keys():
        if key not in intersection_df:
            node.append(key)
            counts.append(meta_df2[key])

    d = pd.DataFrame([], columns=['NODE', 'COUNTS'])
    d['NODE'] = node
    d['COUNTS'] = counts
    d = d.sort_values(by=['COUNTS'], ascending=False)
    d4 = d.sort_values(by=['COUNTS'], ascending=False)
    # d.to_csv('./not_graph2_compare_node.csv')

    g1_html = g1.show_compare(type='compare_node', common=intersection_df)
    g2_html = g2.show_compare(type='compare_node', common=intersection_df)
    return g1_html, g2_html, [d1, d2, d3, d4]
