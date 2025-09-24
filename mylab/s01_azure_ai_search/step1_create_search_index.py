# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: step1_create_search_index.py

DESCRIPTION:
    This script demonstrates how to generate an Azure AI Search index and related features.
    It creates a vector search index, prepares document data, uploads documents, and tests basic search functionality.

USAGE:
    python step1_create_search_index.py

    Before running the script:
    1. pip install azure-search-documents azure-identity python-dotenv
    2. Create a .env file with the following variables:
       - AZURE_SEARCH_ENDPOINT
       - AZURE_SEARCH_API_KEY (or AZURE_SEARCH_INDEX)
       - AZURE_SEARCH_INDEX (optional, defaults to "vector-search-quickstart")

STEPS PERFORMED:
    1. Initialize Azure Search client and credentials
    2. Create search index with vector search configuration
    3. Prepare hotel document data with embeddings
    4. Upload documents to the index
    5. Test basic search functionality (vector, hybrid, semantic)
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes.models import (
    SimpleField,
    ComplexField,
    SearchField,
    SearchFieldDataType,    
    SearchableField,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch, 
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    ExhaustiveKnnAlgorithmConfiguration    
)


def initialize_environment():
    """Initialize environment variables and credentials."""
    print("🔧 初始化環境變數和認證 / Initializing environment and credentials...")
    
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    index_name = os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart")
    
    # Use API key authentication (can be switched to DefaultAzureCredential if needed)
    credential = AzureKeyCredential(api_key)
    # credential = DefaultAzureCredential()  # Alternative authentication method
    
    print(f"✅ Azure Search 端點 / Endpoint: {search_endpoint}")
    print(f"✅ 索引名稱 / Index name: {index_name}")
    print(f"✅ 認證已設定 / Authentication configured")
    
    return search_endpoint, credential, index_name


