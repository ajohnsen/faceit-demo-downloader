import urllib2, json, os.path, os, time, datetime, gzip

# Put your faceit auth here
auth = ""
# This is the userid for the user you want to download demos from.
userid = "b2989b4b-7de7-430d-885b-c7e733ac3288"


def changeFileCreationTime(fname, newtime):
    print "Setting file date to: " + str(newtime)
    # Set modified and accesstime
    os.utime(fname, (newtime, newtime))

def downloadDemo(demoUrl, time):
    downloadUrl(demoUrl, time);

def getDemoFilename(file):
    if (file.endswith('.gz')):
        return file.replace('.gz', '');
    return file;

def downloadUrl(url, time):
    file_name = url.split('/')[-1]
    if os.path.isfile(getDemoFilename(file_name)):
        print file_name + " exists, skipping download";
        changeFileCreationTime(getDemoFilename(file_name), time)
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

        if (file_name.endswith('.gz')):
            inF = gzip.open(file_name, 'rb')
            outF = open(file_name.replace('.gz', ''), 'wb')
            outF.write( inF.read() )
            inF.close()
            outF.close()

            # Delete gzip file
            os.remove(file_name)
        changeFileCreationTime(getDemoFilename(file_name), time)



def getMatchInfo(matchId):
    matchUrl = "https://api.faceit.com/api/matches/" + matchId + "?withStats=true"
    opener = urllib2.build_opener();
    opener.addheaders = [('faceit-auth', auth), ('user-id', userid)];
    response = opener.open(matchUrl)
    data = json.loads(response.read())
    dTime = datetime.datetime.strptime(data['payload']['finished_at'], '%a %b %d %H:%M:%S %Z %Y')
    demoUrl = data['payload']['external_matches'][0]['stats']['demo_file_url']
    createdAt =  time.mktime(dTime.timetuple())
    print "Match: " + matchId;
    downloadDemo(demoUrl, createdAt);


def getMatchHistory():
    matchesUrl = "https://api-gateway.faceit.com/stats/api/v1/stats/time/users/" + userid + "/games/csgo?page=0&size=1000"
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
