from urllib.request import urlopen

#target webpage
url = "https://www.ultimate-guitar.com/top/tabs"

page = urlopen(url)
print("Opened page")
#print(f"Page is stored as {page}")

htmlRaw = page.read()
print("Read page contents")
#print(f"Contents stored as {htmlRaw}")

htmlParsed = htmlRaw.decode("utf-8")
print("Page contents decoded in utf-8")
#print(f"Contents stored as {htmlParsed}")

#html code is stored as a string, so standard string methods can be used
dataStart = htmlParsed.find("<div class=\"js-store\"")
dataEnd = htmlParsed.find("</div>", dataStart)
print(f"data starts at index {dataStart} and ends at index {dataEnd}")
data = htmlParsed[dataStart:dataEnd]
#print(data)

#start refining data
data = data.replace("&quot;","")
#print(data)
data = data.replace("{","\n")
#print(data)
dataStart = data.find("tabs:[\n")
dataEnd = data.find("],current_type:all", dataStart)
data = data[dataStart:dataEnd]
print(data)