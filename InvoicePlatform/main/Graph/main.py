import networks
import psycopg2
import chatbot
import pandas as pd
#from d3blocks import D3Blocks


def compare_edge(g1, g2):
    df1 = g1.relationship_df
    df2 = g2.relationship_df
    print(df1)
    set_df1 = set()
    set_df2 = set()
    for i in range(0, df1.shape[0]):
        set_df1.add(frozenset([df1['ELEMENT1'][i], df1['ELEMENT2'][i]]))

    for j in range(0, df2.shape[0]):
        set_df2.add(frozenset([df2['ELEMENT1'][j], df2['ELEMENT2'][j]]))

    intersection_df = set_df1 & set_df2
    network1.show_compare(type='compare_edge', common=intersection_df)
    network2.show_compare(type='compare_edge', common=intersection_df)
    print(intersection_df)


def compare_node(g1, g2):
    df1 = g1.relationship_df
    df2 = g2.relationship_df
    set_df1 = set()
    set_df2 = set()
    for i in range(0, df1.shape[0]):
        set_df1.add(df1['ELEMENT1'][i])
        set_df1.add(df1['ELEMENT2'][i])
    for i in range(0, df2.shape[0]):
        set_df2.add(df2['ELEMENT1'][i])
        set_df2.add(df2['ELEMENT2'][i])
    intersection_df = set_df1 & set_df2
    network1.show_compare(type='compare_node', common=intersection_df)
    network2.show_compare(type='compare_node', common=intersection_df)


if __name__ == '__main__':

    network0 = networks.ProductNetwork(username='test', network_name='高雄')
    network0.query(county='高雄市', item_tag='奶酪/布丁/果凍', limit=200)
    network0.create_network()
    network0.vis_all_graph()

    result = network0.get_item_name(item_tag='奶酪/布丁/果凍')
    print(result)

    network0.l2_query(item_name='統一布丁', limit=200)
    network0.l2_create_network()
    network0.l2_vis_all_graph()

    network1 = networks.ProductNetwork(username='admin', network_name='高雄紅茶')
    network1.query(county='高雄市', item_tag='紅茶', limit=200)
    network1.create_network()
    network1.vis_all_graph()

    network2 = networks.ProductNetwork(username="betty", network_name="高雄綠茶")
    network2.query(county='高雄市', item_tag='綠茶', limit=200)
    network2.create_network()
    network2.vis_all_graph()

    compare_edge(network1, network2)
    compare_node(network1, network2)

    network1 = networks.ProductNetwork(username='admin', network_name='Loyal_Accounts')
    network1.query(county='高雄市', city_area='左營區', segment='Loyal Accounts', store_brand_name='統一超商_7Eleven', limit=100)
    network1.create_network()
    network1.vis_all_graph()

    network2 = networks.ProductNetwork(username='betty', network_name='Lost')
    network2.query(county='高雄市', city_area='左營區', segment='Lost', store_brand_name='統一超商_7Eleven', limit=100)
    network2.create_network()
    network2.vis_all_graph()

    compare_edge(network1, network2)
    compare_node(network1, network2)

    network0.get_channel_with_item_name('統一布丁')
    network0.get_channel_with_item_tag('紅茶')

# network.query(county='臺北市', city_area='中山區', item_tag='啤酒')
# network.query(county='臺北市', city_area='中正區', item_tag='啤酒')
# network.query(county='臺北市', city_area='大安區', item_tag='啤酒')
#network.execute_query()
#network.analysis(limits = 200)
#network.create_network()
#path_list = network.vis_all_graph()
#print(path_list)
#print(network.get_relationship_df())
#print(network.get_articulation_points())
#print(network.get_communities())

#d3 = D3Blocks()#

# print(network1.['COUNTS'])
#edge_df = pd.DataFrame([])
#edge_df['source'] = network1.relationship_df['ELEMENT1']
#edge_df['target'] = network1.relationship_df['ELEMENT2']
#edge_df['weight'] = network1.relationship_df['COUNTS']

#heatmap = d3.heatmap(edge_df, color='label', filepath='./')

#print(heatmap)
