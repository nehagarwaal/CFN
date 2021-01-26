FROM odoo:13
MAINTAINER Vilas Bhumare
USER root
RUN apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get install -y --no-install-recommends git 
RUN  pip3 install boto3 \
	&&	pip3 install stripe \
	&&	pip3 install pandas \
	&&	pip3 install taxjar \
	&&	pip3 install CnpChargebackSdk \
	&&	pip3 install pdfminer \
	&&	pip3 install --upgrade setuptools \
	&&	pip3 install --upgrade pip \
	&&	pip3 install firebase-admin \
	&&	pip3 install VantiveCommerceSDK==9.14.0 -e git://github.com/bkeating/python-payflowpro.git#egg=python_payflowpro 

#COPY odoo.conf /etc/odoo/odoo.conf

WORKDIR /opt

ADD packages /opt/packages/
WORKDIR /opt/packages/googleads-python-lib/
RUN python3.7 setup.py build install
WORKDIR /opt/packages/facebook-python-business-sdk/
RUN python3.7 setup.py install

ADD ejam_addons /opt/ejam_addons/
ADD enterprise_addons /opt/enterprise_addons/
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
