#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
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




"""
from optparse import OptionParser
from operator import itemgetter
import os, sys, socket, logging, csv
import requests, json

__author__ = 'Sriram G'
__version__ = '1'
__license__ = 'GPLv3'

"""
Global variables
"""
UA = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"
quiet_mode = False
logger = logging.getLogger('syschkLogger')
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='[%(levelname)-7s] %(asctime)s | %(message)s', datefmt='%I:%M:%S %p') #%m/%d/%Y


def uniq(_1colList):
    """
    Uniquify a list that has a single column
    """
    return  [l for i,l in enumerate(_1colList) if l not in _1colList[i+1:]]

def ip2loc(ip_list=[]):
    """
    accepts a single ip or list of ip's as a list
    and get the extra information of the ip address from telize.com api
    """
    logger.debug("ip2loc().ip2map.py...starts getting ip info for %s ips"%str(len(ip_list)))
    api_url = "http://www.telize.com/geoip/%s"
    headers = {'User-Agent': UA}
    ip2loc_list = []
    for ip in ip_list:
        """ip, country_code, country_code3, country, region_code, region, city,
	    postal_code, continent_code, latitude, longitude, dma_code, area_code, asn, isp, timezone
        """
        response = requests.get(api_url % ip, headers=headers)
        json_data = json.loads(response.text)
        try: country_code2= json.dumps(json_data["country_code"]).replace('"',"").strip()
        except KeyError: country_code2= 'N/A'
        try: country_code3= json.dumps(json_data["country_code3"]).replace('"',"").strip()
        except KeyError: country_code3= 'N/A'
        try: country= json.dumps(json_data["country"]).replace('"',"").strip()
        except KeyError: country= 'N/A'
        try: city= json.dumps(json_data["city"]).replace('"',"").strip()
        except KeyError: city= 'N/A'
        try: region= json.dumps(json_data["region"]).replace('"',"").strip()
        except KeyError: region= 'N/A'
        try: region_code= json.dumps(json_data["region_code"]).replace('"',"").strip()
        except KeyError: region_code= 'N/A'
        try: lat= json.dumps(json_data["latitude"]).replace('"',"").strip()
        except KeyError: lat= 'N/A'
        try: lng= json.dumps(json_data["longitude"]).replace('"',"").strip()
        except KeyError: lng= 'N/A'
        try: zip= json.dumps(json_data["postal_code"]).replace('"',"").strip()
        except KeyError: zip= 'N/A'
        try: isp= json.dumps(json_data["isp"]).replace('"',"").strip()
        except KeyError: isp= 'N/A'
        try: asn= json.dumps(json_data["asn"]).replace('"',"").strip()
        except KeyError: asn= 'N/A'

        t = [ip, lat, lng, country_code2, country_code3, country, region_code, region,city, zip, asn, isp]
        ip2loc_list.append(t)
    logger.debug("ip2loc().ip2map.py...finished")
    """
    returns:
    ipaddress, latitude, longitude, country_code2, country_code3, country, region_code, region, city, postal_code, asn, isp
    """
    return ip2loc_list


def main():
    """
    main function
    """
    all_ips = []
    processed = []
    pCSV = csv.writer(sys.stdout)
    parser = OptionParser()
    mapHeading = ""
    mapSubHeading = ""
    parser = OptionParser(usage="usage: %prog <ip_address|file> [options] ", version="%prog v1")
    parser.add_option("-q","--quiet",action="store_true",dest="quiet_mode",help="execute the program silently",default=False)
    parser.add_option("--heading", dest="mapHeading",help="Heading for the Map", metavar="HEADING",default="HEAT MAP")
    parser.add_option("--sub-heading", dest="mapSubHeading",help="Sub Heading for the Map", metavar="SUB HEADING",default="-- locations this month --")

    (options, args) = parser.parse_args()
    quiet_mode = options.quiet_mode
    mapHeading = options.mapHeading
    mapSubHeading = options.mapSubHeading
    csvHeader = ['ipaddress', 'latitude', 'longitude', 'country_code2', 'country_code3', 'country', 'region_code', 'region', 'city', 'postal_code', 'asn', 'isp']
    processed.append(csvHeader)

    # check to see if we got a IP Address or a File with batch ip's
    if len(args) == 1:
        #1 argument found, check to see if its a IP address
        try:
            socket.inet_aton(args[0])
            all_ips.append(args[0])
        except socket.error:
            # not a ip address, but check to see if its a valid file
            if os.path.isfile(args[0]):
                # Read from File (mostly batch)
                logger.debug("Reading from file...")
                # read the ip addresses
                ips = [line.strip() for line in open(args[0],"rU")]
                logger.debug("Total Ip's read: %s" % str(len(ips)))
                all_ips = uniq(ips)
                logger.debug("Unique Ip's to process: %s" % str(len(all_ips)))
                # Got all the ip's from the file
            else:
                print "%s is not valid..." % args[0]
                parser.print_help()
                sys.exit(0)
    else:
        print "No valid ip address or file provided"
        parser.print_help()
        sys.exit(0)

    logger.info("Gathering information...")
    processed += ip2loc(all_ips)


    """
    print the results in a CSV format
    if it is not required, comment it out
    """
    logger.debug("displaying ip to location results")
    [pCSV.writerow(row) for row in processed]

    """
    pivot some statistics with the collected results to prepare
    for mapping
    """
    logger.debug("pivoting of data begins...")
    # pivot countries
    countries = [row[3] for row in processed[1:]]
    countryStats=[]
    b = {}
    for item in countries:
        b[item] = b.get(item, 0) + 1
    for key, value in b.iteritems():
        temp = [key,value]
        countryStats.append(temp)
    countryStats = sorted(countryStats, key=itemgetter(1),reverse=True)
    countryStats = json.dumps([dict(id=cc, value=v) for cc,v in countryStats])
    areas_heatmap = "areas: " + countryStats

    # pivot latitude's
    lats = [row[1] for row in processed[1:]]
    latsStats=[]
    b = {}
    for item in lats:
        b[item] = b.get(item, 0) + 1
    for key, value in b.iteritems():
        temp = [key,value]
        latsStats.append(temp)
    latsStats =  sorted(latsStats, key=itemgetter(1),reverse=True)

    latlonData = []
    for i in processed[1:]:
        latlonData.append("latlong['%s-%s'] = {'latitude':%s, 'longitude':%s};\n" % (i[3], str(i[6]).replace("/",""), i[1], i[2]))

    mapData = []
    for i in latsStats:
        found = filter(lambda x:x[1]==i[0],processed)
        found = '{"code":"%s-%s" , "name":"%s", "value":%d, "color":"#6c00ff"}' %(found[0][3],str(found[0][6]).replace("/",""),
                                        found[0][5],i[1])
        mapData.append(found)

    logger.debug("amMaps generation")
    """
    AmMaps:: begin
    """
    am_maaps_html = """
        <html>
        <link rel="stylesheet" href="ammap.css" type="text/css">
        <script src="ammap.js" type="text/javascript"></script>

        <script>

        var map;
        var minBulletSize = 10;
        var maxBulletSize = 40;
        var min = Infinity;
        var max = -Infinity;

        var latlong = {};
        %s

        var mapData = [
        %s
        ]

        // get min and max values
        for (var i = 0; i < mapData.length; i++) {
            var value = mapData[i].value;
            if (value < min) {
                min = value;
            }
            if (value > max) {
                max = value;
            }
        }

        // build map
        AmCharts.ready(
                function() {
                    map = new AmCharts.AmMap();

                    map.addTitle("%s", 20);
                    map.addTitle("%s", 10);
                    map.colorSteps =  3;

                    map.areasSettings = {
                        autoZoom: false,
                        unlistedAreasColor: "#DDDDDD",
                        selectable: false,
                        //unlistedAreasAlpha: 0.1,
                        //rollOverOutlineColor: "#FFFFFF",
                        //selectedColor: "#FFFFFF",
                        //rollOverColor: "#FFFFFF",
                        //outlineAlpha: 0.3,
                        //outlineColor: "#FFFFFF",
                        //outlineThickness: 1,
                        color: "#FFDE00",
                        colorSolid: "#CC9933"
                    };

                    map.imagesSettings = {
                        alpha:0.4,
                        outlineColor: "#CECCCC",
                        outlineThickness: 1
                    }

                    map.zoomControl = {
                        panControlEnabled: false,
                        zoomControlEnabled: false
                    }

                    var dataProvider = {
                        mapURL: "worldHigh.svg",
                        images: [],

                        %s
                    }

                    // create circle for each country
                    for (var i = 0; i < mapData.length; i++) {
                        var dataItem = mapData[i];
                        var value = dataItem.value;
                        // calculate size of a bubble
                        var size = (value - min) / (max - min) * (maxBulletSize - minBulletSize) + minBulletSize;
                        if (size < minBulletSize) {
                            size = minBulletSize;
                        }
                        var id = dataItem.code;

                        dataProvider.images.push({
                            type: "circle",
                            width: size,
                            height: size,
                            color: dataItem.color,
                            longitude: latlong[id].longitude,
                            latitude: latlong[id].latitude,
                            //label:dataItem.name,
                            //scale:0.5,
                            //size:8,
                            //labelPosition: "left",
                            //labelShiftX:60, labelShiftY:-12,
                            title: dataItem.name,
                            value: value
                        });
                    }

                    /*map.legend = {
                          width: 150,
                          backgroundAlpha: 0.5,
                          backgroundColor: "#FFFFFF",
                          borderColor: "#666666",
                          borderAlpha: 1,
                          bottom: 15,
                          left: 15,
                          top: 400,
                          horizontalGap: 10,
                          data: [
                          {
                          title: "high",
                          color: "#3366CC"},
                          {
                          title: "moderate",
                          color: "#FFCC33"},
                          {
                          title: "low",
                          color: "#66CC99"}
                          ]
                    };*/

                    map.valueLegend = {
                        right: 10,
                        minValue: "low",
                        maxValue: "high"
                    }

                    map.dataProvider = dataProvider;
                    map.write("mapdiv");

        });

        </script>


        <body>
        <div id="mapdiv" style="width:1200px; height:700px; background-color:#eeeeee;"></div>
        </body>
        </html>
    """
    am_maaps_html = am_maaps_html % (''.join(latlonData), ','.join(mapData), mapHeading, mapSubHeading, areas_heatmap )

    logger.info("Maps html file generated @ map.html")
    f = open('map.html', 'w')
    f.write(am_maaps_html)
    f.close()

    """
    end of main function
    """


if __name__ == '__main__':
    main()
