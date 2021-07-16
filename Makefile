run: clean venv
	. venv/bin/activate && \
	which python && \
	mkdir -p ./export && \
	# download which projects needs to export and its token && \
	python download_redcap_data.py .env/REDCap_Export_Metadata_config.ini 22394 'https://redcap.kumc.edu/api/' && \
	# converted downloaded csv with token into ini && \
	python convert_csv_metadata_into_ini_format.py '.env/redcap_projects_exports.csv'  '.env/redcap_projects_exports.ini' && \
	# download all listed redcap projects && \
	python download_redcap_data.py .env/redcap_projects_exports.ini ALL 'https://redcap.kumc.edu/api/'


venv: venv_clean
	# "creating python virtual env"
	python -m venv venv
	. ./venv/bin/activate && \
	pip install --upgrade pip  && \
	pip install -r requirements.txt  && \
	pip install -r requirements_dev.txt  && \
	pip freeze >  requirements_pip_freeze.txt  && \
	which pip && which python && python --version


venv_clean:
	# "deleting python virtual env"
	rm -rf ./venv


clean: venv_clean	
	rm -rf ./export
	rm -rf ./.env/redcap_projects_exports.csv
	rm -rf ./.env/redcap_projects_exports.ini
