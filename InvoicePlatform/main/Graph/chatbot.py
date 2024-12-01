import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyvis.network import Network
import os
# from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import (HumanMessage)


class Chatbot:

    def __init__(self):
        self.type = type
        os.environ["OPENAI_API_KEY"] = ''

        #type: quote, category, product, rfm, comparison...

    def generate_text(self, nodes, edges, item_tag, type):
        pass

    def generate_slogan(self, node, edge):
        #node = node.to_string()
        #edge = edge.to_string()
        content = f"""你現在是一位專業的市場行銷專家。
                  以下將提供該graph的node(node_name, degree, color, group, is_articulation_point)和edge(from, to, counts)
                  Node為：{node}，Edge為：{edge}，
                  請選擇適合的倂買關係來生成3個以上的行銷文案，文案必須幽默有趣。
                  """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content

        return answer

    def generate_category_analysis(self, node, edge):
       # node = node.to_string()
        #edge = edge.to_string()
        content = f"""你現在是一位專業的商業分析師，請提供一份超過3000字且完整且專業的產品銷售分析文字報告！！！。
                  以下將提供該graph的node(node_name, degree, color, group, is_articulation_point)和edge(from, to, counts)
                  Node為：{node}，Edge為：{edge}，
                  請依照以下步驟做詳細解釋，
                  1. 除了self-connected node之外，請找出倂買關係中，最好的前25%的倂買關係，並依比例大小做排序，列出他們的倂買次數（兩個類別產品都要列出）與比例。
                  2. 根據倂買關係的結果給予商家營業建議。
                  3. 每個node都有一個group屬性，代表該node所屬的community，請針對community做分析。
                  4. 每個node都有一個is_articulation_point屬性，代表該node是否為articulation_point，請針對articulation_point做分析。
                  5. 除了articulation_points相關的併買關係之外，請找出其他需要被促銷的產品關係。
                  請提供完整網路圖分析報告，內容需清楚明瞭
                  """
        #5. 以下是過去一年前10名產品的eigenvector centrality，{ce}，請針對每項產品這一年的centrality變化趨勢做解釋。
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_articulation_analysis(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    The response has to be over 3000 words. Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    Articulation Point Identification:
                    Please list all articulation point based on the data. Explain each of point in details. 


                    Articulation Point Importance:
                    For each articulation points. How many product are connected to them and what are those products.
                    If an articulation point product disapper, how would the network changes and what's the results.
                    If an articulation point is disappeared, what product would become isolated. List all isolated products in details!!!!!! give me the exact number how the purchase decrease!!!!!!
                    Explain in details and show your reasoning process(3000 words at least). 


                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese. and no more 800 words
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_articulation_analysis_q1(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    1. Articulation Point Identification:
                    Please list all articulation point based on the data. Explain each of point in details. 

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese. and no more 800 words.
                    Return in pure text format. Not in markdown format.
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_articulation_analysis_q2(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    2. Articulation Point Importance:
                    For each articulation points. How many product are connected to them and what are those products.
                    If an articulation point product disapper, how would the network changes and what's the results.
                    If an articulation point is disappeared, what product would become isolated. 
                    You must list all the isolated products in details!!!!!! give me the exact number how the purchase decrease!!!!!!
                    You must list all the isolated products in details!!!!!! give me the exact number how the purchase decrease!!!!!!
                    You must list all the isolated products in details!!!!!! give me the exact number how the purchase decrease!!!!!!
                    You must list all the isolated products in details!!!!!! give me the exact number how the purchase decrease!!!!!!
                    You must list all the isolated products in details!!!!!! give me the exact number how the purchase decrease!!!!!!
                    You must list all the isolated products in details!!!!!! give me the exact number how the purchase decrease!!!!!!
                    Explain in details and show your reasoning process



                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese. and no more 800 words
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    

    def generate_community_analysis(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    The response has to be over 3000 words. Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    Community Identification:
                    Please list all community based on the data. Explain each community in details. 
                    Indicate the color but tag them in a understable way.

                    Cross Communities Relationships:
                    Please indicate which communities are more closed. and which communities are not.

                    Important Products in each Communities:
                    For every communities, list all the important products. Importance is based on total edge weight which the node is adjacent to.

                    Cross-Community Product  recommendation:
                    Which product combination accross the community are need to be promoted.

                    Within-Community Product combination recommendation:
                    Which product combination within every community are need to be promoted.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese.
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_community_analysis_q1(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    The response has to be over 3000 words. Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    1. Community Identification:
                    Please list all community based on the data. Explain each community in details. 
                    Indicate the color but tag them in a understable way.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese and no more over 800 words.
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_community_analysis_q2(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    The response has to be over 3000 words. Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    2. Cross Communities Relationships:
                    Please indicate which communities are more closed. and which communities are not.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese and no more over 800 words.
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_community_analysis_q3(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    The response has to be over 3000 words. Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    3. Important Products in each Communities:
                    For every communities, list all the important products. Importance is based on total edge weight which the node is adjacent to.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese. and no more over 800 words
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_community_analysis_q4(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    4. Cross-Community Product  recommendation:
                    Which product combination accross the community are need to be promoted.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese and no more 800 words.
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_community_analysis_q5(self, node, edge):
        content = f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    5. Within-Community Product combination recommendation:
                    Which product combination within every community are need to be promoted.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese. and no more 800 words.
                    """
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=800)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_regular_analysis(self, node, edge):
        print(node)
        print(edge)
        #node_str = node.to_string(index=False)
        #edge_str = edge.to_string(index=False)

        content = (f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    1. Top Co-Purchased Products:
                    Identify and list up to 5 product combinations that were purchased together the most frequently.
                    Provide the combinations along with their co-purchase counts and percentages.

                    2. Least Co-Purchased Products:
                    Identify and list up to 5 product combinations that were purchased together the least frequently (but still at least once).
                    Provide the combinations along with their co-purchase counts and percentages.

                    3. Best-Selling Combinations(List at least three):
                    Based on the data, suggest a product combination which is  a best-seller currently.
                    Explain in detail why you believe this combination has high potential (consider factors like high individual sales but low co-purchase rates, strategic product pairs, etc.).
                    The result have to be based on the data not rationality.

                    4. Underperforming Combinations with Potential(List at least three):
                    Identify a product combination that is currently underperforming but has the potential to become a best-seller.
                    Provide detailed reasoning for your choice (e.g., products with complementary features, high individual popularity but low co-purchase rates).
                    The result have to be based on the data not rationality.

                    5. Recommendation of combination with multiple products(List at least three):
                    The numbder of product in a combination does not have to be 2. It can be any other number product in a sales combination.
                    Indicate which combination has the potential to become a best seller.
                    Provide these kind of combination and detailed reasoning for your choice.
                    The result have to be based on the data not rationality.

                    6. Sales Strategy Recommendations:
                    Based on your analysis of the network graph, provide detailed and actionable advice to the business on how to improve their sales strategies.
                    Consider aspects such as product bundling, targeted promotions, cross-selling opportunities, and community groupings from the Louvain Algorithm.

                    Additional Instructions:
                    Use the data provided to support your analysis, citing specific examples where appropriate.
                    Refer to products by their Product Name as given in the data.
                    Ensure that your explanations are highly detailed, complex, and professional, showcasing deep analytical skills.
                    Incorporate advanced analytical concepts, such as network theory, statistical analysis, and market economics.
                    Use data-driven reasoning and, if necessary, assume hypothetical values to illustrate your points clearly.
                    Include conceptual descriptions of any relevant charts, graphs, or network diagrams to support your analysis.
                    Discuss the implications of network features, such as articulation points and high-degree nodes, on sales strategies and network robustness.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese.
                    """)
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer


    def generate_regular_analysis_q1(self, node, edge):
        print(node)
        print(edge)
        #node_str = node.to_string(index=False)
        #edge_str = edge.to_string(index=False)

        content = (f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    1. Top Co-Purchased Products:
                    Identify and list up to 5 product combinations that were purchased together the most frequently along with their co-purchase counts and percentages.
                 
                    Additional Instructions:
                    Use the data provided to support your analysis, citing specific examples where appropriate.
                    Refer to products by their Product Name as given in the data.
                    Ensure that your explanations are highly detailed, complex, and professional, showcasing deep analytical skills.

                    Note to the Assistant:
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Please answer in Traditional Chinese and do not over 700 words.
                    """)
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=700)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_regular_analysis_q2(self, node, edge):
        print(node)
        print(edge)
        #node_str = node.to_string(index=False)
        #edge_str = edge.to_string(index=False)

        content = (f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    2. Least Co-Purchased Products:
                    Identify and list up to 5 product combinations that were purchased together the least frequently (but still at least once), along with their co-purchase counts and percentages.

                    Additional Instructions:
                    Use the data provided to support your analysis, citing specific examples where appropriate.
                    Refer to products by their Product Name as given in the data.
                    Ensure that your explanations are highly detailed, complex, and professional, showcasing deep analytical skills.
                
                    Note to the Assistant:
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Please answer in Traditional Chinese and do not over 700 words.
                    """)
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=700)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_regular_analysis_q3(self, node, edge):
        print(node)
        print(edge)
        #node_str = node.to_string(index=False)
        #edge_str = edge.to_string(index=False)

        content = (f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                 
                    3. Best-Selling Combinations(List at least three):
                    Based on the data, suggest a product combination which is  a best-seller currently.
                    Explain in detail why you believe this combination has high potential (consider factors like high individual sales but low co-purchase rates, strategic product pairs, etc.).
                    The result have to be based on the data not rationality.

                    
                    Additional Instructions:
                    Use the data provided to support your analysis, citing specific examples where appropriate.
                    Refer to products by their Product Name as given in the data.
                    Ensure that your explanations are highly detailed, complex, and professional, showcasing deep analytical skills.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese and do not over 1000 words.
                    """)
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=1000)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_regular_analysis_q4(self, node, edge):
        print(node)
        print(edge)
        #node_str = node.to_string(index=False)
        #edge_str = edge.to_string(index=False)

        content = (f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    4. Underperforming Combinations with Potential(List at least three):
                    Identify a product combination that is currently underperforming but has the potential to become a best-seller.
                    Provide detailed reasoning for your choice (e.g., products with complementary features, high individual popularity but low co-purchase rates).
                    The result have to be based on the data not rationality.

                    Additional Instructions:
                    Use the data provided to support your analysis, citing specific examples where appropriate.
                    Refer to products by their Product Name as given in the data.
                    Ensure that your explanations are highly detailed, complex, and professional, showcasing deep analytical skills.
                    Incorporate advanced analytical concepts, such as network theory, statistical analysis, and market economics.
                    Use data-driven reasoning and, if necessary, assume hypothetical values to illustrate your points clearly.
                    Include conceptual descriptions of any relevant charts, graphs, or network diagrams to support your analysis.
                    Discuss the implications of network features, such as articulation points and high-degree nodes, on sales strategies and network robustness.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese and do not over 1000 words.
                    """)
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=1000)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

    def generate_regular_analysis_q5(self, node, edge):
        print(node)
        print(edge)
        #node_str = node.to_string(index=False)
        #edge_str = edge.to_string(index=False)

        content = (f"""
                    Prompt:

                    You are a professional business analyst who helps businesses make decisions by providing insights from various aspects of sales data.
                    Please give the answers with detailed explanation and your reasoning.

                    Data Overview:

                    We have a co-purchasing network graph represented by two dataframes: Nodes and Edges.

                    Nodes Data Description:

                    Each row represents a product node with the following columns:
                    Node: Product Name
                    Degree: The number of adjacent products (connections)
                    is_articulation_point: Indicates if the node is an articulation point (True or False)
                    Group: The community to which the product belongs, based on the Louvain Algorithm
                    Size: The proportion of sales for that product relative to total sales
                    Nodes Dataframe: {node}

                    Edges Data Description:

                    Each row represents a co-purchasing relationship (edge) between two products with the following columns:
                    Source: One end of the edge (Product Name)
                    Target: The other end of the edge (Product Name)
                    COUNTS: A JSON object containing:
                    COUNTS: The number of orders where both products were purchased together
                    PERCENTAGE: The proportion of orders with both products relative to total orders

                    Edges Dataframe: {edge}

                    Note: An edge between two nodes means that the two products were co-purchased in at least one order.

                    Tasks:

                    5. Recommendation of combination with multiple products(Namely one sales combination has at least three products):
                    The numbder of product in a combination does not have to be 2. It can be any other number product in a sales combination.
                    Indicate which combination has the potential to become a best seller.
                    Provide these kind of combination and detailed reasoning for your choice.
                    The result have to be based on the data not rationality.
                    
                    Additional Instructions:
                    Use the data provided to support your analysis, citing specific examples where appropriate.
                    Refer to products by their Product Name as given in the data.
                    Ensure that your explanations are highly detailed, complex, and professional, showcasing deep analytical skills.
                    Incorporate advanced analytical concepts, such as network theory, statistical analysis, and market economics.
                    Use data-driven reasoning and, if necessary, assume hypothetical values to illustrate your points clearly.
                    Include conceptual descriptions of any relevant charts, graphs, or network diagrams to support your analysis.
                    Discuss the implications of network features, such as articulation points and high-degree nodes, on sales strategies and network robustness.

                    Note to the Assistant:
                    If specific data is required for analysis and not provided, explain how you would approach the analysis or state any assumptions you are making.
                    Use appropriate professional language and structure your response with clear headings and subheadings.
                    Provide in-depth explanations and explore complex relationships within the data.
                    Support your conclusions with logical reasoning and, where applicable, reference relevant business theories or models.
                    Please answer in Traditional Chinese and do not over 1000 words.
                    """)
        chat = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=1000)
        resp = chat([HumanMessage(content=content)])
        answer = resp.content
        return answer

