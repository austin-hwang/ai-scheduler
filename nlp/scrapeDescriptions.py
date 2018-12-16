import urllib2,sys
import pickle
import requests
import re
from BeautifulSoup import BeautifulSoup

class scrapeDescriptions():
    """
    Scrape concentration and club descriptions from Harvard websites
    """
    def get_concentration_info(self):
        """
        Get concentration descriptions from Harvard website
        :return:
        """
        ### Get Concentration Info
        address = 'https://handbook.fas.harvard.edu/book/fields-concentration'
        soup = BeautifulSoup(urllib2.urlopen(address).read())

        # Parses the HTML
        table = soup.find("table")
        attrs = table.findAll("a")
        links = []
        for a in attrs:
            links.append(a.get('href'))

        cnt = 0
        concentrations = []
        descr = []
        for l in links:
            print(l)
            soup = BeautifulSoup(urllib2.urlopen(l).read())

            # Get Concentrations
            header_list = soup.findAll('header')
            for h in header_list:
                if(h.get('id') == 'main-content-header'):
                    header = h
                    break
            concentrations.append(header.getText())

            # Get Concentration descriptions
            div = header.findNext('div')
            paras = ["".join(x.findAll(text=True)) for x in div.findAllNext("p")]
            paras = [x.rstrip() for x in paras]
            paras = "".join(paras)
            descr.append(paras)

            print("Done", cnt)
            cnt += 1

        for i in range(len(concentrations)):
            print(concentrations[i])
            print(descr[i])

        # Saves descriptions found for future use
        pickle.dump(concentrations, open( "concentrations.p", "wb" ))
        pickle.dump(descr, open( "concentration_descr.p", "wb" ))

    def getClubInfo(self):
        """
        Get club descriptions from Harvard student org site
        :return:
        """
        ### Get Club Info
        address = 'https://osl.fas.harvard.edu/student-organizations'
        soup = BeautifulSoup(urllib2.urlopen(address).read())

        # Gets club IDs
        div = soup.findAll('div', {'class' : 'field-item even'})
        iframeSrc = div[1].findAll('iframe')[0]['src']

        r  = requests.get("http:" +iframeSrc)
        data = r.text
        soup = BeautifulSoup(data)
        url_list = soup.findAll("ul")[1].findAll("li")

        ids = []
        for url in url_list:
            attr = url.findAll('a')[0]
            href = attr.get('href')
            matchObj = re.search('(.*)id=(.*)', href)
            ids.append(int(matchObj.group(2)))

        # Gets club info using the IDs found
        orgNames = []
        orgInfo = []
        orgIds = []
        cnt = 0
        address = 'https://fas-mini-sites.fas.harvard.edu/osl/grouplist?rm=details&id=NUMBER'
        for id in ids:
            curr_addr = address.replace('NUMBER', str(id))
            soup = BeautifulSoup(urllib2.urlopen(curr_addr).read())
            test_valid_id = soup.findAll('p')
            print(test_valid_id[0].findAll(text=True))
            # Checks if string is equal length to 'Invalid or missing organization ID.'
            if(len(test_valid_id[0].findAll(text=True)) == 0 or len(test_valid_id[0].findAll(text=True)[0]) == 35):
                continue

            orgIds.append(id)
            name = soup.findAll('h2')[0].text
            orgNames.append(name)
            event_descr = test_valid_id[0].findAll(text=True)[0]
            #event_descr = [x.rstrip() for x in event_descr]
            print(event_descr)
            orgInfo.append(event_descr)
            print("Done", cnt)
            cnt += 1

        for i in range(len(orgInfo)):
            print(orgInfo[i])
            print(orgNames[i])

        # Saves club info
        pickle.dump(orgInfo, open( "org_info.p", "wb" ))
        pickle.dump(orgNames, open( "org_names.p", "wb" ))
        pickle.dump(orgIds, open( "org_ids.p", "wb" ))
