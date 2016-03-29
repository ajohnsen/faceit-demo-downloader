import urllib2, json, os.path, pywintypes, win32file, win32con, time, datetime

auth = ""
userid = ""


def changeFileCreationTime(fname, newtime):
    print "Setting creation date: " + str(newtime)
    wintime = pywintypes.Time(newtime)
    winfile = win32file.CreateFile(
        fname, win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None, win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL, None)

    win32file.SetFileTime(winfile, wintime, None, None)

    winfile.close()

def downloadDemo(demoUrl, time):
    downloadUrl(demoUrl, time);

def downloadUrl(url, time):
    file_name = url.split('/')[-1]
    if os.path.isfile(file_name):
        print file_name + " exists, skipping download";
        changeFileCreationTime(file_name, time)
        return;

    try:
        u = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        if e.code == 401:
            print 'not authorized'
        elif e.code == 404:
            print 'Match demo not found'
        elif e.code == 503:
            print 'service unavailable'
        else:
            print 'unknown error: '
    else:
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        f.close()

    changeFileCreationTime(file_name, time)



def getMatchInfo(matchId):
    matchUrl = "https://api.faceit.com/api/matches/" + matchId + "?withStats=true"
    opener = urllib2.build_opener();
    opener.addheaders = [('faceit-auth', auth), ('user-id', userid)];
    response = opener.open(matchUrl)
    data = json.loads(response.read())
    print "######"
    dTime = datetime.datetime.strptime(data['payload']['finished_at'], '%a %b %d %H:%M:%S %Z %Y')

    demoUrl = data['payload']['external_matches'][0]['stats']['demo_file_url']
    print type(data['payload']['finished_at'])
    createdAt =  time.mktime(dTime.timetuple())
    print createdAt
    print "Match: " + matchId;
    downloadDemo(demoUrl, createdAt);


def getMatchHistory():
    matchesUrl = "https://stats.faceit.com/api/v1/stats/time/users/" + userid + "/games/csgo?page=0&size=1000"
    opener = urllib2.build_opener();
    opener.addheaders = [('faceit-auth', auth), ('user-id', userid)];
    response = opener.open(matchesUrl)
    data = json.loads(response.read())

    count = 0;
    for match in data:
        count += 1;
        print str(count) + " " + match['matchId'];
        getMatchInfo(match['matchId']);

getMatchHistory()
#getMatchHistory("https://s3.amazonaws.com/faceit-puppeteer/prod/csgo/d48ea5d4-1776-416d-b498-3b8615d7b94a/d48ea5d4-1776-416d-b498-3b8615d7b94a.dem")
