from ftplib import FTP_TLS
import frappe-bench

ftp = FTP_TLS('xfer.prod.travelport.com')
ftp.login("mprxc6bf", "CLTS239838!")
ftp.cwd('SharedFolder_CLTS') 
# ftp.retrlines('LIST')
# with open('BrandingLite.xml', 'wb') as fp:
    # ftp.retrbinary
file="BrandingLite.xml"
try:
    ftp.retrbinary("RETR " + file ,open("C:\\Flights\\" + file, 'wb').write)
except Exception as e:
    print(e)
    raise
ftp.quit()