def create_search_index(search_endpoint, credential, index_name):
    """Create a search index with vector search configuration."""
    print("\n📋 建立搜索索引 / Creating search index...")
    
    # Create a search index client
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    
    # Define the index fields
    fields = [
        SimpleField(name="HotelId", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="HotelName", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="Description", type=SearchFieldDataType.String),
        SearchField(
            name="DescriptionVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="my-vector-profile"
        ),
        SearchableField(name="Category", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
        SearchField(name="Tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True, filterable=True, facetable=True),
        SimpleField(name="ParkingIncluded", type=SearchFieldDataType.Boolean, filterable=True, sortable=True, facetable=True),
        SimpleField(name="LastRenovationDate", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True, facetable=True),
        SimpleField(name="Rating", type=SearchFieldDataType.Double, filterable=True, sortable=True, facetable=True),
        ComplexField(name="Address", fields=[
            SearchableField(name="StreetAddress", type=SearchFieldDataType.String),
            SearchableField(name="City", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
            SearchableField(name="StateProvince", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
            SearchableField(name="PostalCode", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
            SearchableField(name="Country", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        ]),
        SimpleField(name="Location", type=SearchFieldDataType.GeographyPoint, filterable=True, sortable=True),
    ]

    # Configure vector search algorithms and profiles
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="my-hnsw-vector-config-1", kind="hnsw"),
            ExhaustiveKnnAlgorithmConfiguration(name="my-eknn-vector-config", kind="exhaustiveKnn")
        ],
        profiles=[
            VectorSearchProfile(name="my-vector-profile", algorithm_configuration_name="my-hnsw-vector-config-1")
        ]
    )

    # Configure semantic search
    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
           title_field=SemanticField(field_name="HotelName"), 
           content_fields=[SemanticField(field_name="Description")], 
           keywords_fields=[SemanticField(field_name="Category")]
        )
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index
    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    
    print(f"✅ 索引建立成功 / Index '{result.name}' created successfully")
    return index_client


def prepare_hotel_documents():
    """Prepare hotel document data with embeddings."""
    print("\n📝 準備酒店文檔數據 / Preparing hotel document data...")
    
    # Sample hotel documents with pre-computed embeddings
    documents = [
        {
            "@search.action": "mergeOrUpload",
            "HotelId": "1",
            "HotelName": "Stay-Kay City Hotel",
            "Description": "This classic hotel is fully-refurbished and ideally located on the main commercial artery of the city in the heart of New York. A few minutes away is Times Square and the historic centre of the city, as well as other places of interest that make New York one of America's most attractive and cosmopolitan cities.",
            "DescriptionVector": [-0.048865054,-0.020307425,0.017633565,0.023875887,-0.04401433,-0.021689085,-0.04437217,0.011500583,0.03840817,0.00029058976,0.016907945,-0.009214383,-0.04512761,0.019889945,0.020973407,0.023040926,-0.026539808,0.050495215,0.07152826,-0.008786962,-0.009994673,-0.0053129313,-0.014601864,-0.048069853,0.021231845,0.022066806,-0.018021226,-0.010526463,0.07220418,0.0068685417,0.009472823,-0.023239726,0.040276892,0.03399481,0.0156058045,-0.001837658,-0.009567252,-0.03630089,0.009010613,0.027672967,-0.023398766,0.030078448,0.018428765,-0.006709502,-0.03598281,-0.018021226,-0.017782666,0.06655826,-0.019909825,0.010963823,-0.028428407,0.007325782,-0.030833889,-0.045724012,-0.0780489,0.024253607,0.018220024,-0.022762606,0.056777295,0.007817812,0.03355745,0.029163968,0.031967048,0.029959168,-0.051568735,0.057294175,-0.0156157445,0.03759309,-0.046002332,-0.020396886,0.053278416,0.016371185,0.03170861,-0.015685324,0.0010555041,0.024094567,0.0051886817,0.012872304,0.004055521,-0.03315985,-0.013568103,-0.023359006,-0.072243944,0.026480168,0.025068687,0.009010613,-0.018090805,-0.025207847,0.009408212,0.0025123358,0.024591567,-0.003725016,-0.0053924513,-0.025227727,-0.055385694,0.012136743,-0.011709323,-0.041310653,-0.021828245,0.04373601,0.030217608,0.023199966,-0.012912064,0.020277606,0.021609565,-0.031887528,0.014164504,-0.062264178,0.03315985,0.0034218458,-0.07550426,0.007653802,-0.04544569,-0.030973049,-0.0029298158,0.041708253,0.053198896,-0.03379601,-0.010834603,0.025168087,-0.031569447,-0.023836127,-0.025088567,-0.009935033,0.0017009829,-0.03395505,0.03174837,-0.030814009,-0.0155958645,-0.0030192758,0.009477792,-0.024830127,-0.046757773,0.0055216714,-0.015069044,0.024015047,0.015735025,-0.020655327,-0.020357126,0.015287724,0.003705136,-0.03389541,-0.026142208,-0.041390173,-0.03705633,0.06818842,0.03186765,0.007181652,-0.012802724,0.030694729,0.025366887,0.064729296,0.029680848,-0.011639743,-0.0016351305,0.0029944258,0.021788485,-0.017921826,-0.03486953,0.040992573,-0.021629445,0.03576413,-0.07232346,0.004868116,0.055783294,0.031112209,-0.046121612,-0.049262654,-0.04500833,-0.023021046,0.03538641,-0.020536046,0.006500762,0.031808008,0.03359721,0.052920576,-0.017812485,-0.014949764,0.028845888,0.019780606,0.019999286,-0.020874007,0.0865973,-0.057691775,0.019442646,0.03190741,-0.079122424,0.046519212,0.018170325,0.012196383,0.013448824,0.009865453,-0.0850069,0.0057204715,-0.03270261,0.051727775,-0.03242429,-0.041151613,0.012902124,0.0003308157,-0.011937943,0.0045102765,0.018617624,-0.016401004,-0.018369125,0.009716352,0.0052185017,-0.024850007,0.019880006,0.03294117,-0.004353721,-0.04373601,0.019134505,0.0693017,-0.016222084,-0.03570449,-0.050018094,0.003702651,-0.028448287,0.047791533,0.00023576444,0.0012723204,0.0047712014,0.028030807,-0.026162088,0.06846674,-0.0069281817,-0.025963288,-0.004067946,0.011848483,0.0010604741,-0.013090984,-0.024174087,-0.029541688,-0.014224144,0.04238417,0.007236322,0.0034392409,-0.03447193,-0.013001524,-0.03357733,0.007017642,-0.008697502,0.011450883,0.030058568,-0.019154385,-0.014104864,-0.022822246,-0.011013523,0.024631327,-0.0059391516,0.03238453,0.03644005,-0.028925408,0.020774607,-0.0029447258,0.0016053105,0.015426884,0.041946813,0.025426527,0.019094745,-0.000408472,0.056061614,-0.024492167,-0.012385244,-0.046996333,-0.054868814,0.030694729,0.00025517851,-0.059918337,-0.045843292,0.0029571508,-0.0068486617,-0.03745393,0.03638041,-0.031092329,0.0055167014,0.000035877198,-0.042145614,-0.0138861835,-0.022086686,-0.03785153,0.07232346,-0.013031344,-0.018657384,-0.006461002,-0.013826543,0.029422408,-0.023716846,0.007141892,-0.0025309732,0.0026788306,0.011659623,-0.03838829,-0.00011531956,-0.007922182,0.022881886,-0.06938122,0.002265078,-0.0021681632,-0.023736726,0.0750669,0.03610209,-0.014820544,-0.018041106,0.061429217,0.003287656,-0.029800128,0.020436646,0.022941526,-0.0022812306,0.020237846,-0.019184206,-0.0716873,-0.022066806,-0.039879292,0.014701264,-0.0058447216,-0.032245368,0.0060137017,0.010049343,-0.021470405,-0.0050147315,0.007718412,0.057413455,-0.023657206,0.011798783,0.025943408,-0.009199472,-0.0021818306,0.040952813,-0.032682728,0.018190205,-0.0026639206,0.022444526,0.016629625,-0.015466644,-0.014800664,0.024512047,0.0016475555,0.014512404,-0.058327936,-0.012653624,-0.010049343,0.064331695,-0.025983168,-0.010337603,-0.017971525,-0.013677443,-0.010993643,-0.056817055,-0.027593447,-0.009542403,0.010009583,0.014422944,0.014850364,0.007609072,0.054550733,-0.011073163,0.039839532,-0.024452407,-0.024929527,0.017822426,-0.007151832,0.014760904,0.007256202,-0.045724012,0.009646772,-0.027692847,0.017395005,-0.007678652,0.0056459215,0.013220204,0.009607012,-0.064013615,0.017116684,-0.001591643,0.008886362,-0.04234441,-0.041310653,-0.0020849155,-0.04294081,0.013478644,-0.028388647,-0.010526463,0.022265606,-0.004798536,-0.014870244,-0.027573567,0.057015855],
            "Category": "Boutique",
            "Tags": ["view", "air conditioning", "concierge"],
            "ParkingIncluded": "false",
            "LastRenovationDate": "2022-01-18T00:00:00Z",
            "Rating": 3.60,
            "Address": {
                "StreetAddress": "677 5th Ave",
                "City": "New York",
                "StateProvince": "NY",
                "PostalCode": "10022",
                "Country": "USA"
            },
            "Location": {"type": "Point", "coordinates": [-73.975403, 40.760586]}
        },
        {
            "@search.action": "mergeOrUpload",
            "HotelId": "2",
            "HotelName": "Old Century Hotel",
            "Description": "The hotel is situated in a nineteenth century plaza, which has been expanded and renovated to the highest architectural standards to create a modern, functional and first-class hotel in which art and unique historical elements coexist with the most modern comforts. The hotel also regularly hosts events like wine tastings, beer dinners, and live music.",
            "DescriptionVector": [-0.04683398,-0.01285595,0.03386663,-0.015239983,-0.0033393162,-0.014727527,-0.012042706,-0.011630513,0.0024954358,-0.037431534,0.006550519,0.021155503,-0.06024695,-0.036050133,0.0026764662,0.036094695,-0.06069256,0.014025685,0.052270465,0.01747919,-0.020620765,-0.017501472,-0.04121925,-0.07085255,0.01518428,0.013591212,-0.06412379,0.050488014,0.020865854,0.05596906,-0.001694724,-0.020999538,0.0724122,0.038099956,-0.023907166,-0.055077832,0.015050597,0.011842179,0.0164877,0.014359896,-0.032730315,0.012087267,0.01220981,-0.011463407,-0.00083482906,-0.027271548,-0.024285937,0.049953274,-0.0077592456,0.0072412197,-0.04284574,0.006394554,-0.0024355564,-0.0005716386,-0.039369956,0.035426274,-0.008778586,-0.04821538,0.057439584,0.011274022,0.055612568,0.0020456447,0.06715396,0.016209193,-0.06875817,0.031839088,-0.026491724,0.029811544,0.016342876,-0.009335604,0.038345043,0.036339782,-0.0041637016,-0.043313634,-0.03622838,-0.026825935,0.0059099495,-0.00022872507,-0.004712363,0.015540771,-0.066619225,-0.00857806],
            "Category": "Boutique",
            "Tags": ["pool", "free wifi", "air conditioning", "concierge"],
            "ParkingIncluded": "false",
            "LastRenovationDate": "2019-02-18T00:00:00Z",
            "Rating": 3.60,
            "Address": {
                "StreetAddress": "140 University Town Center Dr",
                "City": "Sarasota",
                "StateProvince": "FL",
                "PostalCode": "34243",
                "Country": "USA"
            },
            "Location": {"type": "Point", "coordinates": [-82.452843, 27.384417]}
        },
        {
            "@search.action": "mergeOrUpload",
            "HotelId": "3",
            "HotelName": "Gastronomic Landscape Hotel",
            "Description": "The Gastronomic Hotel stands out for its culinary excellence under the management of William Dough, who advises on and oversees all of the Hotel's restaurant services.",
            "DescriptionVector": [-0.015674675,0.030844409,0.00871766,0.0074618403,0.0076239295,0.025871232,0.0069496883,-0.037806276,0.016780032,0.010506701,0.030709885,0.055026546,0.004032529,0.013074103,-0.013885983,0.05354936,-0.02086637,-0.018761648,-0.006327094,0.008717659,-0.03148988,0.017485317,0.018842187,-0.035688713,-0.028041832,-0.029374013,-0.037033077,-0.038713764,0.065806784,-0.04308096,-0.025154227,0.014151593,0.043166354,0.035930764,-0.020275777,-0.026590498,0.008040675,0.001792119,0.027953455,0.023830028,-0.025503797,0.007998721],
            "Category": "Resort and Spa",
            "Tags": ["restaurant", "spa", "pool"],
            "ParkingIncluded": "true",
            "LastRenovationDate": "2015-09-20T00:00:00Z",
            "Rating": 4.8,
            "Address": {
                "StreetAddress": "3393 Peachtree Rd",
                "City": "Atlanta",
                "StateProvince": "GA",
                "PostalCode": "30326",
                "Country": "USA"
            },
            "Location": {"type": "Point", "coordinates": [-84.384109, 33.840703]}
        }
    ]
    
    print(f"✅ 已準備 {len(documents)} 個酒店文檔 / Prepared {len(documents)} hotel documents")
    return documents


def upload_documents(search_endpoint, credential, index_name, documents):
    """Upload documents to the search index."""
    print(f"\n📤 上傳文檔到索引 / Uploading documents to index '{index_name}'...")
    
    # Create a search client
    search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=credential)
    
    # Upload documents
    result = search_client.upload_documents(documents=documents)
    
    upload_success = 0
    for res in result:
        if res.succeeded:
            upload_success += 1
        else:
            print(f"❌ 上傳失敗 / Upload failed for document {res.key}: {res.error_message}")
    
    print(f"✅ 成功上傳 {upload_success} 個文檔 / Successfully uploaded {upload_success} documents")
    return search_client


def test_basic_search(search_client):
    """Test basic search functionality."""
    print(f"\n🔍 測試基本搜索功能 / Testing basic search functionality...")
    
    try:
        # Test 1: Simple text search
        print("\n📝 測試 1: 簡單文字搜索 / Test 1: Simple text search")
        results = search_client.search(search_text="boutique hotel", top=3)
        
        count = 0
        for result in results:
            count += 1
            print(f"  - {result['HotelName']} (評分: {result['Rating']})")
            
        if count > 0:
            print(f"✅ 文字搜索成功，找到 {count} 個結果 / Text search successful, found {count} results")
        else:
            print("⚠️  文字搜索沒有結果 / No text search results")
            
        # Test 2: Vector search (with example vector - shortened for demo)
        print("\n🔍 測試 2: 向量搜索 / Test 2: Vector search")
        sample_vector = [-0.048865054,-0.020307425,0.017633565,0.023875887,-0.04401433] + [0.0] * 1531  # Padded to 1536 dimensions
        
        vector_query = VectorizedQuery(vector=sample_vector, k_nearest_neighbors=3, fields="DescriptionVector")
        results = search_client.search(search_text=None, vector_queries=[vector_query])
        
        count = 0
        for result in results:
            count += 1
            print(f"  - {result['HotelName']} (相似度分數: {result['@search.score']:.4f})")
            
        if count > 0:
            print(f"✅ 向量搜索成功，找到 {count} 個結果 / Vector search successful, found {count} results")
        else:
            print("⚠️  向量搜索沒有結果 / No vector search results")
            
        # Test 3: Filter search
        print("\n🏷️  測試 3: 篩選搜索 / Test 3: Filter search")
        results = search_client.search(search_text="*", filter="Category eq 'Boutique'", top=5)
        
        count = 0
        for result in results:
            count += 1
            print(f"  - {result['HotelName']} (類別: {result['Category']})")
            
        if count > 0:
            print(f"✅ 篩選搜索成功，找到 {count} 個精品酒店 / Filter search successful, found {count} boutique hotels")
        else:
            print("⚠️  篩選搜索沒有結果 / No filter search results")
            
    except Exception as e:
        print(f"❌ 搜索測試失敗 / Search test failed: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to execute all steps."""
    print("🚀 開始執行步驟 1: 建立 AI Search 索引和相關功能")
    print("🚀 Starting Step 1: Generate AI Search Index and Related Features")
    print("=" * 80)
    
    try:
        # Step 1: Initialize environment
        search_endpoint, credential, index_name = initialize_environment()
        
        # Step 2: Create search index
        index_client = create_search_index(search_endpoint, credential, index_name)
        
        # Step 3: Prepare document data
        documents = prepare_hotel_documents()
        
        # Step 4: Upload documents
        search_client = upload_documents(search_endpoint, credential, index_name, documents)
        
        # Step 5: Test basic search functionality
        test_basic_search(search_client)
        
        print(f"\n🎉 步驟 1 完成！/ Step 1 completed successfully!")
        print(f"📝 索引名稱 / Index name: {index_name}")
        print(f"📝 端點 / Endpoint: {search_endpoint}")
        print(f"📝 已準備好用於 AI Agent 整合 / Ready for AI Agent integration")
        
        # Return important information for next steps
        return {
            "index_name": index_name,
            "search_endpoint": search_endpoint,
            "credential": credential,
            "success": True
        }
        
    except Exception as e:
        print(f"\n❌ 步驟 1 失敗 / Step 1 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = main()
    
    if result["success"]:
        print(f"\n✅ 腳本執行成功 / Script executed successfully")
        print(f"🔗 下一步：運行 step2_create_ai_agent.py 來創建 AI Agent")
        print(f"🔗 Next: Run step2_create_ai_agent.py to create AI Agent")
    else:
        print(f"\n❌ 腳本執行失敗 / Script execution failed")
        exit(1)