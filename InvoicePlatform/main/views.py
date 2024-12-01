# views.py
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from .forms import UploadFileForm
from django.http import HttpResponse
from .models import UploadedFile, NetworkGraph
from django.urls import reverse
from .Bert.test import BertModel
import uuid
from .models import County, District, ItemBigTag, ItemSmallTag
from django.http import JsonResponse
import io
import pandas as pd
from .Graph.networks import ProductNetwork, saveJson, compare_node
from .Graph.chatbot import Chatbot
import psycopg2
from django.db import connection
from main import PathList
from decimal import Decimal
import calendar
import json
from django.core.cache import cache
from networkx.readwrite import json_graph
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

BUY_WITH = 1
PRODUCT_IN_PATH = 2
RFM = 3
RFM_WITH_PRODUCT = 4
COUNTRY_DICT = {
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


@login_required
def uploadFile(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
                b = BertModel()
                df = b.addItemTag(df)
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                content = buffer.getvalue()
            else:
                df = pd.read_excel(file)
                b = BertModel()
                df = b.addItemTag(df)
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False, engine='openpyxl')
                content = buffer.getvalue()

            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(
                file.name, io.BytesIO(content.encode('utf-8') if file.name.endswith('.csv') else content)
            )
            UploadedFile.objects.create(user=request.user, file_name=filename)
            fileUrl = fs.url(filename)
            return render(request, 'UploadFile.html', {'form': form, 'fileUrl': fileUrl})
    else:
        form = UploadFileForm()
    return render(request, 'UploadFile.html', {'form': form})


# @login_required
def getMainpage(request):
    return render(request, 'Mainpage123.html')


def getSmallTags(request):
    bigtag = request.GET.get('bigtag')
    smallTags = ItemSmallTag.objects.filter(bigTag__name=bigtag)
    smallTagList = list(smallTags.values('id', 'name'))
    return JsonResponse({'smallTags': smallTagList})


    ###directly select smallTag and Product?
def getProducts(request):
    smallTag = request.GET.get('smallTag')
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT item_name, COUNT(*) 
            FROM test 
            WHERE item_tag = %s 
            GROUP BY item_name
            ORDER BY COUNT(*) DESC
        """, [smallTag]
        )
        rows = cursor.fetchall()

    # 將產品名稱和對應的資料數量一起返回
    products = [{'name': row[0], 'count': row[1]} for row in rows]
    return JsonResponse({'products': products})


def getDistrict(request):
    county = request.GET.get('county')
    districts = District.objects.filter(county__name=county)
    districtList = list(districts.values('id', 'name'))
    return JsonResponse({'districts': districtList})


def _selectArea(request, pictureType):
    counties = County.objects.all()
    print(counties)
    selectedCounty = request.session.get('selectedCounty', '')
    errorMessage = "No"

    if request.method == 'POST':
        county = request.POST.get('county')
        if not county:
            errorMessage = "請選擇縣/市"
        else:
            request.session['selectedCounty'] = county
            if pictureType == BUY_WITH:
                return redirect('/draw_buy_with/?step=select_path_time')
            elif pictureType == PRODUCT_IN_PATH:
                return redirect('/draw_product_in_path/?step=select_time')
            elif pictureType == RFM:
                return redirect('/rfm/?step=select_path_time')
            elif pictureType == RFM_WITH_PRODUCT:
                return redirect('/rfm_with_product/?step=select_path_time')

    return render(
        request, 'Area.html', {
            'counties': counties,
            'selectedCounty': selectedCounty,
            'pictureType': pictureType,
            'errorMessage': errorMessage
        }
    )


###這邊會改成有分類的前幾+交易量前幾###
# def _filterStores(countyName, districtName=None):
#     if districtName:
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 "SELECT DISTINCT store_brand_name FROM test WHERE county = %s AND city_area = %s",
#                 [countyName, districtName]
#             )
#             rows = cursor.fetchall()
#     else:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT DISTINCT store_brand_name FROM test WHERE county = %s", [countyName])
#             rows = cursor.fetchall()
#     storeBrands = [row[0] for row in rows]

#     return storeBrands


def _filterDistrictsStore(countyName, storeList, itemTag, product=None, minStoreCount=10):
    county = COUNTRY_DICT[countyName]

    # Base SQL query initialization
    query = f"""
        SELECT store_brand_name, COUNT(*) as store_count
        FROM {county}
    """

    # Add condition for store list if provided
    if itemTag:
        query += f"""WHERE a_item_tag = '{itemTag}'"""
        if product:
            if isinstance(product, list):
                # 如果列表中只有一個元素，手動構建單元素元組的格式
                if len(product) == 1:
                    query += f" AND a_item_name = '{product[0]}'"
                else:
                    query += f" AND a_item_name IN {tuple(product)}"
            else:
                # 單個項目時直接用單元素元組的格式
                query += f" AND a_item_name = '{product}'"

        if storeList:
            stores = tuple(storeList)
            query += f" AND store_brand_name IN {stores}"
    else:
        if storeList:
            stores = tuple(storeList)
            query += f" WHERE store_brand_name IN {stores}"

    # Add GROUP BY and HAVING clauses
    query += f"""
        GROUP BY store_brand_name   
    """
    # HAVING COUNT(*) > {minStoreCount}

    # Execute query
    with connection.cursor() as cursor:
        cursor.execute(query) # Pass the parameters dynamically
        result = cursor.fetchall()

    # Extract store_brand_name from the result
    existingStores = [row[0] for row in result]

    return existingStores


def _filterDistrict(countyName):
    if countyName:
        districtList = District.objects.filter(county__name=countyName).values_list('name', flat=True)
        return list(districtList)
    return []


def _filterBigTags(request):
    countyName = request.session.get('selectedCounty', '')
    districtName = request.session.get('districtName', '')
    selectedStartTime = request.session.get('startTime', '')
    selectedEndTime = request.session.get('endTime', '')
    storeTypeList = request.session.get('storeTypeList', '')
    county = COUNTRY_DICT[countyName]
    query = f"SELECT DISTINCT a_item_tag FROM {county}"
    params = []

    hasCondition = False # 标记是否已经添加了第一个条件

    # 动态构建查询条件
    if selectedStartTime:
        query += " WHERE" if not hasCondition else " AND"
        query += f" datetime >= '{selectedStartTime}-01'"
        hasCondition = True # 第一个条件已添加

    if selectedEndTime:
        year, month = map(int, selectedEndTime.split('-'))
        lastDay = calendar.monthrange(year, month)[1]
        query += " WHERE" if not hasCondition else " AND"
        query += f" datetime <= '{selectedEndTime}-{lastDay}'"
        hasCondition = True # 标记已添加条件

    if storeTypeList:
        query += " WHERE" if not hasCondition else " AND"
        query += f" store_brand_name IN {tuple(storeTypeList)}"
        hasCondition = True # 标记已添加条件

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    smallTags = [row[0] for row in rows]
    # 暫時反向尋找，之後建立大標籤之欄位
    bigTags = ItemSmallTag.objects.filter(name__in=smallTags).values_list('bigTag__name', flat=True).distinct()
    bigTagsList = list(bigTags)
    return bigTagsList


def _selectPathAndTime(request, pictureType):
    countyName = request.session.get('selectedCounty', '')
    districtName = request.session.get('districtName', '')
    # stores = _filterStores(countyName)

    selectedStartTime = request.session.get('startTime', '')
    selectedEndTime = request.session.get('endTime', '')
    storeType = request.session.get('storeType', '')
    storeTypeList = request.session.get('storeTypeList', '')
    errorMessage = request.GET.get('error_message', '')

    if request.method == 'POST':
        startTime = request.POST.get('startTime')
        endTime = request.POST.get('endTime')
        storeType = request.POST.get('store')
        storeTypeList = PathList.getStoreList(storeType)
        request.session['startTime'] = startTime
        request.session['endTime'] = endTime
        request.session['storeType'] = storeType
        request.session['storeTypeList'] = storeTypeList

        # startDate = parse_date(startTime)
        # endDate = parse_date(endTime)
        if startTime and endTime:
            if startTime >= endTime:
                errorMessage = "開始時間必須早於結束時間"
            else:
                if pictureType == BUY_WITH:
                    return redirect('/draw_buy_with/?step=select_tag')
                elif pictureType == PRODUCT_IN_PATH:
                    return redirect('/draw_product_in_path/?step=select_tag')
                elif pictureType == RFM:
                    return redirect('/rfm/?step=display_picture')
                elif pictureType == RFM_WITH_PRODUCT:
                    return redirect('/rfm_with_product/?step=select_tag')
        else:
            if pictureType == BUY_WITH:
                return redirect('/draw_buy_with/?step=select_tag')
            elif pictureType == PRODUCT_IN_PATH:
                return redirect('/draw_product_in_path/?step=select_tag')
            elif pictureType == RFM:
                return redirect('/rfm/?step=display_picture')
            elif pictureType == RFM_WITH_PRODUCT:
                return redirect('/rfm_with_product/?step=select_tag')

    if pictureType == PRODUCT_IN_PATH:
        return render(
            request,
            'Time.html',
            {
                # 'stores': stores,
                'startTime': selectedStartTime,
                'endTime': selectedEndTime,
                'errorMessage': errorMessage,
            }
        )
    else:
        return render(
            request, 'PathAndTime.html', {
                'stores': storeType,
                'startTime': selectedStartTime,
                'endTime': selectedEndTime,
                'pictureType': pictureType,
                'errorMessage': errorMessage,
            }
        )


def _selectTag(request, pictureType):
    bigTags = _filterBigTags(request)
    selectedBigTag = request.session.get('bigTag', '')
    selectedSmallTag = request.session.get('smallTag', '')
    selectedProduct = request.session.get('product', '')

    if request.method == 'POST':
        bigTag = request.POST.get('bigTag')
        smallTag = request.POST.get('smallTag')
        selectedProducts = request.POST.get('selectedProducts')
        if selectedProducts:
            # 將逗號分隔的產品列表轉為 Python 列表
            productList = selectedProducts.split(',')
            request.session['productList'] = productList
        # product = request.POST.get('product')
        request.session['bigTag'] = bigTag
        request.session['smallTag'] = smallTag

        if not smallTag:
            errorMessage = '請選擇子分類'
            return redirect(f'/draw_buy_with/?step=select_tag&error_message={errorMessage}')

        if pictureType == BUY_WITH:
            return redirect('/draw_buy_with/?step=display_picture')
        elif pictureType == PRODUCT_IN_PATH:
            return redirect('/draw_product_in_path/?step=display_picture')
        elif pictureType == RFM_WITH_PRODUCT:
            return redirect('/rfm_with_product/?step=display_picture')

    bigTags = _filterBigTags(request)
    if not bigTags:
        return redirect('/draw_buy_with/?step=select_path_time&error_message=此區間無資料，請重新選擇。')
    # errorMessage = request.GET.get('error_message', '')
    errorMessage = request.session.pop('error_message', '')
    return render(
        request, 'Tag.html', {
            'bigTags': bigTags,
            'bigTag': selectedBigTag,
            'smallTag': selectedSmallTag,
            'product': selectedProduct,
            'pictureType': pictureType,
            'errorMessage': errorMessage
        }
    )


def _displayPathPic(request):
    startTime = request.session.get('startTime', '')
    endTime = request.session.get('endTime', '')

    # 檢查是否為字串 'None'，並將其轉為 NoneType
    startTime = None if startTime == 'None' else startTime
    endTime = None if endTime == 'None' else endTime
    countyName = request.session.get('selectedCounty', '')
    district = request.session.get('selectedDistrict', '') # narrow down 才有
    smallTag = request.session.get('smallTag', '')
    productList = request.session.get('productList', '')
    # product = request.session.get('product', '')
    orderBy = request.GET.get('order_by', 'TOTAL_QUANTITY') # Get order by parameter
    df = _drawPic(request, countyName, smallTag, PRODUCT_IN_PATH, startTime, endTime, productList=productList)
    if df is not None:
        # Sort the dataframe
        # based on the selected option
        df = df.sort_values(by=orderBy, ascending=False)

        dfDict = {
            key: [float(value) if isinstance(value, Decimal) else value for value in values]
            for key, values in df.to_dict(orient='list').items()
        }

        topList = list(zip(dfDict['STORE_NAME'], dfDict[orderBy]))
        sortedList = sorted(topList, key=lambda x: x[1], reverse=True)

        topStores = [store for store, _ in sortedList[:10]]
        topValues = [value for _, value in sortedList[:10]]

        data = list(
            zip(
                dfDict.get('STORE_NAME', []), dfDict.get('TOTAL_QUANTITY', []), dfDict.get('TOTAL_PROFIT', []),
                dfDict.get('PROFIT_PER_UNIT', []), dfDict.get('NUMBER_OF_SALESRECORD', []),
                dfDict.get('PROFIT_PER_SALES', [])
            )
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'top_10_stores': topStores, 'top_10_quantities': topValues, 'data': data})

        # title = productList if productList else smallTag
        return render(
            request, 'ProductInPath.html', {
                'df': dfDict,
                'title': smallTag,
                'titleList': productList,
                'top_10_stores': topStores,
                'top_10_quantities': topValues,
                'data': data,
            }
        )
    else:
        messages.error(request, 'No data in your condition. Please try another one.')
        return _selectTag(request, PRODUCT_IN_PATH)


def _displayPic(request, pictureType, displayType=None):
    startTime = request.session.get('startTime', '')
    endTime = request.session.get('endTime', '')

    # 檢查是否為字串 'None'，並將其轉為 NoneType
    startTime = None if startTime == 'None' else startTime
    endTime = None if endTime == 'None' else endTime
    countyName = request.session.get('selectedCounty', '')
    if pictureType in (RFM_WITH_PRODUCT, RFM):
        segment = request.session.get('segment', 'Potential Loyalist')
    else:
        segment = request.session.get('segment', '')
    district = request.session.get('selectedDistrict', '') # narrow down 才有
    storeType = request.session.get('storeType', '')
    storeTypeList = request.session.get('storeTypeList', '')
    smallTag = request.session.get('smallTag', '')
    productList = request.session.get('productList', '')
    limit = request.session.get('limit', '')
    excludeDiscounts = False
    districtList = _filterDistrict(countyName)
    storesToQuery = storeTypeList
    # stores = _filterStores(districtName)
    if storeTypeList:
        storeCanBeChoose = _filterDistrictsStore(
            countyName=countyName, storeList=storeTypeList, itemTag=smallTag, product=productList
        )
    else:
        storeCanBeChoose = _filterDistrictsStore(
            countyName=countyName, storeList=storeTypeList, itemTag=smallTag, product=productList
        )
    if request.method == 'POST':
        startTime = request.POST.get('startTime', '')
        endTime = request.POST.get('endTime', '')

        # startTime = None if startTime == 'None' else startTime
        # endTime = None if endTime == 'None' else endTime

        district = request.POST.get('district')
        storesToQuery = request.POST.get('store')
        segment = request.POST.get('segment')
        limit = request.POST.get('limit')
        excludeDiscounts = True if request.POST.get("excludeDiscounts") == 'on' else None
        # districtName = District.objects.get(id=districtId).name
        request.session['startTime'] = startTime
        request.session['endTime'] = endTime
        request.session['selectedDistrict'] = district
        # request.session['districtName'] = districtName
        request.session['store'] = storesToQuery
        request.session['segment'] = segment
        request.session['limit'] = limit
        request.session['limexcludeDiscountsit'] = excludeDiscounts
        # request.session['selectedPath'] = pathId

    result = _drawPic(
        request,
        countyName,
        smallTag,
        pictureType,
        startTime,
        endTime,
        productList,
        storesToQuery,
        district, #narrow down
        segment,
        limit,
        excludedDiscounts=excludeDiscounts
    )

    if result is not None:

        relationship, articulationPoint, communities, df = result
        nodes, edges = _getNodeAndEdge(
            countyName,
            smallTag,
            startTime,
            endTime,
            productList,
            storesToQuery,
            district, #narrow down
            segment,
            limit,
            excludeDiscounts
        )

        if pictureType == BUY_WITH:
            options = set(df['ELEMENT1']).union(set(df['ELEMENT2']))

            return render(
                request, 'Display.html', {
                    'startTime': startTime,
                    'endTime': endTime,
                    'districtList': districtList,
                    'selectedPath': request.session.get('selectedPath', ''),
                    'displayType': displayType,
                    'stores': storeCanBeChoose,
                    'relationship': relationship,
                    'articulationPoint': articulationPoint,
                    'communities': communities,
                    'options': options,
                    'nodes': nodes,
                    'edges': edges,
                    'countyName': countyName,
                    'smallTag': smallTag,
                    'productList': productList,
                    'limit': limit,
                    "districtName": district,
                    'path': storesToQuery if not isinstance(storesToQuery, list) <= 1 else storeType,
                }
            )
        elif pictureType in (RFM, RFM_WITH_PRODUCT):
            options = set(df['ELEMENT1']).union(set(df['ELEMENT2']))
            return render(
                request, 'DisplayRFM.html', {
                    'startTime': startTime,
                    'endTime': endTime,
                    'districtList': districtList,
                    'selectedPath': request.session.get('selectedPath', ''),
                    'displayType': displayType,
                    'stores': storeCanBeChoose,
                    'relationship': relationship,
                    'articulationPoint': articulationPoint,
                    'communities': communities,
                    'options': options,
                    'nodes': nodes,
                    'edges': edges,
                    'segment': segment,
                    'selectedDistrict': district,
                    'countyName': countyName,
                    'smallTag': smallTag,
                    'productList': productList,
                    'limit': limit,
                    'path': storesToQuery if not isinstance(storesToQuery, list) <= 1 else storeType,
                }
            )
    else:
        if pictureType in [BUY_WITH, RFM_WITH_PRODUCT, PRODUCT_IN_PATH]:
            # error_message = request.session.pop('error_message', 'No data in your condition. Please try another one.')

            messages.error(request, 'No data in your condition. Please try another one.')
            return _selectTag(request, pictureType)
        if pictureType == RFM:
            messages.error(request, 'No data in your condition. Please try another one.')
            return _selectPathAndTime(request, pictureType)


def _drawPic(
    request,
    countyName,
    smallTag,
    pictureType,
    startTime=None,
    endTime=None,
    productList=None,
    storeTypeList=None,
    districtName=None,
    segment=None,
    limit=None,
    excludedDiscounts=None,
):
    if pictureType == PRODUCT_IN_PATH:
        network = ProductNetwork(username='admin', network_name='通路')
        if productList:
            df = network.get_channel_with_item_name(productList)
        else:
            df = network.get_channel_with_item_tag(smallTag)
        return df
    else:
        if not limit:
            #limit default value
            limit = 100
        network = ProductNetwork(username='admin', network_name='啤酒網路圖')
        try:
            df = network.query(
                county=countyName,
                city_area=districtName,
                item_tag=smallTag,
                datetime_lower_bound=startTime,
                datetime_upper_bound=endTime,
                store_brand_name=storeTypeList,
                item_name=productList,
                segment=segment,
                limit=limit,
                excludedDiscounts=excludedDiscounts
            )
            if df is not None:
                # network.execute_query()
                # network.analysis(limits=100)
                network.create_network()
                data = json_graph.node_link_data(network.g)
                if pictureType == RFM:
                    networkName = f'{countyName}/{segment}'
                elif pictureType == RFM_WITH_PRODUCT:
                    networkName = f'{countyName}/{segment}/{smallTag}'
                elif pictureType == BUY_WITH:
                    networkName = f'{countyName}/{smallTag}'
                request.session['network'] = {
                    'username': network.username,
                    'networkName': networkName,
                    'data': data,
                    'relationshipDF': network.relationship_df.to_json(orient='split')
                }
                relationship, articulationPoint, communities = network.vis_all_graph()
                return relationship, articulationPoint, communities, df
            else:
                request.session['error_message'] = 'No data in your condition. Please try another one.'
                return None

        except (psycopg2.ProgrammingError, ValueError) as e:
            # 將錯誤訊息存入 session
            request.session['error_message'] = 'No data in your condition. Please try another one.'
            return None

            # 根據 pictureType 返回適當的處理函數
        #     if pictureType in [BUY_WITH, RFM_WITH_PRODUCT, PRODUCT_IN_PATH]:
        #         return _selectTag(request, pictureType)
        #     elif pictureType == RFM:
        #         return _selectPathAndTime(request, pictureType)
        # return None


def _getNodeAndEdge(
    countyName,
    smallTag,
    startTime=None,
    endTime=None,
    productList=None,
    storeTypeList=None,
    districtName=None,
    segment=None,
    limit=None,
    excludeDiscounts=None
):

    if not limit:
        #limit default value
        limit = 100
    network = ProductNetwork(username='admin', network_name='啤酒網路圖')
    df = network.query(
        county=countyName,
        city_area=districtName,
        item_tag=smallTag,
        datetime_lower_bound=startTime,
        datetime_upper_bound=endTime,
        store_brand_name=storeTypeList,
        item_name=productList,
        segment=segment,
        limit=limit,
        excludedDiscounts=excludeDiscounts
    )
    # network.execute_query()
    # network.analysis(limits=100)
    network.create_network()
    network.vis_all_graph()
    nodes = network.get_nodes()
    edges = network.get_edges()
    return nodes, edges


def _clearSession(request):
    userSessionKeys = ['_auth_user_id', '_auth_user_backend', '_auth_user_hash']

    userSessionData = {key: request.session.get(key) for key in userSessionKeys}

    request.session.clear()

    for key, value in userSessionData.items():
        if value:
            request.session[key] = value


def drawBuyWith(request):
    displayType = request.GET.get('displayType', 'Regular')
    step = request.GET.get('step', 'select_area')
    pictureType = BUY_WITH
    clearSession = request.GET.get('clearSession', 'False') == 'True'

    if clearSession:
        _clearSession(request)

    if step == 'select_area':

        return _selectArea(request, pictureType)

    elif step == 'select_path_time':
        return _selectPathAndTime(request, pictureType)

    elif step == 'select_tag':
        return _selectTag(request, pictureType)

    elif step == 'display_picture':
        return _displayPic(request, pictureType, displayType)

    return redirect('/draw_buy_with/?step=select_area')


def showInfo(request):
    displayType = request.GET.get('displayType', 'Regular')
    content = ""

    if displayType == "Articulation Points":
        content = "Information about Articulation Points."
    elif displayType == "Community":
        content = "Information about Community."
    else:
        content = "Information about Regular."

    return JsonResponse({"content": content})


##防呆
##資料篩選
def drawPath(request):
    step = request.GET.get('step', 'select_area')
    pictureType = PRODUCT_IN_PATH
    clearSession = request.GET.get('clearSession', 'False') == 'True'

    if clearSession:
        _clearSession(request)

    if step == 'select_area':
        response = _selectArea(request, pictureType)

    elif step == 'select_time':
        response = _selectPathAndTime(request, pictureType)

    elif step == 'select_tag':
        response = _selectTag(request, pictureType)

    elif step == 'display_picture':
        response = _displayPathPic(request)

    else:
        response = redirect('/draw_product_in_path/?step=select_area')

    if response is None:
        print(f"drawPath returned None for step: {step}")
        return HttpResponse("An error occurred: No valid response was generated.", status=500)

    return response


def analyze(request):
    if request.method == 'POST':
        nodes = request.POST.get('nodes')
        edges = request.POST.get('edges')
        analysisType = request.POST.get('analysisType', '')
    
        if not nodes or not edges:
            return JsonResponse({'error': 'Missing nodes or edges'}, status=400)

        print('Nodes:', nodes)
        print('Edges:', edges)

        chatbot = Chatbot()

        if analysisType == 'regular':
            result = chatbot.generate_regular_analysis_q1(nodes, edges)
            #result += chatbot.generate_slogan(nodes, edges)
        elif analysisType == 'articulation':
            result = chatbot.generate_articulation_analysis_q1(nodes, edges)
        else:
            result = chatbot.generate_community_analysis_q1(nodes, edges)

        return JsonResponse({'analysis': result})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def analyzeq1(request):
    if request.method == 'POST':
        nodes = request.POST.get('nodes')
        edges = request.POST.get('edges')
        analysisType = request.POST.get('analysisType', '')
    
        if not nodes or not edges:
            return JsonResponse({'error': 'Missing nodes or edges'}, status=400)

        print('Nodes:', nodes)
        print('Edges:', edges)

        chatbot = Chatbot()

        if analysisType == 'regular':
            result = chatbot.generate_regular_analysis_q2(nodes, edges)
            #result += chatbot.generate_slogan(nodes, edges)
        elif analysisType == 'articulation':
            result = chatbot.generate_articulation_analysis_q2(nodes, edges)
        else:
            result = chatbot.generate_community_analysis_q2(nodes, edges)

        return JsonResponse({'analysis': result})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def analyzeq2(request):
    if request.method == 'POST':
        nodes = request.POST.get('nodes')
        edges = request.POST.get('edges')
        analysisType = request.POST.get('analysisType', '')
    
        if not nodes or not edges:
            return JsonResponse({'error': 'Missing nodes or edges'}, status=400)

        print('Nodes:', nodes)
        print('Edges:', edges)

        chatbot = Chatbot()

        if analysisType == 'regular':
            result = chatbot.generate_regular_analysis_q3(nodes, edges)
            #result += chatbot.generate_slogan(nodes, edges)
        elif analysisType == 'articulation':
            result =  '功能研發中^^'
        else:
            result = chatbot.generate_community_analysis_q3(nodes, edges)

        return JsonResponse({'analysis': result})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def analyzeq3(request):
    if request.method == 'POST':
        nodes = request.POST.get('nodes')
        edges = request.POST.get('edges')
        analysisType = request.POST.get('analysisType', '')
    
        if not nodes or not edges:
            return JsonResponse({'error': 'Missing nodes or edges'}, status=400)

        print('Nodes:', nodes)
        print('Edges:', edges)

        chatbot = Chatbot()

        if analysisType == 'regular':
            result = chatbot.generate_regular_analysis_q4(nodes, edges)
            #result += chatbot.generate_slogan(nodes, edges)
        elif analysisType == 'articulation':
            result =  '功能研發中^^'
        else:
            result = chatbot.generate_community_analysis_q4(nodes, edges)

        return JsonResponse({'analysis': result})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def analyzeq4(request):
    if request.method == 'POST':
        nodes = request.POST.get('nodes')
        edges = request.POST.get('edges')
        analysisType = request.POST.get('analysisType', '')
    
        if not nodes or not edges:
            return JsonResponse({'error': 'Missing nodes or edges'}, status=400)

        print('Nodes:', nodes)
        print('Edges:', edges)

        chatbot = Chatbot()

        if analysisType == 'regular':
            result = chatbot.generate_regular_analysis_q5(nodes, edges)
            #result += chatbot.generate_slogan(nodes, edges)
        elif analysisType == 'articulation':
            #result = chatbot.generate_articulation_analysis(nodes, edges)
            result = '功能研發中^^'
        else:
            result = chatbot.generate_community_analysis_q5(nodes, edges)

        return JsonResponse({'analysis': result})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def analyzeq5(request):
    if request.method == 'POST':
        nodes = request.POST.get('nodes')
        edges = request.POST.get('edges')
        analysisType = request.POST.get('analysisType', '')
    
        if not nodes or not edges:
            return JsonResponse({'error': 'Missing nodes or edges'}, status=400)

        print('Nodes:', nodes)
        print('Edges:', edges)

        chatbot = Chatbot()

        if analysisType == 'regular':
            #result = chatbot.generate_regular_analysis_q5(nodes, edges)
            result = chatbot.generate_slogan(nodes, edges)
        elif analysisType == 'articulation':
            result =  '功能研發中^^'
        else:
            result =  '功能研發中^^'

        return JsonResponse({'analysis': result})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def displayOvertime(request):
    return render(request, 'Overtime.html')


def getDeeperInsight(request):
    option = request.GET.get('deeperInsightSearch')
    startTime = request.session.get('startTime', '')
    endTime = request.session.get('endTime', '')
    # productList = request.session.get('productList', '')
    # 檢查是否為字串 'None'，並將其轉為 NoneType
    startTime = None if startTime == 'None' else startTime
    endTime = None if endTime == 'None' else endTime
    countyName = request.session.get('selectedCounty', '')
    storeTypeList = request.session.get('storeTypeList', '')
    small_tag = request.session.get('smallTag', '')
    product_list = request.session.get('productList', '')
    district = request.session.get('selectedDistrict', '')
    limit = request.session.get('limit', '')
    if not option:
        return redirect('/draw_buy_with/?step=display_picture')
    network = ProductNetwork(username='admin', network_name='啤酒網路圖')

    table = network.get_item_name(
        small_tag = small_tag,
        item_tag=option,
        product_list=product_list,
        datetime_lower_bound=startTime,
        datetime_upper_bound=endTime,
        store_brand_name=storeTypeList,
        county=countyName,
        city_area=district,
        limit=limit
    )

    context = {
        "option": option,
        'table': table,
    }
    return render(request, 'DeeperInsight.html', context)


def drawRFM(request):
    step = request.GET.get('step', 'select_area')
    pictureType = RFM
    clearSession = request.GET.get('clearSession', 'False') == 'True'

    if clearSession:
        _clearSession(request)
    displayType = request.GET.get('displayType', 'Regular')
    if step == 'select_area':
        return _selectArea(request, pictureType)

    elif step == 'select_path_time':
        return _selectPathAndTime(request, pictureType)

    elif step == 'display_picture':
        return _displayPic(request, pictureType, displayType)

    return redirect('/draw_buy_with/?step=select_area')


def drawRFMwithProduct(request):
    step = request.GET.get('step', 'select_area')
    pictureType = RFM_WITH_PRODUCT

    displayType = request.GET.get('displayType', 'Regular')
    clearSession = request.GET.get('clearSession', 'False') == 'True'

    if clearSession:
        _clearSession(request)

    if step == 'select_area':
        return _selectArea(request, pictureType)

    elif step == 'select_path_time':
        return _selectPathAndTime(request, pictureType)

    elif step == 'select_tag':
        return _selectTag(request, pictureType)

    elif step == 'display_picture':
        return _displayPic(request, pictureType, displayType)

    return redirect('/rfm_with_product/?step=select_area')


def displayBuyWithInPathNetworks(request, uu_ID):
    renderedHtml = cache.get(uu_ID)
    return render(
        request,
        'BuyWithInPath.html',
        {
            'relationship': renderedHtml['relationship'],
            'articulationPoint': renderedHtml['articulationPoint'],
            'communities': renderedHtml['communities'],
            'options': renderedHtml['options'],
            'nodes': renderedHtml['nodes'],
            'edges': renderedHtml['edges'],
            'countyName': renderedHtml['countyName'],
            'smallTag': renderedHtml['smallTag'],
            'store': renderedHtml['store'],
            'productList': renderedHtml['productList'],
            # 'displayType': displayType,
        }
    )


def displayBuyWithInPath(request):
    startTime = request.session.get('startTime', '')
    endTime = request.session.get('endTime', '')

    # 檢查是否為字串 'None'，並將其轉為 NoneType
    startTime = None if startTime == 'None' else startTime
    endTime = None if endTime == 'None' else endTime
    countyName = request.session.get('selectedCounty', '')
    #district = request.session.get('selectedDistrict', '') # narrow down 才有
    smallTag = request.session.get('smallTag', '')
    productList = request.session.get('productList', '')
    store = request.GET.get('store')
    displayType = request.GET.get('displayType', 'Regular')
    network = ProductNetwork(username='admin', network_name='啤酒網路圖')
    df = network.query(
        county=countyName,
        item_tag=smallTag,
        datetime_lower_bound=startTime,
        datetime_upper_bound=endTime,
        store_brand_name=store,
        item_name=productList,
        limit=100
    )
    if df is not None:
        # network.execute_query()
        # network.analysis(limits=100)
        network.create_network()
        data = json_graph.node_link_data(network.g)
        networkName = f'{countyName}/{smallTag}/{store}'
        request.session['network'] = {
            'username': network.username,
            'networkName': networkName,
            'data': data,
            'relationshipDF': network.relationship_df.to_json(orient='split')
        }
        relationship, articulationPoint, communities = network.vis_all_graph()
    else:
        return JsonResponse({'status': 'error', 'message': 'No data in your condition. Please try another one.'})

    # network.execute_query()
    # network.analysis(limits=100)

    network.create_network()
    relationship, articulationPoint, communities = network.vis_all_graph()
    options = set(df['ELEMENT1']).union(set(df['ELEMENT2']))
    nodes, edges = _getNodeAndEdge(countyName, smallTag, startTime, endTime, productList, store, limit=100)
    renderedHtml = render_to_string(
        'BuyWithInPath.html',
        {
            'relationship': relationship,
            'articulationPoint': articulationPoint,
            'communities': communities,
            'options': options,
            'nodes': nodes,
            'edges': edges,
            'countyName': countyName,
            'smallTag': smallTag,
            'store': store,
            'productList': productList
            # 'displayType': displayType,
        }
    )
    uu_ID = str(uuid.uuid4()) # 生成唯一 ID 用于识别缓存内容
    html = {
        'relationship': relationship,
        'articulationPoint': articulationPoint,
        'communities': communities,
        'options': options,
        'nodes': nodes,
        'edges': edges,
        'countyName': countyName,
        'smallTag': smallTag,
        'store': store,
        'productList': productList
    }

    # 将 HTML 内容存入缓存，设定一个过期时间（例如 300 秒）
    cache.set(uu_ID, html, timeout=300)

    redirect_url = reverse('main:displayBuyWithInPathNetworks', kwargs={'uu_ID': uu_ID})
    return JsonResponse({'status': 'success', 'redirect_url': redirect_url})


def saveData(request):
    if request.method == "POST":
        # 從 session 中取得 network
        network = request.session.get('network')
        if network:
            NetworkGraph.objects.create(
                name=network['networkName'],
                json=network['data'],
                user=request.user,
                csv=network['relationshipDF'],
            )
            return JsonResponse({"message": "Data saved successfully!"}, status=200)
        else:
            return JsonResponse({"message": "Data saved error, no network found!"}, status=400)
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)


def getStoredPicture(request):
    savedPictures = NetworkGraph.objects.filter(user=request.user)
    if savedPictures:
        return render(request, 'SavedPicture.html', {'pictures': savedPictures})
    else:
        message = "You have no saved pictures."
        return render(request, 'SavedPicture.html', {'message': message})


def loadPicture(request):
    if request.method == "POST":
        selectedPictures = request.POST.getlist('selectedPictures')

        if len(selectedPictures) == 2:
            pictures = NetworkGraph.objects.filter(id__in=selectedPictures)
            network1 = ProductNetwork(username='test', network_name=pictures[0].name)
            network1.load(pictures[0].json, pictures[0].csv)
            network2 = ProductNetwork(username='test', network_name=pictures[1].name)
            network2.load(pictures[1].json, pictures[1].csv)
            network1HTML, network2HTML, d1tod4 = compare_node(network1, network2)
            return render(
                request, 'CompareGraph.html', {
                    'network1HTML': network1HTML,
                    'network2HTML': network2HTML,
                    'd1': d1tod4[0],
                    'd2': d1tod4[1],
                    'd3': d1tod4[2],
                    'd4': d1tod4[3],
                    'network1': network1,
                    'network2': network2
                }
            )

        else:
            return HttpResponse("Error: You must select exactly two pictures.")
    else:
        return HttpResponse("Invalid request method.")


def deleteGraph(request):
    if request.method == "POST":
        data = json.loads(request.body) # 從 JSON 中取得 `pictureId`
        pictureId = data.get('pictureId')
        print(f"Received delete request for picture ID: {pictureId}") # 檢查是否接收到 `pictureId`

        try:
            picture = NetworkGraph.objects.get(id=pictureId, user=request.user)
            picture.delete()
            return JsonResponse({"message": "Picture deleted successfully!"}, status=200)
        except NetworkGraph.DoesNotExist:
            return JsonResponse({"message": "Picture not found."}, status=404)
    else:
        return JsonResponse({"message": "Invalid request method."}, status=405)
