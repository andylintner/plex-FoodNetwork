import re, urllib
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

WEB_ROOT = 'http://www.foodnetwork.com'
VID_PAGE = 'http://www.foodnetwork.com/video-library/index.html'

CACHE_INTERVAL = 3600 * 6

####################################################################################################
def Start():
  Plugin.AddPrefixHandler("/video/foodNetwork", MainMenu, 'Food Network', 'icon-default.jpg', 'art-default.jpg')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = 'Food Network'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
def MainMenu():
  dir = MediaContainer()
  page = XML.ElementFromURL(VID_PAGE, cacheTime=1200, isHTML=True)
  for tag in page.xpath("//div[@id='vid-channels']/ul/li"):
	title = tag.xpath("./h4")[0].text.strip()
	channel_id = tag.xpath("./div")[0].get('id')
	dir.Append(Function(DirectoryItem(ShowBrowse, title=title), channel_id=channel_id, title=title))
  
  return dir

####################################################################################################
def ShowBrowse(sender, channel_id, title = None):
    page = XML.ElementFromURL(VID_PAGE, cacheTime=1200, isHTML=True)

    dir = MediaContainer(title2=title)
    for tag in page.xpath("//div[@id='"+channel_id+"']//a[@class='frame']"):
		thumb = tag.xpath("./img")[0].get('src')
		root = tag.xpath("./..//a")[1]
		title = root.text.strip()
		url = root.get('href')
		try:
			duration = root.xpath("../span")[0].text
		except:
			duration = None
		if duration:
			duration = GetDurationFromDesc(duration)			
		dir.Append(WebVideoItem(WEB_ROOT+url, title, thumb=thumb, duration=duration))
	
    
    return dir
    
####################################################################################################
def CreateVideo(tag):
    url = tag.xpath(".//div[@class='browse-desc']/div//a")[0].get('href')
    return WebVideoItem(WEB_ROOT+url, GetTitle(tag), thumb=GetThumb(tag), summary=GetSummary(tag), subtitle=GetSubtitle(tag))

####################################################################################################
def CreateCategory(tag):
    url =  tag.xpath(".//div[@class='browse-desc']/div//a")[0].get('onclick')
    urlParts = re.match("doSearch\('([^']*)','([^']*)", url)
    url = urlParts.group(1) + urllib.quote_plus(urlParts.group(2))
    title = GetTitle(tag)
    return Function(DirectoryItem(Browse, title=title, thumb=GetThumb(tag)), url=WEB_ROOT+'/'+url, title=title)

####################################################################################################
def GetTitle(tag):
    title = tag.xpath(".//div[@class='browse-desc']/div//a")[0].text
    if not title:
        title = tag.xpath(".//div[@class='browse-desc']/div//a")[0].tail
    title = title.strip()
    return title

####################################################################################################    
def GetThumb(tag):
    return WEB_ROOT+tag.xpath(".//div[@class='thumb-image']/a/img")[0].get('src')

####################################################################################################    
def GetSubtitle(tag):
    try:
      return tag.xpath(".//div[@class='browse-desc']//span[@class='browse-subject']")[0].text.replace('Subject: ','')
    except:
      return ""

####################################################################################################    
def GetSummary(tag):
    try:
      list = [text for text in tag.xpath(".//div[@class='browse-desc']")[0].itertext()]
      Log(list)
      if len(list) > 2:
        return list[2].strip()
    except:
      raise
    
####################################################################################################    
def AddPager(page, dir, pageTitle):
    next = page.xpath("//span[@class='nav-pagination']/a[@class='current']/following-sibling::a")
    if next:
        next = next[0]
        url = next.get('href')
        dir.Append(Function(DirectoryItem(Browse, title=L("Next Page...")), url=url, title=pageTitle, replaceParent=True))
    prev = page.xpath("//span[@class='nav-pagination']/a[@class='current']/preceding-sibling::a")
    if prev:
        prev = prev[0]
        url = prev.get('href')
        dir.Append(Function(DirectoryItem(Browse, title=L("Previous Page...")), url=url, title=pageTitle, replaceParent=True))
        
####################################################################################################
def Search(sender, query):
    return Browse(sender, SEARCH_PAGE, title="Search Results", values={"p_p_sesameStreetKeyword":query})

def GetDurationFromDesc(desc):
  duration = ""

  try:
    descArray =  desc.split("(")
    descArrayLen =  len (descArray)
    if descArrayLen<2:
      return ""

    time = descArray[descArrayLen - 1]
    timeArray = time.split(":")

    timeArrayLen = len(timeArray)

    if timeArrayLen<2:
      return ""

    minutes = int(timeArray[0])
    seconds = int(timeArray[1].split(")")[0])
    duration = str(((minutes*60) + seconds)*1000)
    
  except:
    # There was a problem getting the duration (maybe it isn't on the description any more?) so quit with a null
    return ""

  return duration