'''
59 columns
add "majors/" to URL to get to majors page
data file format:
	attributes seperated by comma and ending in ;\n
	spaces relaced with dashes
'''

import time
from pprint import pprint
import requests
from bs4 import BeautifulSoup
from progressbar import ProgressBar


response = requests.get(
    "https://www.niche.com/colleges/search/best-colleges-for-computer-science/?type=private&type=public", headers={"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})
soup = BeautifulSoup(response.content, "html.parser")
if response.status_code > 299:
	print("shit")
pprint(response.status_code)



# data collection
atributes={
	"name":0,
	"niche-url-name":1,
	"religious-affiliation":2,
	"city":3,
	"state":4,
	"niche-grade":5,
	"sat-consideration":6,
	"gpa-consideration":7,
	"first-descriptive-student-word":8,
	"second-descriptive-student-word":9,
	"third-descriptive-student-word":10,
	"first-descriptive-college-word":11,
	"second-descriptive-college-word":12,
	"third-descriptive-college-word":13,
	"academics-grade":14,
	"value-grade":15,
	"campus-grade":16,
	"party-scene-grade":17,
	"location-grade":18,
	"campus-food-grade":19,
	"safety-grade":20,
	"professors-grade":21,
	"dorms-grade":22,
	"student-life-grade":23,
	"price":24,
	"num-of-students":25,
	"num-of-comp-sci-students":26,
	"city-size?":27,
	"comp-sci-rank":28,
	"num-of-reviews":29,
	"athletic-division":30,
	"acceptance-rate":31,
	"sat-min":32,
	"sat-max":33,
	"application-fee":34,
	"%-receiving-aid":35,
	"avg-aid":36,
	"student-faculty-ratio":37,
	"num-of-descriptive-student-word-responses":38,
	"%-point-differential-for-first-and-second-student-words":39,
	"num-of-descriptive-college-word-responses":40,
	"%-point-differential-for-first-and-second-college-words":41,
	"%-live-on-campus":42,
	"graduation-rate":43,
	"2-yr-employment":44,
	"median-earnings-6-yrs-after":45,
	"%-confident-they-can-find-a-job":46,
	"num-of-responses-to-confidence-finding-job":47,
	"%-of-1-star-reviews":48,
	"%-of-2-star-reviews":49,
	"%-of-3-star-reviews":50,
	"%-of-4-star-reviews":51,
	"%-of-5-star-reviews":52,
	"star-rating":53,
	"4-yr":54,
	"early-decision":55,
	"SAT-in-range":56,
	"SAT-at-least":57,
	"comp-sci-in-top-5":58
}

links=[]
pages_num = int(soup.find_all("button", "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-sizeMedium MuiPaginationItem-text MuiPaginationItem-circular MuiPaginationItem-textPrimary MuiPaginationItem-page css-c17ou6")[-1].text)
results_num = int(soup.find("p", "MuiTypography-root MuiTypography-body2 search-result-count-text css-1l1273x").string[7:13].replace(",",""))


# rate_wait=3
# status=200
# for num in range(pages_num):
# 	url = f"https://www.niche.com/colleges/search/best-colleges-for-computer-science/?type=private&type=public&page={num}"
# 	if num==0:
# 		url = "https://www.niche.com/colleges/search/best-colleges-for-computer-science/?type=private&type=public"
# 	time.sleep(rate_wait)
# 	ranking_page = requests.get(url, headers={
# 	                          "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})
# 	ranking_soup = BeautifulSoup(ranking_page.content, "html.parser")
# 	status=ranking_page.status_code
# 	if rate_wait>16:
# 		print("too many rate limits")
# 		print("rate wait:",rate_wait)
# 		break
# 	elif status == 429:
# 		rate_wait*=2
# 		print("Rate-limited")
# 		print(f"Waiting {rate_wait} seconds between requests")
# 	elif status==403:
# 		print("SHIT!!!!!")
# 		print("CODE 403 FORBIDDEN")
# 		break
# 	elif status==404:
# 		print("404 page not found")
# 		print(f"page that was tried:{url}")
# 		continue
# 	link = ranking_soup.find_all(
# 		"a", "MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineNone search-result__link css-1dbsl7y")
# 	for i in link:
# 		links.append(i.get("href"))
# 		print(i.get("href"))
# 	if num>=10:
# 		break
# print("DONE")
