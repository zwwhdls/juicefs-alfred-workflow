import http.client
import json
import uuid
import os.path
import sys
import unicodedata
import urllib.parse, urllib.error

from payload import Payload
from search_result import SearchResult

indexName = "crawler_JuiceFS"
appId = "9P43LZLS0G"
apiKey = os.getenv("API_KEY")
language = os.getenv("LANGUAGE", "en")
hitsPerPage = int(os.getenv("HITS_PER_PAGE", 10))

doc_tags = {
    "ce": "docs-community-current",
    "ee": "docs-default-current",
    "csi": "docs-csi-current"
}


def build_juicefs_query(doc_tag, data):
    query = {"requests": []}
    req = {}

    req["query"] = data
    req["indexName"] = indexName
    params = {
        "attributesToRetrieve": '["hierarchy.lvl0","hierarchy.lvl1","hierarchy.lvl2","hierarchy.lvl3","hierarchy.lvl4","hierarchy.lvl5","hierarchy.lvl6","content","type","url"]',
        "attributesToSnippet": '["hierarchy.lvl1:10","hierarchy.lvl2:10","hierarchy.lvl3:10","hierarchy.lvl4:10","hierarchy.lvl5:10","hierarchy.lvl6:10","content:10"]',
        "hitsPerPage": hitsPerPage,
        "facetFilters": f'["language:{language}",["docusaurus_tag:{doc_tags[doc_tag]}"]]',
        "snippetEllipsisText": "…",
        "advancedSyntax": "true",
        "clickAnalytics": "false",
        "analytics": "false",
    }
    encoded_params = urllib.parse.urlencode(params)
    req["params"] = encoded_params
    query["requests"].append(req)

    jsonData = json.dumps(query)
    return jsonData


def create_title(hit):
    if hit.get("type") == "content":
        return hit.get("content")
    return hit.get("hierarchy").get(hit.get("type"))


def create_subtitle_chain(hit):
    lvl0 = hit.get("hierarchy").get("lvl0")
    lvl1 = hit.get("hierarchy").get("lvl1")
    lvl2 = hit.get("hierarchy").get("lvl2")
    lvl3 = hit.get("hierarchy").get("lvl3")
    lvl4 = hit.get("hierarchy").get("lvl4")
    lvl5 = hit.get("hierarchy").get("lvl5")
    lvl6 = hit.get("hierarchy").get("lvl6")
    if lvl0 is None:
        return ""
    if lvl1 is None:
        return f"{lvl0}"
    if lvl2 is None:
        return f"{lvl0}/{lvl1}"
    if lvl3 is None:
        return f"{lvl0}/{lvl1}/{lvl2}"
    if lvl4 is None:
        return f"{lvl0}/{lvl1}/{lvl2}/{lvl3}"
    if lvl5 is None:
        return f"{lvl0}/{lvl1}/{lvl2}/{lvl3}/{lvl4}"
    if lvl6 is None:
        return f"{lvl0}/{lvl1}/{lvl2}/{lvl3}/{lvl4}/{lvl5}"
    return f"{lvl0}/{lvl1}/{lvl2}/{lvl3}/{lvl4}/{lvl5}/{lvl6}"


# Get query from Alfred
docTag = str(sys.argv[1])
alfredQuery = str(sys.argv[2])
# alfredQuery = unicodedata.normalize('NFC', alfredQuery)

searchResultList = []
exception = ""
raw = {}
# If no query is provided and we're able to get the userId from the cookie env variable, show recently viewed notion pages.
# Else show notion search results for the query given
try:
    headers = {"Content-type": "application/json", "charset": "utf-8"}
    conn = http.client.HTTPSConnection("9p43lzls0g-1.algolianet.com")
    encoded_params = urllib.parse.urlencode({
        "x-algolia-agent": "juicefs-alfred-workflow",
        "x-algolia-api-key": apiKey,
        "x-algolia-application-id": appId,
    })
    path = f"/1/indexes/*/queries?{encoded_params}"
    conn.request("POST", path, build_juicefs_query(docTag, alfredQuery), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()

    # Extract search results
    searchResults = Payload(data)
    first = searchResults.results[0]
    raw = json.dumps(first, indent=4)
    for x in first.get("hits"):
        searchResultObject = SearchResult()
        searchResultObject.title = create_title(x)
        searchResultObject.subtitle = create_subtitle_chain(x)
        searchResultObject.link = x.get("url")
        searchResultObject.action = {
            "url": x.get("url"),
        }
        searchResultList.append(searchResultObject)
except Exception as e:
    trace_back = sys.exc_info()[2]
    line = trace_back.tb_lineno
    exception = str(line) + ": " + str(e)

itemList = []
for searchResultObject in searchResultList:
    item = {}
    item["type"] = "default"
    item["title"] = searchResultObject.title
    item["arg"] = searchResultObject.link
    item["subtitle"] = searchResultObject.subtitle
    item["autocomplete"] = searchResultObject.title
    item["action"] = searchResultObject.action
    item["valid"] = True
    itemList.append(item)

if exception:
    item = {}
    item["uid"] = 1
    item["title"] = "There was an error:"
    item["subtitle"] = str(exception)
    item["arg"] = "juicefs.com"
    itemList.append(item)

if not itemList:
    item = {}
    item["uid"] = 1
    item["title"] = "Open JuiceFS - No results, empty query, or error"
    item["subtitle"] = " "
    item["arg"] = "juicefs.com"
    itemList.append(item)

items = {}
items["items"] = itemList
# items["raw"] = raw
items["query"] = alfredQuery
items["doc"] = docTag
items_json = json.dumps(items, indent=4)
sys.stdout.write(items_json)
