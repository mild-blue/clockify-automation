CONDA_ENV=clockify-automation

conda-create:
	conda env create -f conda.yml --name $(CONDA_ENV)