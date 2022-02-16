import traceback
import requests
import pandas as pd
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options

df=pd.DataFrame(pd.read_excel('test.xlsx'))

addresses=list(df['Homepage-URL'])
cookiesdata=[]
redirectedAddresses=[]
SSLProtection=[]
wordpressAPP=[]
responsiveness=[]
chrome_options = Options()
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('log-level=3')
driver = webdriver.Chrome(options=chrome_options)
#-----------------------------------------------------------------------TEST-----------------------------------------------------------------------------
for i in addresses:
    try:
        driver.get(i)
        sleep(0.5)
        print ("Testing WebPage: ",i)
        print (f"{len(addresses)-addresses.index(i)-1} pages are left.")
        #SSLProtection verification-----------------------------------------------------------
        redirectedAddresses.append(driver.current_url)
        SSLProtection.append(str('https' in str(driver.current_url)).lower())

        #Cookies verification-----------------------------------------------------------------
        rescookie=driver.find_elements_by_xpath("//*[contains(@class, 'ookie')]")
        cookiesdata.append(str(len(rescookie)>1 or ("cookieconsent" in str(driver.page_source).lower()) or ("sessioncookies" in str(driver.page_source).lower()) or ("cookies einverstanden" in str(driver.page_source).lower()) or ("benutzt cookies" in str(driver.page_source).lower()) or ("diese webseite verwendet cookies" in str(driver.page_source).lower()) or ("cookie compliance" in str(driver.page_source).lower()) or ("showcookienotification: true" in str(driver.page_source).lower())).lower())
        
        #Wordpress verification---------------------------------------------------------------
        new_url=driver.current_url
        if (new_url[-1]!='/'):
            new_url+="/"
        iswordpress= "wordpress" in str(requests.get(new_url+"login/", allow_redirects=True).text).lower()
        iswordpress= iswordpress or "wordpress" in str(requests.get(new_url+"wp-login.php", allow_redirects=True).text).lower()
        iswordpress= iswordpress or "wordpress" in str(requests.get(new_url+"wp-login/", allow_redirects=True).text).lower()
        iswordpress= iswordpress or "wordpress" in str(requests.get(new_url+"wp-admin/", allow_redirects=True).text).lower()
        iswordpress= iswordpress or "wordpress" in str(requests.get(new_url+"wp-admin.php", allow_redirects=True).text).lower()
        iswordpress= iswordpress or "wordpress" in str(requests.get(new_url+"license.txt", allow_redirects=True).text).lower()
        iswordpress= iswordpress or "wordpress" in str(requests.get(new_url, allow_redirects=True).text).lower()
        wordpressAPP.append(str(iswordpress).lower())
        
        #Responsive verification--------------------------------------------------------------
        driver.set_window_size(420,600)
        jsScript="""
            if (document.getElementsByTagName('body')[0])
            return document.getElementsByTagName('body')[0].scrollLeft;
        """
        initialscroll=driver.execute_script(jsScript)
        if (initialscroll!=None):
            sleep(0.5)
            jsScript="""
                document.getElementsByTagName('body')[0].scrollLeft+=500;
            """
            driver.execute_script(jsScript)
            sleep(0.5)
            jsScript="""
                return document.getElementsByTagName('body')[0].scrollLeft;
            """
            currrentscroll=driver.execute_script(jsScript)
            first_test=initialscroll == currrentscroll
        else: 
            first_test=True
        jsScript="""
            return document.documentElement.scrollLeft;
        """
        #documentElement
        initialscroll=driver.execute_script(jsScript)
        sleep(0.5)
        jsScript="""
            document.documentElement.scrollLeft+=500;
        """
        driver.execute_script(jsScript)
        sleep(0.5)
        jsScript="""
            return document.documentElement.scrollLeft;
        """
        currrentscroll=driver.execute_script(jsScript)
        responsiveness.append(str((initialscroll == currrentscroll) and first_test).lower())
        driver.set_window_size(1920,1080)
    except:
        x=min(len(cookiesdata),len(responsiveness),len(SSLProtection),len(wordpressAPP))
        cookiesdata=cookiesdata[0:x]
        responsiveness=responsiveness[0:x]
        SSLProtection=SSLProtection[0:x]
        wordpressAPP=wordpressAPP[0:x]
        df.drop(df[(df['Homepage-URL']==i)].index, inplace=True)
        print ("A website didn't load, It will be deleted, continuing...")
driver.quit()
#-----------------------------------------------------------------------UPDATE-----------------------------------------------------------------------------

df['Cookie?']=cookiesdata
df['SSL?']=SSLProtection
df['Wordpress?']=wordpressAPP
df['Responsive?']=responsiveness
#-----------------------------------------------------------------------SORT-----------------------------------------------------------------------------

falses=[]
for row in df.index:
    false=0
    if (df['Cookie?'][row].lower()=='false'):
        false+=1
    if (df['SSL?'][row].lower()=='false'):
        false+=1
    if(df['Responsive?'][row].lower()=='false'):
        false+=1
    if(df['Wordpress?'][row].lower()=='false'):
        false+=1
    falses.append(false)

df.insert(11, "falses?", falses)

df.sort_values(by = ['falses?'],inplace=True, ascending=False)

df.drop('falses?' , inplace=True, axis=1)

#-----------------------------------------------------------------------DELETE-----------------------------------------------------------------------------

indexes=df[ (df['Cookie?'].astype(str).str.lower()=='true') 
           & (df['SSL?'].astype(str).str.lower()=='true') 
           & (df['Responsive?'].astype(str).str.lower()=='true')].index
df.drop(indexes,inplace=True)

df.reset_index(drop=True, inplace=True)

#-----------------------------------------------------------------------COLOR-----------------------------------------------------------------------------

def color(val):
    if str(val).lower()=='false':
        color = 'red'
    elif str(val).lower()=='true':
        color ='green'
    else:
        color ='white' 
    return 'background-color: %s' % color
sf=df.style.applymap(color)

def highlight_cols(s):
    color = 'black'
    return 'background-color: %s' % color

sf=sf.applymap(highlight_cols, subset=pd.IndexSlice[:, ['Unnamed: 6']])

#-----------------------------------------------------------------------SAVE-----------------------------------------------------------------------------
sf.to_excel('output.xlsx')