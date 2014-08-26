Description:
    Take input of a single IP or multiple ip addresses from a file and pass it to telize api to
    determine the details of the IP, like ASN,ISP,LATITUDE,LONGITUDE, etc.
    Once we determine the above information of the IP, we will use amcharts to create
    a bubble/heat map in HTML/SVG format

Requirements:

    1) requests (pip install requests OR sudo easy_install requests)

    2) PhantomJS (if you desire to convert the resulting html to SVG/PNG/PDF)
        for Mac: brew update && brew install phantomjs
        for Windows: https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.7-windows.zip
        for Linux: sudo yum install fontconfig freetype libfreetype.so.6 libfontconfig.so.1 libstdc++.so.6
                and then download: https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.7-linux-x86_64.tar.bz2
                        or 32bit: https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.7-linux-i686.tar.bz2


